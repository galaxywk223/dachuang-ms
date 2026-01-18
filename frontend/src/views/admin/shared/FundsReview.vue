<template>
  <div class="funds-review-page">
    <el-card class="main-card" shadow="never" v-loading="loading">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="header-title">经费审核</span>
          </div>
          <div class="header-actions">
            <el-button type="primary" plain @click="fetchData">刷新</el-button>
          </div>
        </div>
      </template>

      <el-table :data="tableData" stripe border>
        <el-table-column prop="project_no" label="项目编号" width="140" />
        <el-table-column prop="project_title" label="项目名称" min-width="180" />
        <el-table-column prop="title" label="支出事项" min-width="160" />
        <el-table-column
          prop="amount"
          label="金额 (元)"
          width="120"
          align="right"
        >
          <template #default="scope">
            {{ Number(scope.row.amount).toFixed(2) }}
          </template>
        </el-table-column>
        <el-table-column prop="proof_file_url" label="凭证" width="90" align="center">
          <template #default="scope">
            <el-link
              v-if="scope.row.proof_file_url"
              type="primary"
              :href="resolveFileUrl(scope.row.proof_file_url)"
              target="_blank"
              :underline="false"
            >
              查看
            </el-link>
            <span v-else class="text-gray-400">无</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_by_name" label="录入人" width="120" />
        <el-table-column label="状态" width="140" align="center">
          <template #default="scope">
            <el-tag :type="getReviewStatusType(scope.row)">
              {{ getReviewStatusLabel(scope.row) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" align="center" fixed="right">
          <template #default="scope">
            <el-button
              link
              type="success"
              size="small"
              @click="handleReview(scope.row, true)"
              >通过</el-button
            >
            <el-button
              link
              type="danger"
              size="small"
              @click="handleReview(scope.row, false)"
              >驳回</el-button
            >
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container" v-if="pagination.total > pagination.pageSize">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          background
          size="small"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import request from "@/utils/request";
import { CONFIG } from "@/config";

defineOptions({
  name: "FundsReviewView",
});

type ExpenditureItem = {
  id: number;
  project_no?: string;
  project_title?: string;
  title?: string;
  amount?: number | string;
  proof_file_url?: string;
  created_by_name?: string;
  status?: string;
  status_display?: string;
  leader_review_status?: string;
  current_node_name?: string;
};

type ApiResponse = {
  code?: number;
  message?: string;
  data?: unknown;
};

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null;

const normalizeList = <T>(payload: unknown): T[] => {
  if (Array.isArray(payload)) return payload as T[];
  if (isRecord(payload) && Array.isArray(payload.results)) {
    return payload.results as T[];
  }
  if (
    isRecord(payload) &&
    isRecord(payload.data) &&
    Array.isArray(payload.data.results)
  ) {
    return payload.data.results as T[];
  }
  if (isRecord(payload) && Array.isArray(payload.data)) {
    return payload.data as T[];
  }
  return [];
};

const resolveCount = (payload: unknown, fallback: number) => {
  if (!isRecord(payload)) return fallback;
  if (typeof payload.count === "number") return payload.count;
  if (isRecord(payload.data) && typeof payload.data.count === "number") {
    return payload.data.count;
  }
  return fallback;
};

const tableData = ref<ExpenditureItem[]>([]);
const loading = ref(false);

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0,
});

const fetchData = async () => {
  loading.value = true;
  try {
    const res = (await request.get("/projects/expenditures/", {
      params: {
        review_scope: "self",
        page: pagination.page,
        page_size: pagination.pageSize,
      },
    })) as ApiResponse | unknown;

    const payload = isRecord(res) && "data" in res ? res.data : res;
    const list = normalizeList<ExpenditureItem>(payload);
    tableData.value = list;
    pagination.total = resolveCount(payload, list.length);
  } catch (error) {
    console.error(error);
    ElMessage.error("加载列表失败");
  } finally {
    loading.value = false;
  }
};

const handleSizeChange = (size: number) => {
  pagination.pageSize = size;
  fetchData();
};

const handleCurrentChange = (page: number) => {
  pagination.page = page;
  fetchData();
};

const handleReview = async (row: ExpenditureItem, approved: boolean) => {
  try {
    await ElMessageBox.confirm(
      approved ? "确认通过该经费申请吗？" : "确认驳回该经费申请吗？",
      "提示",
      { type: approved ? "success" : "warning" }
    );
    await request.post(`/projects/expenditures/${row.id}/review/`, {
      action: approved ? "approve" : "reject",
    });
    ElMessage.success("审核已提交");
    fetchData();
  } catch {
    // cancel
  }
};

const getReviewStatusLabel = (row: ExpenditureItem) => {
  if (row.status === "APPROVED" || row.status === "REJECTED") {
    return row.status_display || "已审核";
  }
  if (row.leader_review_status === "PENDING") {
    return "待负责人审核";
  }
  if (row.current_node_name) {
    return row.current_node_name;
  }
  return row.status_display || "待审核";
};

const getReviewStatusType = (row: ExpenditureItem) => {
  if (row.status === "APPROVED") return "success";
  if (row.status === "REJECTED") return "danger";
  if (row.leader_review_status === "PENDING") return "warning";
  if (row.current_node_name) return "warning";
  return "info";
};

const resolveFileUrl = (url?: string) => {
  if (!url) return "";
  if (/^https?:\/\//i.test(url)) return url;
  return `${CONFIG.api.BASE_URL}${url}`;
};

onMounted(() => {
  fetchData();
});
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.funds-review-page {
  padding: 20px;
}

.main-card {
  border-radius: 8px;
  :deep(.el-card__header) {
    padding: 16px 20px;
    font-weight: 600;
    border-bottom: 1px solid $color-border-light;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  font-size: 16px;
  color: $slate-800;
}

.pagination-container {
  padding-top: 24px;
  display: flex;
  justify-content: flex-end;
}
</style>
