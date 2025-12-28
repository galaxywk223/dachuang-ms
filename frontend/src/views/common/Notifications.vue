<template>
  <div class="notifications-page">
    <el-card class="main-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="header-title">通知中心</span>
          </div>
          <div class="header-actions">
            <el-button type="primary" plain @click="markAllRead">全部已读</el-button>
          </div>
        </div>
      </template>

      <div class="filter-row">
        <el-select v-model="filterType" placeholder="通知类型" clearable style="width: 200px" @change="fetchNotifications">
          <el-option label="系统通知" value="SYSTEM" />
          <el-option label="项目通知" value="PROJECT" />
          <el-option label="审核通知" value="REVIEW" />
        </el-select>
        <el-select v-model="filterRead" placeholder="读取状态" clearable style="width: 200px" @change="fetchNotifications">
          <el-option label="未读" value="false" />
          <el-option label="已读" value="true" />
        </el-select>
      </div>

      <el-table :data="notifications" v-loading="loading" stripe border>
        <el-table-column prop="title" label="标题" min-width="200" />
        <el-table-column prop="notification_type_display" label="类型" width="120" />
        <el-table-column prop="created_at" label="时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.is_read ? 'info' : 'warning'">
              {{ row.is_read ? '已读' : '未读' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" align="center" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="openDetail(row)">查看</el-button>
            <el-button link type="success" v-if="!row.is_read" @click="markRead(row)">标记已读</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :total="pagination.total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <el-dialog v-model="detailVisible" title="通知详情" width="520px">
      <div class="detail-content">
        <h4>{{ current?.title }}</h4>
        <p class="detail-time">{{ formatDate(current?.created_at) }}</p>
        <div class="detail-text">{{ current?.content }}</div>
      </div>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import dayjs from "dayjs";
import {
  getNotifications,
  markNotificationRead,
  markAllNotificationsRead,
} from "@/api/notifications";

defineOptions({
  name: "NotificationsView",
});

type NotificationItem = {
  id: number;
  title: string;
  content: string;
  notification_type_display?: string;
  created_at?: string;
  is_read?: boolean;
};

type NotificationQuery = {
  page: number;
  page_size: number;
  notification_type?: string;
  is_read?: string;
};

type NotificationListPayload = {
  results?: NotificationItem[];
  count?: number;
};

const loading = ref(false);
const notifications = ref<NotificationItem[]>([]);
const filterType = ref<string | undefined>();
const filterRead = ref<string | undefined>();
const detailVisible = ref(false);
const current = ref<NotificationItem | null>(null);

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0,
});

const formatDate = (date?: string) => {
  if (!date) return "-";
  return dayjs(date).format("YYYY-MM-DD HH:mm");
};

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null;

const normalizeListPayload = (payload: unknown): NotificationListPayload => {
  if (!isRecord(payload)) {
    return {};
  }
  const results = Array.isArray(payload.results)
    ? (payload.results as NotificationItem[])
    : undefined;
  const count =
    typeof payload.count === "number" ? payload.count : undefined;
  return { results, count };
};

const normalizeResponse = (
  response: unknown
): { results: NotificationItem[]; count: number } => {
  const rootPayload = normalizeListPayload(response);
  const dataPayload = isRecord(response)
    ? normalizeListPayload(response.data)
    : {};

  const results =
    dataPayload.results || rootPayload.results || [];
  const count =
    dataPayload.count ?? rootPayload.count ?? results.length;

  return { results, count };
};

const fetchNotifications = async () => {
  loading.value = true;
  try {
    const params: NotificationQuery = {
      page: pagination.page,
      page_size: pagination.pageSize,
    };
    if (filterType.value) params.notification_type = filterType.value;
    if (filterRead.value) params.is_read = filterRead.value;
    const res = await getNotifications(params);
    const normalized = normalizeResponse(res);
    notifications.value = normalized.results;
    pagination.total = normalized.count;
  } catch {
    ElMessage.error("获取通知失败");
  } finally {
    loading.value = false;
  }
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
  notifications.value = notifications.value.map((item) => ({ ...item, is_read: true }));
  ElMessage.success("已全部标记为已读");
};

const handleSizeChange = () => fetchNotifications();
const handlePageChange = () => fetchNotifications();

onMounted(fetchNotifications);
</script>

<style scoped lang="scss">
.notifications-page {
  .filter-row {
    display: flex;
    gap: 12px;
    margin-bottom: 16px;
  }
  .detail-content {
    h4 {
      margin-bottom: 4px;
    }
    .detail-time {
      font-size: 12px;
      color: #64748b;
      margin-bottom: 12px;
    }
    .detail-text {
      white-space: pre-line;
      line-height: 1.6;
    }
  }
}
</style>
