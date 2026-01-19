<template>
  <div class="funds-manage-container">
    <el-card class="main-card" shadow="never" v-loading="loading">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="header-title">经费管理</span>
            <el-tag
              v-if="activeProject"
              size="small"
              effect="plain"
              class="ml-2"
              >{{ activeProject.title }}</el-tag
            >
          </div>
          <div class="header-actions">
            <el-select
              v-model="activeProjectId"
              placeholder="选择项目"
              filterable
              clearable
              style="width: 260px"
              class="mr-2"
              @change="handleProjectChange"
            >
              <el-option
                v-for="item in projects"
                :key="item.id"
                :label="`${item.project_no || ''} ${item.title}`"
                :value="item.id"
              />
            </el-select>
            <el-button
              type="primary"
              :disabled="!activeProjectId"
              @click="showAddDialog"
              >录入支出</el-button
            >
          </div>
        </div>
      </template>

      <div v-if="projects.length === 0" class="empty-container">
        <el-empty description="暂无可管理的项目" />
      </div>

      <div v-else>
        <div v-if="!activeProjectId" class="empty-container">
          <el-empty description="请选择项目" />
        </div>

        <div v-else>
          <div class="stats-panel mb-4">
            <el-row :gutter="20">
              <el-col :span="6">
                <el-statistic
                  title="总预算"
                  :value="stats.total_budget"
                  :precision="2"
                  suffix="元"
                />
              </el-col>
              <el-col :span="6">
                <el-statistic
                  title="已使用"
                  :value="stats.used_amount"
                  :precision="2"
                  suffix="元"
                  value-style="color: var(--el-color-danger)"
                />
              </el-col>
              <el-col :span="6">
                <el-statistic
                  title="剩余额度"
                  :value="stats.remaining_amount"
                  :precision="2"
                  suffix="元"
                  value-style="color: var(--el-color-success)"
                />
              </el-col>
              <el-col :span="6">
                <div class="statistic-card">
                  <div class="statistic-title">使用率</div>
                  <el-progress
                    :percentage="stats.usage_rate"
                    :color="getUsageColor(stats.usage_rate)"
                    :format="formatUsageText"
                  />
                </div>
              </el-col>
            </el-row>
          </div>

          <el-divider />

          <el-table :data="expenditures" style="width: 100%" stripe border>
            <el-table-column
              prop="expenditure_date"
              label="日期"
              width="120"
              sortable
            />
            <el-table-column prop="title" label="支出事项" min-width="180" />
            <el-table-column
              prop="amount"
              label="金额 (元)"
              width="150"
              align="right"
            >
              <template #default="scope">
                {{ Number(scope.row.amount).toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column
              prop="proof_file_url"
              label="凭证"
              width="100"
              align="center"
            >
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
            <el-table-column
              prop="created_by_name"
              label="录入人"
              width="120"
            />
            <el-table-column label="状态" width="140" align="center">
              <template #default="scope">
                <el-tag :type="getReviewStatusType(scope.row)">
                  {{ getReviewStatusLabel(scope.row) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column
              label="操作"
              width="200"
              align="center"
              fixed="right"
            >
              <template #default="scope">
                <template v-if="scope.row.can_review">
                  <el-button
                    link
                    type="success"
                    size="small"
                    @click="handleWorkflowReview(scope.row, true)"
                    >通过</el-button
                  >
                  <el-button
                    link
                    type="danger"
                    size="small"
                    @click="handleWorkflowReview(scope.row, false)"
                    >驳回</el-button
                  >
                </template>
                <el-button
                  link
                  type="danger"
                  size="small"
                  @click="handleDelete(scope.row)"
                  >删除</el-button
                >
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-card>

    <AddExpenseDialog
      v-model:visible="dialogVisible"
      :project-id="activeProjectId"
      @success="refreshProjectData"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import request from "@/utils/request";
import AddExpenseDialog from "@/views/student/funds/components/AddExpenseDialog.vue";
import { removeProjectExpenditure } from "@/api/projects";
import { CONFIG } from "@/config";

defineOptions({
  name: "FundsView",
});

type ProjectItem = {
  id: number;
  project_no?: string;
  title: string;
};

type ExpenditureItem = {
  id: number;
  expenditure_date?: string;
  title?: string;
  amount?: number | string;
  proof_file_url?: string;
  created_by_name?: string;
  status?: string;
  status_display?: string;
  leader_review_status?: string;
  current_node_name?: string;
  can_review?: boolean;
};

type StatsPayload = {
  total_budget?: number;
  used_amount?: number;
  remaining_amount?: number;
  usage_rate?: number;
};

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null;

const normalizeList = <T>(payload: unknown): T[] => {
  if (!isRecord(payload)) return [];
  if (Array.isArray(payload.results)) return payload.results as T[];
  if (isRecord(payload.data) && Array.isArray(payload.data.results)) {
    return payload.data.results as T[];
  }
  if (Array.isArray(payload.data)) return payload.data as T[];
  return [];
};

const getErrorMessage = (error: unknown, fallback: string) => {
  if (error instanceof Error) {
    return error.message || fallback;
  }
  if (typeof error === "string") {
    return error || fallback;
  }
  return fallback;
};

const loading = ref(false);
const dialogVisible = ref(false);
const projects = ref<ProjectItem[]>([]);
const expenditures = ref<ExpenditureItem[]>([]);
const activeProjectId = ref<number | null>(null);

const stats = reactive({
  total_budget: 0,
  used_amount: 0,
  remaining_amount: 0,
  usage_rate: 0,
});

const activeProject = computed(
  () => projects.value.find((item) => item.id === activeProjectId.value) || null
);

const fetchProjects = async () => {
  loading.value = true;
  try {
    const res = await request.get("/projects/", {
      params: {
        status_in:
          "IN_PROGRESS,MID_TERM_DRAFT,MID_TERM_SUBMITTED,MID_TERM_REVIEWING,MID_TERM_REJECTED,READY_FOR_CLOSURE,CLOSURE_DRAFT,CLOSURE_SUBMITTED,CLOSURE_LEVEL2_REVIEWING,CLOSURE_LEVEL1_REVIEWING",
      },
    });
    const payload = isRecord(res) && isRecord(res.data) ? res.data : res;
    projects.value = normalizeList<ProjectItem>(payload);
    if (!activeProjectId.value && projects.value.length > 0) {
      activeProjectId.value = projects.value[0].id;
    }
  } catch (error: unknown) {
    ElMessage.error(getErrorMessage(error, "获取项目列表失败"));
  } finally {
    loading.value = false;
  }
};

const fetchStats = async (projectId: number) => {
  try {
    const res = await request.get(`/projects/${projectId}/budget-stats/`);
    const payload = isRecord(res) && isRecord(res.data) ? res.data : res;
    const data =
      isRecord(payload) && isRecord(payload.data) ? payload.data : payload;
    Object.assign(stats, data as StatsPayload);
  } catch (error: unknown) {
    console.error(error);
  }
};

const fetchExpenditures = async (projectId: number) => {
  try {
    const res = await request.get(`/projects/expenditures/`, {
      params: { project: projectId },
    });
    const payload = isRecord(res) && isRecord(res.data) ? res.data : res;
    expenditures.value = normalizeList<ExpenditureItem>(payload);
  } catch (error: unknown) {
    console.error(error);
  }
};

const handleDelete = async (row: ExpenditureItem) => {
  try {
    await ElMessageBox.confirm(
      "确定删除该经费记录吗？删除后可在回收站恢复。",
      "提示",
      {
        type: "warning",
      }
    );
    const res = await removeProjectExpenditure(row.id);
    if (isRecord(res) && (res.code === 200 || res.status === 204)) {
      ElMessage.success("已移入回收站");
      refreshProjectData();
    } else {
      ElMessage.error(
        (isRecord(res) && typeof res.message === "string" && res.message) ||
          "删除失败"
      );
    }
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

const handleWorkflowReview = async (row: ExpenditureItem, approved: boolean) => {
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
    refreshProjectData();
  } catch {
    // cancel
  }
};

const resolveFileUrl = (url?: string) => {
  if (!url) return "";
  if (/^https?:\/\//i.test(url)) return url;
  return `${CONFIG.api.BASE_URL}${url}`;
};

const refreshProjectData = async () => {
  if (!activeProjectId.value) return;
  await fetchStats(activeProjectId.value);
  await fetchExpenditures(activeProjectId.value);
};

const handleProjectChange = () => {
  if (activeProjectId.value) {
    refreshProjectData();
  }
};

const showAddDialog = () => {
  if (!activeProjectId.value) {
    ElMessage.warning("请先选择项目");
    return;
  }
  dialogVisible.value = true;
};

const getUsageColor = (rate: number) => {
  if (rate < 60) return "#10b981";
  if (rate < 90) return "#f59e0b";
  return "#ef4444";
};

const formatUsageText = (percentage: number) => `${percentage}%`;

onMounted(async () => {
  await fetchProjects();
  if (activeProjectId.value) {
    await refreshProjectData();
  }
});
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.funds-manage-container {
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

.stats-panel {
  margin-top: 8px;
}

.ml-2 {
  margin-left: 8px;
}
.mr-2 {
  margin-right: 8px;
}
.mb-4 {
  margin-bottom: 16px;
}
</style>
