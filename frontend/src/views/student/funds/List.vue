<template>
  <div class="funds-list-container">
    <el-card class="box-card" v-loading="loading">
      <template #header>
        <div class="card-header">
          <span class="title">经费管理</span>
          <el-button type="primary" @click="showAddDialog">录入支出</el-button>
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

        <!-- 支出列表 -->
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
                 <el-icon><Document /></el-icon> 查看
              </el-link>
              <span v-else class="text-gray-400">无</span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100" align="center">
            <template #default>
               <el-tag type="info">已录入</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_by_name" label="录入人" width="120" />
        </el-table>
      </div>
    </el-card>

    <AddExpenseDialog 
      v-model:visible="dialogVisible"
      :project-id="project?.id || null"
      :categories="categories"
      @success="fetchData"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from "vue";
import { Document } from '@element-plus/icons-vue';
import AddExpenseDialog from "./components/AddExpenseDialog.vue";
import request from "@/utils/request";
import { ElMessage } from "element-plus";

// 状态定义
const loading = ref(false);
const dialogVisible = ref(false);
const project = ref<any>(null);
const expenditures = ref<any[]>([]);
const categories = ref<any[]>([]);

const stats = reactive({
  total_budget: 0,
  used_amount: 0,
  remaining_amount: 0,
  usage_rate: 0,
});

// 获取项目及相关数据
const fetchProject = async () => {
  try {
    const { data } = await request.get('/projects/', {
        // 获取进行中或各种状态的项目
         params: { status_in: 'IN_PROGRESS,MID_TERM_DRAFT,MID_TERM_SUBMITTED,MID_TERM_REVIEWING,MID_TERM_APPROVED,MID_TERM_REJECTED' }
    });
    if (data.results && data.results.length > 0) {
        project.value = data.results[0]; // 默认取第一个
        return project.value.id;
    }
    return null;
  } catch (error) {
    console.error("Failed to fetch project", error);
    return null;
  }
};

const fetchStats = async (projectId: number) => {
    try {
        const { data } = await request.get(`/projects/${projectId}/budget-stats/`);
        Object.assign(stats, data);
    } catch (error) {
        console.error("Failed to fetch stats", error);
    }
};

const fetchExpenditures = async (projectId: number) => {
    try {
        const { data } = await request.get(`/projects/expenditures/`, {
            params: { project: projectId }
        });
        expenditures.value = data.results || data; // 兼容分页或不分页
    } catch (error) {
        console.error("Failed to fetch expenditures", error);
    }
};

const fetchCategories = async () => {
    try {
        // Code hardcoded for now or fetch by type code
        // Assuming we have a dictionary API or we just mock it for now if strict logic not enforced
        // Real logic: fetch by code 'EXPENDITURE_CATEGORY'
        // For now, let's mock or try to fetch if we had the endpoint
        // Let's assume we have /dictionaries/items/?type__code=EXPENDITURE_CATEGORY
        const response = await request.get('/dictionaries/items/', {
            params: { type_code: 'EXPENDITURE_CATEGORY' }
        });
        const list =
            (response as any)?.data?.results ??
            (response as any)?.results ??
            (response as any)?.data ??
            response;
        categories.value = Array.isArray(list) ? list : [];
        
        // Fail-safe mock if empty
        if (categories.value.length === 0) {
            categories.value = [
                { id: 1, label: '设备费', value: 'EQUIPMENT' },
                { id: 2, label: '材料费', value: 'MATERIAL' },
                { id: 3, label: '差旅费', value: 'TRAVEL' },
                { id: 4, label: '版面费', value: 'PUBLICATION' },
                { id: 5, label: '服务费', value: 'SERVICE' },
                { id: 6, label: '其他', value: 'OTHER' },
            ];
        }
    } catch (error) {
         // Fallback default
         categories.value = [
            { id: 1, label: '设备费', value: 'EQUIPMENT' },
            { id: 2, label: '材料费', value: 'MATERIAL' },
        ];
    }
};

const fetchData = async () => {
    loading.value = true;
    try {
        const projectId = project.value?.id || await fetchProject();
        if (projectId) {
            await Promise.all([
                fetchStats(projectId),
                fetchExpenditures(projectId)
            ]);
        }
        await fetchCategories(); // One time ideally
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

const getUsageStatus = (rate: number) => {
    if (rate >= 100) return 'exception';
    if (rate >= 80) return 'warning';
    return 'success';
};

onMounted(() => {
    fetchData();
});

</script>

<style scoped lang="scss">
.funds-list-container {
    padding: 20px;
    
    .card-header {
       display: flex;
       justify-content: space-between;
       align-items: center;
       .title { font-size: 18px; font-weight: bold; }
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
}
</style>
