<template>
  <div class="notifications-page">
    <el-card class="main-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="header-title">消息中心</span>
          </div>
          <div class="header-actions" v-if="activeTab === 'personal'">
            <el-button type="primary" plain @click="markAllRead">
              全部已读
            </el-button>
          </div>
        </div>
      </template>

      <el-tabs v-model="activeTab" class="message-tabs" @tab-change="handleTabChange">
        <el-tab-pane label="个人通知" name="personal">
          <div class="filter-row">
            <el-select
              v-model="filterType"
              placeholder="通知类型"
              clearable
              style="width: 200px"
              @change="fetchNotifications"
            >
              <el-option label="系统通知" value="SYSTEM" />
              <el-option label="项目通知" value="PROJECT" />
              <el-option label="审核通知" value="REVIEW" />
            </el-select>
            <el-select
              v-model="filterRead"
              placeholder="读取状态"
              clearable
              style="width: 200px"
              @change="fetchNotifications"
            >
              <el-option label="未读" value="false" />
              <el-option label="已读" value="true" />
            </el-select>
          </div>

          <el-table :data="notifications" v-loading="notificationLoading" stripe border>
            <el-table-column prop="title" label="标题" min-width="200" />
            <el-table-column
              prop="notification_type_display"
              label="类型"
              width="120"
            />
            <el-table-column prop="created_at" label="时间" width="180">
              <template #default="{ row }">
                {{ formatDateTime(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="状态" width="120">
              <template #default="{ row }">
                <el-tag :type="row.is_read ? 'info' : 'warning'">
                  {{ row.is_read ? "已读" : "未读" }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="140" align="center" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="openDetail(row)">
                  查看
                </el-button>
                <el-button
                  link
                  type="success"
                  v-if="!row.is_read"
                  @click="markRead(row)"
                >
                  标记已读
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="pagination-container">
            <el-pagination
              v-model:current-page="notificationPagination.page"
              v-model:page-size="notificationPagination.pageSize"
              :total="notificationPagination.total"
              :page-sizes="[10, 20, 50]"
              layout="total, sizes, prev, pager, next, jumper"
              @size-change="handleNotificationSizeChange"
              @current-change="handleNotificationPageChange"
            />
          </div>
        </el-tab-pane>

        <el-tab-pane label="平台公告" name="notices">
          <EmptyState
            v-if="!noticeLoading && notices.length === 0"
            title="暂无公告"
            description="当前没有已发布的平台公告。"
          />
          <div v-else v-loading="noticeLoading" class="notice-list">
            <article v-for="notice in notices" :key="notice.id" class="notice-item">
              <div class="notice-title">
                <span>{{ notice.title }}</span>
                <el-tag v-if="notice.is_pinned" type="warning" size="small">
                  置顶
                </el-tag>
              </div>
              <p>{{ notice.content }}</p>
              <time>{{ formatDateTime(notice.published_at || notice.created_at) }}</time>
            </article>
          </div>
        </el-tab-pane>

        <el-tab-pane label="资料下载" name="materials">
          <el-table :data="materials" v-loading="materialLoading" stripe>
            <el-table-column prop="title" label="资料名称" min-width="220" />
            <el-table-column prop="category" label="分类" width="140" />
            <el-table-column
              prop="description"
              label="说明"
              min-width="260"
              show-overflow-tooltip
            />
            <el-table-column label="下载次数" width="110">
              <template #default="{ row }">
                {{ typeof row.download_count === "number" ? row.download_count : "-" }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" align="center">
              <template #default="{ row }">
                <el-button type="primary" link @click="downloadMaterial(row)">
                  下载
                </el-button>
              </template>
            </el-table-column>
          </el-table>
          <EmptyState
            v-if="!materialLoading && materials.length === 0"
            title="暂无资料"
            description="当前没有开放下载的资料。"
          />
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <el-dialog v-model="detailVisible" title="通知详情" width="520px">
      <div class="detail-content">
        <h4>{{ current?.title }}</h4>
        <p class="detail-time">{{ formatDateTime(current?.created_at) }}</p>
        <div class="detail-text">{{ current?.content }}</div>
      </div>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import dayjs from "dayjs";
import EmptyState from "@/components/common/EmptyState.vue";
import {
  getNotifications,
  getPlatformMaterials,
  getPlatformNotices,
  markAllNotificationsRead,
  markNotificationRead,
  downloadPlatformMaterial,
  recordMaterialDownload,
} from "@/api/notifications";
import { saveBlob } from "@/utils/common";

defineOptions({
  name: "NotificationsView",
});

type MessageTab = "personal" | "notices" | "materials";

type NotificationItem = {
  id: number;
  title: string;
  content: string;
  notification_type_display?: string;
  created_at?: string;
  is_read?: boolean;
};

type NoticeItem = {
  id: number;
  title: string;
  content: string;
  is_pinned?: boolean;
  published_at?: string;
  created_at?: string;
};

type MaterialItem = {
  id: number | string;
  title: string;
  category?: string;
  description?: string;
  file_url?: string;
  file_name?: string;
  external_url?: string;
  download_count?: number;
  source?: string;
};

type NotificationQuery = {
  page: number;
  page_size: number;
  notification_type?: string;
  is_read?: string;
};

type ListPayload<T> = {
  results?: T[];
  count?: number;
};

const route = useRoute();
const router = useRouter();

const activeTab = ref<MessageTab>("personal");
const notificationLoading = ref(false);
const noticeLoading = ref(false);
const materialLoading = ref(false);
const notifications = ref<NotificationItem[]>([]);
const notices = ref<NoticeItem[]>([]);
const materials = ref<MaterialItem[]>([]);
const filterType = ref<string | undefined>();
const filterRead = ref<string | undefined>();
const detailVisible = ref(false);
const current = ref<NotificationItem | null>(null);

const notificationPagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0,
});

const validTabs: MessageTab[] = ["personal", "notices", "materials"];

const resolveTab = (value: unknown): MessageTab => {
  const tab = Array.isArray(value) ? value[0] : value;
  return validTabs.includes(tab as MessageTab) ? (tab as MessageTab) : "personal";
};

const formatDateTime = (date?: string) => {
  if (!date) return "-";
  return dayjs(date).format("YYYY-MM-DD HH:mm");
};

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null;

const normalizeListPayload = <T,>(payload: unknown): ListPayload<T> => {
  if (!isRecord(payload)) {
    return {};
  }
  const results = Array.isArray(payload.results) ? (payload.results as T[]) : undefined;
  const count = typeof payload.count === "number" ? payload.count : undefined;
  return { results, count };
};

const normalizeResponse = <T,>(response: unknown): { results: T[]; count: number } => {
  const rootPayload = normalizeListPayload<T>(response);
  const dataPayload = isRecord(response) ? normalizeListPayload<T>(response.data) : {};
  const results = dataPayload.results || rootPayload.results || [];
  const count = dataPayload.count ?? rootPayload.count ?? results.length;
  return { results, count };
};

const loadActiveTab = () => {
  if (activeTab.value === "personal") return fetchNotifications();
  if (activeTab.value === "notices") return fetchNotices();
  return fetchMaterials();
};

const fetchNotifications = async () => {
  notificationLoading.value = true;
  try {
    const params: NotificationQuery = {
      page: notificationPagination.page,
      page_size: notificationPagination.pageSize,
    };
    if (filterType.value) params.notification_type = filterType.value;
    if (filterRead.value) params.is_read = filterRead.value;
    const res = await getNotifications(params);
    const normalized = normalizeResponse<NotificationItem>(res);
    notifications.value = normalized.results;
    notificationPagination.total = normalized.count;
  } catch {
    ElMessage.error("获取通知失败");
  } finally {
    notificationLoading.value = false;
  }
};

const fetchNotices = async () => {
  noticeLoading.value = true;
  try {
    const res = await getPlatformNotices({ status: "PUBLISHED" });
    notices.value = normalizeResponse<NoticeItem>(res).results;
  } catch {
    ElMessage.error("获取公告失败");
  } finally {
    noticeLoading.value = false;
  }
};

const fetchMaterials = async () => {
  materialLoading.value = true;
  try {
    const res = await getPlatformMaterials({ is_active: true });
    materials.value = normalizeResponse<MaterialItem>(res).results;
  } catch {
    ElMessage.error("获取资料失败");
  } finally {
    materialLoading.value = false;
  }
};

const handleTabChange = (tabName: string | number) => {
  const tab = resolveTab(String(tabName));
  void router.replace({
    query: {
      ...route.query,
      tab,
    },
  });
  void loadActiveTab();
};

const openDetail = (row: NotificationItem) => {
  current.value = row;
  detailVisible.value = true;
};

const markRead = async (row: NotificationItem) => {
  await markNotificationRead(row.id);
  row.is_read = true;
  ElMessage.success("已标记为已读");
};

const markAllRead = async () => {
  await markAllNotificationsRead();
  notifications.value = notifications.value.map((item) => ({
    ...item,
    is_read: true,
  }));
  ElMessage.success("已全部标记为已读");
};

const downloadMaterial = async (row: MaterialItem) => {
  if (row.file_url) {
    const blob = (await downloadPlatformMaterial(row.id)) as Blob;
    saveBlob(blob, row.file_name || row.title || "资料文件");
    await fetchMaterials();
    return;
  }
  if (row.external_url) {
    await recordMaterialDownload(row.id);
    window.open(row.external_url, "_blank", "noopener,noreferrer");
    await fetchMaterials();
    return;
  }
  if (!row.file_url && !row.external_url) {
    ElMessage.warning("该资料暂无文件");
  }
};

const handleNotificationSizeChange = () => {
  notificationPagination.page = 1;
  void fetchNotifications();
};

const handleNotificationPageChange = () => {
  void fetchNotifications();
};

watch(
  () => route.query.tab,
  (tab) => {
    const nextTab = resolveTab(tab);
    if (activeTab.value !== nextTab) {
      activeTab.value = nextTab;
      void loadActiveTab();
    }
  }
);

onMounted(() => {
  activeTab.value = resolveTab(route.query.tab);
  void loadActiveTab();
});
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.notifications-page {
  padding: 20px;
}

.main-card {
  border-radius: 8px;

  :deep(.el-card__header) {
    padding: 16px 20px;
    font-weight: 600;
    border-bottom: 1px solid $slate-200;
  }
}

.card-header,
.header-left,
.header-actions {
  display: flex;
  align-items: center;
}

.card-header {
  justify-content: space-between;
}

.header-title {
  color: $slate-900;
  font-size: 16px;
  font-weight: 700;
}

.message-tabs {
  :deep(.el-tabs__content) {
    padding-top: 10px;
  }
}

.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.detail-content {
  h4 {
    margin-bottom: 4px;
    color: $slate-900;
    font-size: 16px;
  }

  .detail-time {
    margin-bottom: 12px;
    color: $slate-500;
    font-size: 12px;
  }

  .detail-text {
    color: $slate-700;
    line-height: 1.6;
    white-space: pre-line;
  }
}

.notice-list {
  display: grid;
  gap: 14px;
}

.notice-item {
  padding: 18px;
  border: 1px solid $slate-200;
  border-radius: $radius-xl;
  background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);

  p {
    margin: 10px 0;
    color: $slate-600;
    line-height: 1.7;
  }

  time {
    color: $slate-400;
    font-size: 13px;
  }
}

.notice-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  color: $slate-900;
  font-weight: 800;
}
</style>
