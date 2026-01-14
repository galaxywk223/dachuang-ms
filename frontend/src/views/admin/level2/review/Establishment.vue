<template>
  <div class="review-page">
    <!-- Filter Section -->
    <div class="filter-section">
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
          <el-button type="primary" @click="handleSearch" :icon="Search">
            查询
          </el-button>
          <el-button @click="handleReset" :icon="RefreshLeft"> 重置 </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- Table Section -->
    <div class="table-container">
      <div class="table-header">
        <div class="title-bar">
          <span class="title">立项审核</span>
          <el-tag
            type="info"
            size="small"
            effect="plain"
            round
            class="count-tag"
            >共 {{ total }} 项</el-tag
          >
        </div>
        <div class="actions">
          <el-button type="primary" plain @click="openBatchDialog"
            >批量审核</el-button
          >
        </div>
      </div>

      <el-table
        v-loading="loading"
        :data="projects"
        style="width: 100%"
        :header-cell-style="{
          background: '#f8fafc',
          color: '#475569',
          fontWeight: '600',
          height: '48px',
        }"
        :cell-style="{ color: '#334155', height: '48px' }"
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
        <el-table-column label="重点领域项目" width="110" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.is_key_field" type="success" size="small"
              >是</el-tag
            >
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="重点领域代码" width="110" align="center">
          <template #default="{ row }">
            <span>{{ row.key_domain_code || "-" }}</span>
          </template>
        </el-table-column>
        <el-table-column
          prop="leader_name"
          label="负责人姓名"
          width="100"
          align="center"
        />
        <el-table-column
          prop="leader_student_id"
          label="负责人学号"
          width="120"
          align="center"
        />
        <el-table-column
          prop="college"
          label="学院"
          width="140"
          show-overflow-tooltip
          align="center"
        />
        <el-table-column
          prop="leader_contact"
          label="联系电话"
          width="120"
          align="center"
        />
        <el-table-column
          prop="leader_email"
          label="邮箱"
          width="180"
          show-overflow-tooltip
          align="center"
        />
        <el-table-column
          prop="budget"
          label="项目经费"
          width="100"
          align="center"
        >
          <template #default="{ row }">
            {{ row.budget }}
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
                :icon="View"
                @click="handleViewDetail(row)"
              >
                详情
              </el-button>
              <el-dropdown
                trigger="click"
                @command="(cmd: string) => handleCommand(cmd, row)"
              >
                <el-button type="primary" link size="small" :icon="EditPen">
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

      <div class="pagination-footer">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
          background
          size="small"
          class="custom-pagination"
        />
      </div>
    </div>

    <!-- 审核对话框 -->
    <el-dialog
      v-model="reviewDialogVisible"
      :title="reviewType === 'approve' ? '审核通过' : '驳回申请'"
      width="480px"
      align-center
      destroy-on-close
    >
      <el-form :model="reviewForm" label-position="top">
        <el-form-item
          label="退回至"
          v-if="reviewType === 'reject' && rejectTargets.length > 0"
        >
          <el-select
            v-model="reviewForm.target_node_id"
            placeholder="请选择退回节点"
            style="width: 100%"
            clearable
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

    <el-dialog v-model="batchDialogVisible" title="批量审核" width="520px">
      <el-form label-position="top">
        <el-form-item label="审核结果">
          <el-radio-group v-model="batchForm.action">
            <el-radio label="approve">通过</el-radio>
            <el-radio label="reject">驳回</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="评分">
          <el-input-number v-model="batchForm.score" :min="0" :max="100" />
        </el-form-item>
        <el-form-item label="审核意见">
          <el-input
            v-model="batchForm.comments"
            type="textarea"
            :rows="4"
            placeholder="请输入审核意见"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="batchDialogVisible = false">取消</el-button>
          <el-button
            type="primary"
            :loading="batchSubmitting"
            @click="submitBatchReview"
          >
            提交
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import {
  Search,
  Check,
  Close,
  RefreshLeft,
  ArrowDown,
  View,
  EditPen,
} from "@element-plus/icons-vue";
import {
  getPendingReviews,
  getRejectTargets,
  reviewAction,
  type PendingReview,
  type WorkflowNode,
} from "@/api/reviews";
import ProjectStatusBadge from "@/components/business/project/StatusBadge.vue";
import request from "@/utils/request";

defineOptions({ name: "Level2EstablishmentReviewView" });

const router = useRouter();

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
  status?: string;
  status_display?: string;
};

type ReviewProjectsResponse = {
  code?: number;
  data?: {
    results?: PendingReview[];
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
  target_node_id: null as number | null,
});
const rejectTargets = ref<WorkflowNode[]>([]);

const batchDialogVisible = ref(false);
const batchSubmitting = ref(false);
const batchForm = ref({
  action: "approve",
  comments: "",
  score: null as number | null,
});

const resolveReviewList = (payload: unknown): PendingReview[] => {
  if (Array.isArray(payload)) return payload as PendingReview[];
  if (!isRecord(payload)) return [];
  if (Array.isArray(payload.results)) return payload.results as PendingReview[];
  if (isRecord(payload.data) && Array.isArray(payload.data?.results)) {
    return payload.data?.results as PendingReview[];
  }
  if (Array.isArray(payload.data as PendingReview[])) {
    return payload.data as PendingReview[];
  }
  return [];
};

const resolveReviewCount = (payload: unknown) => {
  if (!isRecord(payload)) return 0;
  if (typeof payload.count === "number") return payload.count;
  if (typeof payload.total === "number") return payload.total;
  if (isRecord(payload.data)) {
    if (typeof payload.data?.count === "number") return payload.data.count;
    if (typeof payload.data?.total === "number") return payload.data.total;
  }
  return 0;
};

const buildProjectRows = (reviews: PendingReview[]): ProjectRow[] =>
  reviews.map((review) => {
    const projectInfo = isRecord(review.project_info)
      ? (review.project_info as ProjectRow)
      : ({} as ProjectRow);
    return {
      ...projectInfo,
      id: (projectInfo.id as number) ?? review.project,
      review_id: review.id,
    };
  });

const fetchProjects = async () => {
  loading.value = true;
  try {
    const response = await getPendingReviews({
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchQuery.value,
      review_type: "APPLICATION",
    });

    const data =
      isRecord(response) && "data" in response ? response.data : response;
    const reviews = resolveReviewList(data);
    projects.value = buildProjectRows(reviews);
    total.value = resolveReviewCount(data) || projects.value.length;
    selectedRows.value = [];
  } catch (error) {
    ElMessage.error(getErrorMessage(error, "获取项目列表失败"));
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
  if (row.id) {
    router.push({ name: "level2-project-detail", params: { id: row.id } });
  } else {
    ElMessage.warning("项目ID缺失");
  }
};

const handleCommand = (command: string, row: ProjectRow) => {
  if (command === "approve") handleApprove(row);
  if (command === "reject") handleReject(row);
};

const handleApprove = (row: ProjectRow) => {
  reviewType.value = "approve";
  reviewForm.value.projectId = row.id;
  reviewForm.value.comment = "";
  reviewDialogVisible.value = true;
};

const handleReject = async (row: ProjectRow) => {
  reviewType.value = "reject";
  reviewForm.value.projectId = row.id;
  reviewForm.value.comment = "";
  reviewForm.value.target_node_id = null;
  rejectTargets.value = [];

  // 加载可退回节点
  try {
    if (typeof row.review_id === "number") {
      const res = await getRejectTargets(row.review_id);
      if (res.code === 200) {
        rejectTargets.value = res.data || [];
      }
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

  try {
    const selectedRow = projects.value.find(
      (row) => row.id === reviewForm.value.projectId
    );
    const data: { comment: string; target_node_id?: number | null } = {
      comment: reviewForm.value.comment,
    };
    let response: ReviewProjectsResponse;
    if (reviewType.value === "approve") {
      if (typeof selectedRow?.review_id === "number") {
        response = (await reviewAction(selectedRow.review_id, {
          action: "approve",
          comments: reviewForm.value.comment,
        })) as ReviewProjectsResponse;
      } else {
        throw new Error("缺少审核记录");
      }
    } else {
      if (reviewForm.value.target_node_id) {
        data.target_node_id = reviewForm.value.target_node_id;
      }
      if (typeof selectedRow?.review_id === "number") {
        response = (await reviewAction(selectedRow.review_id, {
          action: "reject",
          comments: reviewForm.value.comment,
          target_node_id: data.target_node_id ?? null,
        })) as ReviewProjectsResponse;
      } else {
        throw new Error("缺少审核记录");
      }
    }

    if (response.code === 200) {
      ElMessage.success(reviewType.value === "approve" ? "已通过" : "已驳回");
      reviewDialogVisible.value = false;
      fetchProjects();
    }
  } catch (error) {
    ElMessage.error(getErrorMessage(error, "操作失败"));
  }
};

const openBatchDialog = () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning("请先勾选要审核的项目");
    return;
  }
  batchForm.value = { action: "approve", comments: "", score: null };
  batchDialogVisible.value = true;
};

const submitBatchReview = async () => {
  if (selectedRows.value.length === 0) return;
  batchSubmitting.value = true;
  try {
    const payload: {
      review_ids: number[];
      action: string;
      comments: string;
      score?: number;
    } = {
      review_ids: selectedRows.value
        .map((row) => row.review_id)
        .filter((id): id is number => typeof id === "number"),
      action: batchForm.value.action,
      comments: batchForm.value.comments,
    };
    if (batchForm.value.score !== null && batchForm.value.score !== undefined) {
      payload.score = batchForm.value.score;
    }
    const res = await request.post("/reviews/batch-review/", payload);
    if (isRecord(res) && res.code === 200) {
      ElMessage.success("批量审核完成");
      batchDialogVisible.value = false;
      selectedRows.value = [];
      fetchProjects();
    }
  } catch (error) {
    ElMessage.error(getErrorMessage(error, "批量审核失败"));
  } finally {
    batchSubmitting.value = false;
  }
};

onMounted(() => {
  fetchProjects();
});
</script>

<style scoped lang="scss" src="./Establishment.scss"></style>
