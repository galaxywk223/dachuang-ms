<template>
  <div class="funds-manage-container">
    <el-card class="main-card" shadow="never" v-loading="loading">
      <template #header>
        <div class="card-header">
           <div class="header-left">
             <span class="header-title">经费管理</span>
             <el-tag v-if="activeProject" size="small" effect="plain" class="ml-2">{{ activeProject.title }}</el-tag>
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
             <el-button type="primary" :disabled="!activeProjectId" @click="showAddDialog">录入支出</el-button>
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
                <el-statistic title="总预算" :value="stats.total_budget" :precision="2" suffix="元" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="已使用" :value="stats.used_amount" :precision="2" suffix="元" value-style="color: var(--el-color-danger)" />
              </el-col>
              <el-col :span="6">
                <el-statistic title="剩余额度" :value="stats.remaining_amount" :precision="2" suffix="元" value-style="color: var(--el-color-success)" />
              </el-col>
              <el-col :span="6">
                <div class="statistic-card">
                  <div class="statistic-title">使用率</div>
                  <el-progress :percentage="stats.usage_rate" :status="getUsageStatus(stats.usage_rate)" />
                </div>
              </el-col>
            </el-row>
          </div>

          <el-divider />

          <el-table :data="expenditures" style="width: 100%" stripe border>
            <el-table-column prop="expenditure_date" label="日期" width="120" sortable />
            <el-table-column prop="title" label="支出事项" min-width="180" />
            <el-table-column prop="category_name" label="类别" width="120">
              <template #default="scope">
                <el-tag>{{ scope.row.category_name || '未分类' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="amount" label="金额 (元)" width="150" align="right">
              <template #default="scope">
                {{ Number(scope.row.amount).toFixed(2) }}
              </template>
            </el-table-column>
            <el-table-column prop="proof_file_url" label="凭证" width="100" align="center">
              <template #default="scope">
                <el-link v-if="scope.row.proof_file_url" type="primary" :href="scope.row.proof_file_url" target="_blank" :underline="false">
                  查看
                </el-link>
                <span v-else class="text-gray-400">无</span>
              </template>
            </el-table-column>
            <el-table-column prop="created_by_name" label="录入人" width="120" />
            <el-table-column label="操作" width="120" align="center" fixed="right">
              <template #default="scope">
                <el-button link type="danger" size="small" @click="handleDelete(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-card>

    <AddExpenseDialog
      v-model:visible="dialogVisible"
      :project-id="activeProjectId"
      :categories="categories"
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

const loading = ref(false);
const dialogVisible = ref(false);
const projects = ref<any[]>([]);
const expenditures = ref<any[]>([]);
const categories = ref<any[]>([]);
const activeProjectId = ref<number | null>(null);

const stats = reactive({
  total_budget: 0,
  used_amount: 0,
  remaining_amount: 0,
  usage_rate: 0,
});

const activeProject = computed(() =>
  projects.value.find((item) => item.id === activeProjectId.value) || null
);

const fetchProjects = async () => {
  loading.value = true;
  try {
    const res: any = await request.get("/projects/", {
      params: {
        status_in:
          "IN_PROGRESS,MID_TERM_DRAFT,MID_TERM_SUBMITTED,MID_TERM_REVIEWING,MID_TERM_APPROVED,MID_TERM_REJECTED,CLOSURE_DRAFT,CLOSURE_SUBMITTED,CLOSURE_LEVEL2_REVIEWING,CLOSURE_LEVEL1_REVIEWING",
      },
    });
    const payload = res.data || res;
    projects.value = payload.results || payload.data?.results || payload.data || [];
    if (!activeProjectId.value && projects.value.length > 0) {
      activeProjectId.value = projects.value[0].id;
    }
  } catch (error: any) {
    ElMessage.error(error.message || "获取项目列表失败");
  } finally {
    loading.value = false;
  }
};

const fetchStats = async (projectId: number) => {
  try {
    const res: any = await request.get(`/projects/${projectId}/budget-stats/`);
    const payload = res.data || res;
    Object.assign(stats, payload.data || payload);
  } catch (error) {
    console.error(error);
  }
};

const fetchExpenditures = async (projectId: number) => {
  try {
    const res: any = await request.get(`/projects/expenditures/`, {
      params: { project: projectId },
    });
    const payload = res.data || res;
    expenditures.value = payload.results || payload.data?.results || payload.data || [];
  } catch (error) {
    console.error(error);
  }
};

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm("确定删除该经费记录吗？删除后可在回收站恢复。", "提示", {
      type: "warning",
    });
    const res: any = await removeProjectExpenditure(row.id);
    if (res?.code === 200 || res?.status === 204) {
      ElMessage.success("已移入回收站");
      refreshProjectData();
    } else {
      ElMessage.error(res?.message || "删除失败");
    }
  } catch {
    // cancel
  }
};

const fetchCategories = async () => {
  try {
    const response = await request.get("/dictionaries/items/", {
      params: { type_code: "EXPENDITURE_CATEGORY" },
    });
    const list =
      (response as any)?.data?.results ??
      (response as any)?.results ??
      (response as any)?.data ??
      response;
    categories.value = Array.isArray(list) ? list : [];
    if (categories.value.length === 0) {
      categories.value = [
        { id: 1, label: "设备费", value: "EQUIPMENT" },
        { id: 2, label: "材料费", value: "MATERIAL" },
        { id: 3, label: "差旅费", value: "TRAVEL" },
        { id: 4, label: "会议费", value: "MEETING" },
        { id: 5, label: "劳务费", value: "LABOR" },
      ];
    }
  } catch (error) {
    console.error(error);
  }
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

const getUsageStatus = (rate: number) => {
  if (rate < 60) return "success";
  if (rate < 90) return "warning";
  return "exception";
};

onMounted(async () => {
  await fetchCategories();
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
  
.ml-2 { margin-left: 8px; }
.mr-2 { margin-right: 8px; }
.mb-4 { margin-bottom: 16px; }
</style>
