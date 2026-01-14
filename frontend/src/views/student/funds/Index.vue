<template>
  <div class="funds-list-container">
    <el-card class="main-card" shadow="never" v-loading="loading">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="header-title">经费管理</span>
          </div>
          <div class="header-actions">
            <el-button type="primary" @click="showAddDialog"
              >录入支出</el-button
            >
          </div>
        </div>
      </template>

      <div v-if="!project" class="empty-container">
        <el-empty description="暂无进行中的项目" />
      </div>

      <div v-else>
        <!-- 预算统计面板 -->
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
                  :status="getUsageStatus(stats.usage_rate)"
                />
              </div>
            </el-col>
          </el-row>
        </div>

        <el-divider />

        <!-- 支出列表 -->
        <el-table
          :data="expenditures"
          style="width: 100%"
          stripe
          header-cell-class-name="table-header-cell"
        >
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
                :href="scope.row.proof_file_url"
                target="_blank"
                :underline="false"
              >
                <el-icon><Document /></el-icon> 查看
              </el-link>
              <span v-else class="text-gray-400">无</span>
            </template>
          </el-table-column>
          <el-table-column
            prop="status"
            label="状态"
            width="100"
            align="center"
          >
            <template #default>
              <el-tag type="info">已录入</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_by_name" label="录入人" width="120" />
          <el-table-column
            label="操作"
            width="120"
            align="center"
            fixed="right"
          >
            <template #default="scope">
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
    </el-card>

    <AddExpenseDialog
      v-model:visible="dialogVisible"
      :project-id="project?.id || null"
      @success="fetchData"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from "vue";
import { useRoute } from "vue-router";
import { Document } from "@element-plus/icons-vue";
import AddExpenseDialog from "./components/AddExpenseDialog.vue";
import request from "@/utils/request";
import { ElMessage, ElMessageBox } from "element-plus";
import { removeProjectExpenditure } from "@/api/projects";

defineOptions({
  name: "StudentFundsView",
});

const route = useRoute();

type ProjectItem = {
  id: number;
  project_no?: string;
  title?: string;
};

type ExpenditureItem = {
  id: number;
  expenditure_date?: string;
  title?: string;
  amount?: number | string;
  proof_file_url?: string;
  created_by_name?: string;
};

type StatsPayload = {
  total_budget?: number;
  used_amount?: number;
  remaining_amount?: number;
  usage_rate?: number;
};

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null;

const resolveList = <T>(payload: unknown): T[] => {
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

// 状态定义
const loading = ref(false);
const dialogVisible = ref(false);
const project = ref<ProjectItem | null>(null);
const expenditures = ref<ExpenditureItem[]>([]);

const stats = reactive({
  total_budget: 0,
  used_amount: 0,
  remaining_amount: 0,
  usage_rate: 0,
});

// 获取项目信息
const fetchProject = async (projectId: number) => {
  try {
    const { data } = await request.get(`/projects/${projectId}/`);
    if (isRecord(data)) {
      project.value = data as ProjectItem;
      return projectId;
    }
    return null;
  } catch (error) {
    console.error("Failed to fetch project", error);
    ElMessage.error("获取项目信息失败");
    return null;
  }
};

const fetchStats = async (projectId: number) => {
  try {
    const { data } = await request.get(`/projects/${projectId}/budget-stats/`);
    Object.assign(stats, data as StatsPayload);
  } catch (error) {
    console.error("Failed to fetch stats", error);
  }
};

const fetchExpenditures = async (projectId: number) => {
  try {
    const { data } = await request.get(`/projects/expenditures/`, {
      params: { project: projectId },
    });
    expenditures.value = resolveList<ExpenditureItem>(data);
  } catch (error) {
    console.error("Failed to fetch expenditures", error);
  }
};

const fetchData = async () => {
  loading.value = true;
  try {
    const projectIdParam = route.params.projectId;
    if (!projectIdParam) {
      ElMessage.error("缺少项目ID参数");
      return;
    }
    const projectId = Number(projectIdParam);
    if (isNaN(projectId)) {
      ElMessage.error("项目ID格式错误");
      return;
    }
    await fetchProject(projectId);
    await Promise.all([fetchStats(projectId), fetchExpenditures(projectId)]);
  } finally {
    loading.value = false;
  }
};

const showAddDialog = () => {
  if (!project.value) {
    ElMessage.warning("未找到有效项目");
    return;
  }
  dialogVisible.value = true;
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
      fetchData();
    } else {
      const message =
        isRecord(res) && typeof res.message === "string"
          ? res.message
          : "删除失败";
      ElMessage.error(message);
    }
  } catch {
    // cancel
  }
};

const getUsageStatus = (rate: number) => {
  if (rate >= 100) return "exception";
  if (rate >= 80) return "warning";
  return "success";
};

onMounted(() => {
  fetchData();
});
</script>

<style scoped lang="scss">
.funds-list-container {
  padding: 20px;
}

.main-card {
  border-radius: 8px;
  :deep(.el-card__header) {
    padding: 16px 20px;
    font-weight: 600;
    border-bottom: 1px solid #e2e8f0;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-title {
  font-size: 16px;
  color: #1e293b;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.statistic-card {
  background-color: #f8fafc;
  border-radius: 8px;
  padding: 12px;
  text-align: center;
}

.statistic-title {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-bottom: 4px;
}

.mb-4 {
  margin-bottom: 20px;
}

.text-gray-400 {
  color: #9ca3af;
}
</style>
