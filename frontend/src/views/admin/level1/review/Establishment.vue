<template>
  <div class="review-page">
    <el-card class="main-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="header-title">校级立项审核</span>
            <el-tag type="info" size="small" effect="plain" round class="ml-2"
              >共 {{ total }} 项</el-tag
            >
          </div>
          <div class="header-actions"></div>
        </div>
      </template>

      <div class="filter-section mb-4">
        <el-form :inline="true" class="filter-form">
          <el-form-item label="项目名称">
            <el-input
              v-model="searchQuery"
              placeholder="请输入项目名称"
              style="width: 240px"
              clearable
              :prefix-icon="Search"
              @clear="handleSearch"
              @keyup.enter="handleSearch"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <div class="action-bar mb-4">
        <el-button type="danger" plain @click="openBatchDialog"
          >批量驳回</el-button
        >
      </div>

      <el-table
        v-loading="loading"
        :data="projects"
        style="width: 100%"
        border
        stripe
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" align="center" />
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column
          prop="title"
          label="项目名称"
          min-width="200"
          show-overflow-tooltip
        >
          <template #default="{ row }">
            <span class="project-title">{{ row.title }}</span>
          </template>
        </el-table-column>
        <el-table-column
          prop="level_display"
          label="项目级别"
          width="100"
          align="center"
        >
          <template #default="{ row }">
            <el-tag size="small" effect="plain">{{ row.level_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column
          prop="category_display"
          label="项目类别"
          width="120"
          align="center"
        >
          <template #default="{ row }">
            <el-tag effect="light" size="small" type="info">{{
              row.category_display
            }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="负责人" width="100" align="center">
          <template #default="{ row }">
            {{ row.leader_name || "-" }}
          </template>
        </el-table-column>
        <el-table-column
          prop="college"
          label="学院"
          width="140"
          show-overflow-tooltip
          align="center"
        />
        <el-table-column
          prop="budget"
          label="申报经费"
          width="100"
          align="center"
        >
          <template #default="{ row }">
            {{ row.budget }}
          </template>
        </el-table-column>
        <el-table-column
          prop="approved_budget"
          label="批准经费"
          width="100"
          align="center"
        >
          <template #default="{ row }">
            {{ row.approved_budget ?? "-" }}
          </template>
        </el-table-column>
        <el-table-column label="审核节点" width="120" align="center">
          <template #default="{ row }">
            <ProjectStatusBadge
              :status="row.status"
              :label="row.status_display"
            />
          </template>
        </el-table-column>

        <el-table-column label="操作" width="180" align="center" fixed="right">
          <template #default="{ row }">
            <div class="operation-actions">
              <el-button
                type="primary"
                link
                size="small"
                @click="handleViewDetail(row)"
              >
                详情
              </el-button>
              <el-dropdown
                trigger="click"
                @command="(cmd: string) => handleCommand(cmd, row)"
              >
                <el-button type="primary" link size="small">
                  审核<el-icon class="el-icon--right"><arrow-down /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="approve">
                      <span
                        style="
                          display: flex;
                          align-items: center;
                          gap: 6px;
                          color: #67c23a;
                        "
                      >
                        <el-icon><Check /></el-icon>通过申请
                      </span>
                    </el-dropdown-item>
                    <el-dropdown-item command="reject" divided>
                      <span
                        style="
                          display: flex;
                          align-items: center;
                          gap: 6px;
                          color: #f56c6c;
                        "
                      >
                        <el-icon><Close /></el-icon>驳回申请
                      </span>
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container mt-4">
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

    <el-dialog
      v-model="reviewDialogVisible"
      :title="reviewType === 'approve' ? '审核通过' : '驳回申请'"
      width="520px"
      align-center
      destroy-on-close
    >
      <el-form :model="reviewForm" label-position="top">
        <el-form-item v-if="reviewType === 'approve'" label="批准经费" required>
          <el-input-number
            v-model="reviewForm.approved_budget"
            :min="0"
            :precision="2"
            class="w-full"
            controls-position="right"
          />
        </el-form-item>
        <el-form-item
          label="退回至"
          v-if="reviewType === 'reject' && rejectTargets.length > 0"
        >
          <el-select
            v-model="reviewForm.target_node_id"
            placeholder="请选择退回节点"
            style="width: 100%"
          >
            <el-option
              v-for="node in rejectTargets"
              :key="node.id"
              :label="node.name"
              :value="node.id"
            >
              <span>{{ node.name }}</span>
              <span
                style="
                  float: right;
                  color: var(--el-text-color-secondary);
                  font-size: 12px;
                "
              >
                {{ node.role }}
              </span>
            </el-option>
          </el-select>
          <div
            style="
              color: var(--el-text-color-secondary);
              font-size: 12px;
              margin-top: 4px;
            "
          >
            未选择时将退回到默认节点
          </div>
        </el-form-item>
        <el-form-item
          :label="
            reviewType === 'approve' ? '审核意见 (可选)' : '驳回原因 (必填)'
          "
        >
          <el-input
            v-model="reviewForm.comment"
            type="textarea"
            :rows="4"
            :placeholder="
              reviewType === 'approve' ? '请输入...' : '请输入驳回的具体原因...'
            "
            resize="none"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="reviewDialogVisible = false">取消</el-button>
          <el-button
            :type="reviewType === 'approve' ? 'primary' : 'danger'"
            @click="confirmReview"
          >
            确认提交
          </el-button>
        </span>
      </template>
    </el-dialog>

    <el-dialog v-model="batchDialogVisible" title="批量驳回" width="520px">
      <el-form label-position="top">
        <el-form-item label="驳回原因（必填）">
          <el-input
            v-model="batchForm.comments"
            type="textarea"
            :rows="4"
            placeholder="请输入驳回原因"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="batchDialogVisible = false">取消</el-button>
          <el-button
            type="danger"
            :loading="batchSubmitting"
            @click="submitBatchReject"
          >
            提交驳回
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { Search, Check, Close, ArrowDown } from "@element-plus/icons-vue";
import {
  getReviewProjects,
  approveProject,
  rejectProject,
} from "@/api/projects/admin";
import ProjectStatusBadge from "@/components/business/project/StatusBadge.vue";
import request from "@/utils/request";
import { getRejectTargetsByProject, type WorkflowNode } from "@/api/reviews";

defineOptions({ name: "Level1EstablishmentReviewView" });

type ProjectRow = {
  id: number;
  review_id?: number;
  title?: string;
  level_display?: string;
  category_display?: string;
  is_key_field?: boolean;
  key_domain_code?: string;
  leader_name?: string;
  leader_student_id?: string;
  college?: string;
  leader_contact?: string;
  leader_email?: string;
  budget?: number;
  approved_budget?: number | null;
  status?: string;
  status_display?: string;
};

type ReviewProjectsResponse = {
  code?: number;
  data?: {
    results?: ProjectRow[];
    total?: number;
  };
};

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null;

const getErrorMessage = (error: unknown, fallback: string) => {
  if (!isRecord(error)) return fallback;
  const response = error.response;
  if (
    isRecord(response) &&
    isRecord(response.data) &&
    typeof response.data.message === "string"
  ) {
    return response.data.message;
  }
  if (typeof error.message === "string") return error.message;
  return fallback;
};

const loading = ref(false);
const projects = ref<ProjectRow[]>([]);
const searchQuery = ref("");
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);
const selectedRows = ref<ProjectRow[]>([]);

const reviewDialogVisible = ref(false);
const reviewType = ref<"approve" | "reject">("approve");
const reviewForm = ref({
  projectId: 0,
  comment: "",
  approved_budget: null as number | null,
  target_node_id: null as number | null,
});
const rejectTargets = ref<WorkflowNode[]>([]);

const batchDialogVisible = ref(false);
const batchSubmitting = ref(false);
const batchForm = ref({
  comments: "",
});

const fetchProjects = async () => {
  loading.value = true;
  try {
    const response = (await getReviewProjects({
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchQuery.value,
      type: "establishment",
    })) as ReviewProjectsResponse;

    if (response.code === 200 && response.data) {
      projects.value = response.data.results ?? [];
      total.value = response.data.total ?? 0;
      selectedRows.value = [];
    }
  } catch {
    ElMessage.error("获取项目列表失败");
  } finally {
    loading.value = false;
  }
};

const handleSearch = () => {
  currentPage.value = 1;
  fetchProjects();
};

const handleReset = () => {
  searchQuery.value = "";
  handleSearch();
};

const handlePageChange = () => {
  fetchProjects();
};

const handleSizeChange = () => {
  currentPage.value = 1;
  fetchProjects();
};

const handleSelectionChange = (val: ProjectRow[]) => {
  selectedRows.value = val;
};

const handleViewDetail = (row: ProjectRow) => {
  ElMessage.info(`查看详情：${row.title || "项目"}`);
};

const handleCommand = (command: string, row: ProjectRow) => {
  if (command === "approve") handleApprove(row);
  if (command === "reject") handleReject(row);
};

const handleApprove = (row: ProjectRow) => {
  reviewType.value = "approve";
  reviewForm.value.projectId = row.id;
  reviewForm.value.comment = "";
  reviewForm.value.approved_budget =
    row.approved_budget ?? (row.budget ? Number(row.budget) : null);
  reviewDialogVisible.value = true;
};

const handleReject = async (row: ProjectRow) => {
  reviewType.value = "reject";
  reviewForm.value.projectId = row.id;
  reviewForm.value.comment = "";
  reviewForm.value.approved_budget = null;
  reviewForm.value.target_node_id = null;
  rejectTargets.value = [];
  // 加载可退回节点
  try {
    const res = await getRejectTargetsByProject(row.id);
    if (res.code === 200) {
      rejectTargets.value = res.data || [];
    }
  } catch (error) {
    console.error("获取退回节点失败", error);
    rejectTargets.value = [];
  }
  reviewDialogVisible.value = true;
};

const confirmReview = async () => {
  if (reviewType.value === "reject" && !reviewForm.value.comment) {
    ElMessage.warning("请输入驳回原因");
    return;
  }
  if (
    reviewType.value === "approve" &&
    reviewForm.value.approved_budget === null
  ) {
    ElMessage.warning("请填写批准经费");
    return;
  }

  try {
    const data: {
      comment: string;
      approved_budget?: number | null;
      target_node_id?: number | null;
    } = {
      comment: reviewForm.value.comment,
    };
    let response: ReviewProjectsResponse;
    if (reviewType.value === "approve") {
      data.approved_budget = reviewForm.value.approved_budget;
      response = (await approveProject(
        reviewForm.value.projectId,
        data
      )) as ReviewProjectsResponse;
    } else {
      // 如果是退回且选择了目标节点
      if (reviewForm.value.target_node_id) {
        data.target_node_id = reviewForm.value.target_node_id;
      }
      response = (await rejectProject(
        reviewForm.value.projectId,
        data
      )) as ReviewProjectsResponse;
    }

    if (response.code === 200) {
      ElMessage.success(reviewType.value === "approve" ? "已通过" : "已驳回");
      reviewDialogVisible.value = false;
      fetchProjects();
    }
  } catch {
    ElMessage.error("操作失败");
  }
};

const openBatchDialog = () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning("请先勾选要驳回的项目");
    return;
  }
  batchForm.value.comments = "";
  batchDialogVisible.value = true;
};

const submitBatchReject = async () => {
  if (!batchForm.value.comments) {
    ElMessage.warning("请输入驳回原因");
    return;
  }
  batchSubmitting.value = true;
  try {
    const payload: {
      review_ids: number[];
      action: string;
      comments: string;
    } = {
      review_ids: selectedRows.value
        .map((row) => row.review_id)
        .filter((id): id is number => typeof id === "number"),
      action: "reject",
      comments: batchForm.value.comments,
    };
    const res = await request.post("/reviews/batch-review/", payload);
    if (isRecord(res) && res.code === 200) {
      ElMessage.success("批量驳回完成");
      batchDialogVisible.value = false;
      selectedRows.value = [];
      fetchProjects();
    }
  } catch (error) {
    ElMessage.error(getErrorMessage(error, "批量驳回失败"));
  } finally {
    batchSubmitting.value = false;
  }
};

onMounted(() => {
  fetchProjects();
});
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.review-page {
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

.header-left {
  display: flex;
  align-items: center;
}

.header-title {
  font-size: 16px;
  color: $slate-800;
}

.header-actions {
  display: flex;
  align-items: center;
}

.action-bar {
  display: flex;
  justify-content: flex-end;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
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
