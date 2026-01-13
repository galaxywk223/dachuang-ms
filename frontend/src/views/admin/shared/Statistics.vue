<template>
  <div class="statistics-page">
    <el-card class="main-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="header-title">统计概览</span>
          </div>
          <div class="header-actions">
            <el-button type="primary" plain @click="refreshAll"
              >刷新数据</el-button
            >
          </div>
        </div>
      </template>

      <div class="stats-summary mb-4">
        <el-row :gutter="20">
          <el-col :span="8">
            <StatCard
              :icon="Folder"
              icon-bg="linear-gradient(135deg, #60a5fa 0%, #2563eb 100%)"
              :value="stats.total_projects"
              label="项目总数"
            />
          </el-col>
          <el-col :span="8">
            <StatCard
              :icon="Check"
              icon-bg="linear-gradient(135deg, #34d399 0%, #059669 100%)"
              :value="stats.approved_projects"
              label="已立项/完成"
            />
          </el-col>
          <el-col :span="8">
            <StatCard
              :icon="Clock"
              icon-bg="linear-gradient(135deg, #f59e0b 0%, #d97706 100%)"
              :value="stats.pending_review"
              label="待审核"
            />
          </el-col>
        </el-row>
      </div>

      <el-card class="tool-card mt-4">
        <template #header>
          <div class="card-header">
            <span class="title">项目统计报表</span>
            <el-button type="primary" plain @click="fetchReport"
              >刷新</el-button
            >
          </div>
        </template>
        <el-form inline label-position="left" class="mb-2">
          <el-form-item label="年度">
            <el-input
              v-model="reportFilters.year"
              placeholder="如 2025"
              style="width: 140px"
            />
          </el-form-item>
          <el-form-item label="学院代码">
            <el-input
              v-model="reportFilters.college"
              placeholder="学院代码"
              style="width: 160px"
            />
          </el-form-item>
          <el-form-item label="状态筛选">
            <el-input
              v-model="reportFilters.status_in"
              placeholder="逗号分隔"
              style="width: 220px"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="fetchReport">查询</el-button>
            <el-button @click="resetReport">重置</el-button>
          </el-form-item>
        </el-form>

        <el-row :gutter="16" class="mb-4">
          <el-col :span="6">
            <el-statistic title="项目总数" :value="reportData.total" />
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="12">
            <el-card shadow="never" class="inner-card">
              <template #header><span class="title">按状态</span></template>
              <el-table :data="reportData.by_status" border stripe size="small">
                <el-table-column prop="status" label="状态" />
                <el-table-column
                  prop="count"
                  label="数量"
                  width="100"
                  align="center"
                />
              </el-table>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card shadow="never" class="inner-card">
              <template #header><span class="title">按学院</span></template>
              <el-table
                :data="reportData.by_college"
                border
                stripe
                size="small"
              >
                <el-table-column prop="leader__college" label="学院">
                  <template #default="{ row }">
                    {{ getCollegeLabel(row.leader__college) }}
                  </template>
                </el-table-column>
                <el-table-column
                  prop="count"
                  label="数量"
                  width="100"
                  align="center"
                />
              </el-table>
            </el-card>
          </el-col>
        </el-row>

        <el-row :gutter="16" class="mt-4">
          <el-col :span="12">
            <el-card shadow="never" class="inner-card">
              <template #header><span class="title">按级别</span></template>
              <el-table :data="reportData.by_level" border stripe size="small">
                <el-table-column prop="level__label" label="级别" />
                <el-table-column
                  prop="count"
                  label="数量"
                  width="100"
                  align="center"
                />
              </el-table>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card shadow="never" class="inner-card">
              <template #header><span class="title">按类别</span></template>
              <el-table
                :data="reportData.by_category"
                border
                stripe
                size="small"
              >
                <el-table-column prop="category__label" label="类别" />
                <el-table-column
                  prop="count"
                  label="数量"
                  width="100"
                  align="center"
                />
              </el-table>
            </el-card>
          </el-col>
        </el-row>
      </el-card>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { Folder, Check, Clock } from "@element-plus/icons-vue";
import StatCard from "@/components/common/StatCard.vue";
import {
  getProjectStatistics,
  getProjectStatisticsReport,
} from "@/api/projects/admin";
import { useDictionary } from "@/composables/useDictionary";
import { DICT_CODES } from "@/api/dictionaries";
import dayjs from "dayjs";

defineOptions({
  name: "StatisticsView",
});

type StatsSummary = {
  total_projects: number;
  approved_projects: number;
  pending_review: number;
};

type ReportRow = {
  count?: number;
};

type ReportData = {
  total: number;
  by_status: (ReportRow & { status?: string })[];
  by_college: (ReportRow & { leader__college?: string })[];
  by_level: (ReportRow & { level__label?: string })[];
  by_category: (ReportRow & { category__label?: string })[];
};

type ApiResponse<T> = {
  code?: number;
  data?: T;
  message?: string;
};

const { getLabel, loadDictionaries } = useDictionary();

const stats = reactive<StatsSummary>({
  total_projects: 0,
  approved_projects: 0,
  pending_review: 0,
});

const getCollegeLabel = (collegeCode?: string) => {
  if (!collegeCode) return "-";
  return getLabel(DICT_CODES.COLLEGE, collegeCode);
};

const reportFilters = reactive({
  year: "",
  college: "",
  status_in: "",
});

const reportData = reactive<ReportData>({
  total: 0,
  by_status: [],
  by_college: [],
  by_level: [],
  by_category: [],
});

const fetchReport = async () => {
  try {
    const params: Record<string, string> = {};
    if (reportFilters.year) params.year = reportFilters.year;
    if (reportFilters.college) params.college = reportFilters.college;
    if (reportFilters.status_in) params.status_in = reportFilters.status_in;
    const res = (await getProjectStatisticsReport(
      params
    )) as ApiResponse<ReportData>;
    const data = res?.data;
    reportData.total = data?.total ?? 0;
    reportData.by_status = data?.by_status ?? [];
    reportData.by_college = data?.by_college ?? [];
    reportData.by_level = data?.by_level ?? [];
    reportData.by_category = data?.by_category ?? [];
  } catch (error: unknown) {
    console.error(error);
  }
};

const resetReport = () => {
  reportFilters.year = "";
  reportFilters.college = "";
  reportFilters.status_in = "";
  fetchReport();
};

const fetchStatistics = async () => {
  try {
    const res = (await getProjectStatistics()) as ApiResponse<StatsSummary>;
    if (res.code === 200) {
      Object.assign(stats, res.data);
    }
  } catch {
    ElMessage.error("获取统计数据失败");
  }
};

const refreshAll = () => {
  fetchStatistics();
  fetchReport();
};

onMounted(async () => {
  await loadDictionaries([DICT_CODES.COLLEGE]);
  refreshAll();
});
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.statistics-page {
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

.inner-card {
  :deep(.el-card__header) {
    padding: 10px 12px;
    font-weight: 500;
  }
}

.stats-summary {
  margin-bottom: 24px;
}

.tool-card {
  margin-top: 12px;
}

.tool-row {
  display: flex;
  align-items: center;
  gap: 16px;
}

.actions {
  display: flex;
  gap: 12px;
}

.mb-4 {
  margin-bottom: 16px;
}
.mt-4 {
  margin-top: 16px;
}
</style>
