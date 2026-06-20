<template>
  <div class="change-review-page">
    <el-card class="main-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="header-title">{{ title }}</span>
            <el-tag v-if="showTotal" type="info" size="small" effect="plain" round class="ml-2">
              共 {{ total }} 项
            </el-tag>
          </div>
        </div>
      </template>

      <div class="filter-section mb-4" v-if="showFilters">
        <el-form :inline="true" class="filter-form">
          <el-form-item label="变更类型">
            <el-select v-model="filters.requestType" placeholder="全部类型" clearable style="width: 150px">
              <el-option label="全部" value="" />
              <el-option label="项目变更" value="CHANGE" />
            </el-select>
          </el-form-item>
          <el-form-item label="项目名称">
            <el-input
              v-model="filters.search"
              placeholder="搜索项目名称"
              style="width: 200px"
              clearable
              @keyup.enter="handleSearch"
            >
              <template #prefix><el-icon><Search /></el-icon></template>
            </el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="resetFilters">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <el-table v-loading="loading" :data="requests" style="width: 100%" border stripe>
        <el-table-column v-if="showIndex" type="index" label="序号" width="60" align="center" />
        <el-table-column prop="project_no" label="项目编号" width="140" />
        <el-table-column prop="project_title" label="项目名称" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            <div class="font-medium">{{ row.project_title }}</div>
            <div v-if="showProjectNoHint" class="text-xs text-gray-500">
              项目编号: {{ row.project_no || "-" }}
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="request_type_display" label="类型" width="120" align="center">
          <template #default="{ row }">
            <el-tag>{{ row.request_type_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column v-if="showLeader" prop="leader_name" label="负责人" width="120" />
        <el-table-column v-if="showCreatedAt" prop="created_at" label="申请时间" width="160" align="center">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column prop="status_display" label="状态" width="140" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" align="center" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="openReview(row)">
              审核
            </el-button>
            <el-button
              v-if="row.attachment_url"
              link
              type="primary"
              size="small"
              @click="downloadAttachment(row)"
            >
              附件
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container mt-4" v-if="showPagination">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" title="审核意见" width="480px">
      <el-form label-width="90px">
        <el-form-item label="审核意见">
          <el-input v-model="comments" type="textarea" :rows="4" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="danger" :loading="reviewing" @click="submitReview('reject')">
            驳回
          </el-button>
          <el-button type="primary" :loading="reviewing" @click="submitReview('approve')">
            通过
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { ElMessage } from "element-plus";
import { Search } from "@element-plus/icons-vue";
import dayjs from "dayjs";
import {
  downloadChangeRequestAttachment,
  getChangeRequests,
  reviewChangeRequest,
} from "@/api/projects/change-requests";
import { saveBlob } from "@/utils/common";

type ChangeRequestRow = {
  id: number;
  project_no?: string;
  project_title?: string;
  request_type_display?: string;
  leader_name?: string;
  created_at?: string;
  status?: string;
  status_display?: string;
  attachment_url?: string;
  attachment_name?: string;
};

type ChangeRequestListResponse = {
  data?: {
    results?: ChangeRequestRow[];
    count?: number;
    total?: number;
  } | ChangeRequestRow[];
  results?: ChangeRequestRow[];
  count?: number;
  total?: number;
};

const props = withDefaults(
  defineProps<{
    title?: string;
    status: string;
    teacherScope?: boolean;
    showFilters?: boolean;
    showPagination?: boolean;
    showIndex?: boolean;
    showLeader?: boolean;
    showCreatedAt?: boolean;
    showProjectNoHint?: boolean;
    showTotal?: boolean;
  }>(),
  {
    title: "项目异动审核",
    teacherScope: false,
    showFilters: true,
    showPagination: true,
    showIndex: true,
    showLeader: false,
    showCreatedAt: true,
    showProjectNoHint: true,
    showTotal: true,
  }
);

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null;

const getErrorMessage = (error: unknown, fallback: string) => {
  if (!isRecord(error)) return fallback;
  const response = error.response;
  if (isRecord(response) && isRecord(response.data) && typeof response.data.message === "string") {
    return response.data.message;
  }
  if (typeof error.message === "string") return error.message;
  return fallback;
};

const loading = ref(false);
const reviewing = ref(false);
const requests = ref<ChangeRequestRow[]>([]);
const total = ref(0);
const currentPage = ref(1);
const pageSize = ref(10);
const dialogVisible = ref(false);
const currentId = ref<number | null>(null);
const comments = ref("");

const filters = ref({
  requestType: "",
  search: "",
});

const resolveList = (payload: ChangeRequestListResponse | ChangeRequestRow[]) => {
  if (Array.isArray(payload)) {
    return { results: payload, total: payload.length };
  }
  if (payload && "data" in payload && payload.data) {
    const data = payload.data;
    if (Array.isArray(data)) {
      return { results: data, total: data.length };
    }
    return {
      results: data.results ?? [],
      total: data.count ?? data.total ?? data.results?.length ?? 0,
    };
  }
  return {
    results: payload.results ?? [],
    total: payload.count ?? payload.total ?? payload.results?.length ?? 0,
  };
};

const fetchRequests = async () => {
  loading.value = true;
  try {
    const params: Record<string, string | number> = {
      page: currentPage.value,
      page_size: pageSize.value,
      status: props.status,
    };
    if (props.teacherScope) params.teacher_scope = "true";
    if (filters.value.requestType) params.request_type = filters.value.requestType;
    if (filters.value.search) params.search = filters.value.search;

    const res = (await getChangeRequests(params)) as ChangeRequestListResponse | ChangeRequestRow[];
    const normalized = resolveList(res);
    requests.value = normalized.results;
    total.value = normalized.total;
  } catch (error) {
    console.error(error);
    ElMessage.error("获取异动审核列表失败");
  } finally {
    loading.value = false;
  }
};

const handleSearch = () => {
  currentPage.value = 1;
  void fetchRequests();
};

const resetFilters = () => {
  filters.value.requestType = "";
  filters.value.search = "";
  handleSearch();
};

const handleSizeChange = (val: number) => {
  pageSize.value = val;
  currentPage.value = 1;
  void fetchRequests();
};

const handlePageChange = (val: number) => {
  currentPage.value = val;
  void fetchRequests();
};

const openReview = (row: ChangeRequestRow) => {
  currentId.value = row.id;
  comments.value = "";
  dialogVisible.value = true;
};

const submitReview = async (action: "approve" | "reject") => {
  if (!currentId.value) return;
  reviewing.value = true;
  try {
    await reviewChangeRequest(currentId.value, { action, comments: comments.value });
    ElMessage.success("审核完成");
    dialogVisible.value = false;
    void fetchRequests();
  } catch (error) {
    ElMessage.error(getErrorMessage(error, "操作失败"));
  } finally {
    reviewing.value = false;
  }
};

const downloadAttachment = async (row: ChangeRequestRow) => {
  if (!row.id) return;
  try {
    const blob = (await downloadChangeRequestAttachment(row.id)) as Blob;
    saveBlob(blob, row.attachment_name || "异动附件");
  } catch {
    ElMessage.error("下载异动附件失败");
  }
};

const formatDate = (value?: string) => {
  if (!value) return "-";
  return dayjs(value).format("YYYY-MM-DD HH:mm");
};

const getStatusType = (status?: string) => {
  if (status?.includes("REJECT")) return "danger";
  if (status?.includes("APPROV")) return "success";
  return "warning";
};

onMounted(fetchRequests);
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.change-review-page {
  padding: 20px;
}

.main-card {
  border-radius: 8px;

  :deep(.el-card__header) {
    padding: 16px 20px;
    border-bottom: 1px solid $color-border-light;
    font-weight: 600;
  }
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-title {
  color: $slate-800;
  font-size: 16px;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.ml-2 {
  margin-left: 8px;
}

.mb-4 {
  margin-bottom: 16px;
}

.mt-4 {
  margin-top: 16px;
}
</style>
