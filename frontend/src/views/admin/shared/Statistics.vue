<template>
  <div class="statistics-page">
    <el-card class="main-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="header-title">统计概览</span>
          </div>
          <div class="header-actions">
            <el-form inline class="filter-form">
              <el-form-item label="年度" class="mb-0">
                <el-input
                  v-model="reportFilters.year"
                  placeholder="如 2025"
                  style="width: 120px"
                  clearable
                />
              </el-form-item>
              <el-form-item label="学院代码" class="mb-0">
                <el-input
                  v-model="reportFilters.college"
                  placeholder="学院代码"
                  style="width: 140px"
                  clearable
                />
              </el-form-item>
              <el-form-item label="状态筛选" class="mb-0">
                <el-input
                  v-model="reportFilters.status_in"
                  placeholder="逗号分隔"
                  style="width: 180px"
                  clearable
                />
              </el-form-item>
              <el-form-item class="mb-0">
                <el-button type="primary" @click="fetchReport">查询</el-button>
                <el-button @click="resetReport">重置</el-button>
              </el-form-item>
            </el-form>
            <div class="divider"></div>
            <el-button type="primary" plain @click="refreshAll"
              >刷新数据</el-button
            >
          </div>
        </div>
      </template>

      <div class="content-wrapper">
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
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, onMounted } from "vue";
import { getProjectStatisticsReport } from "@/api/projects/admin";
import { useDictionary } from "@/composables/useDictionary";
import { DICT_CODES } from "@/api/dictionaries";

defineOptions({
  name: "StatisticsView",
});

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

const refreshAll = () => {
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
    padding: 12px 20px;
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
  gap: 12px;
}

.filter-form {
  display: flex;
  align-items: center;
  flex-wrap: nowrap;

  &::before,
  &::after {
    display: none !important;
    content: none !important;
  }

  :deep(.el-form-item) {
    display: flex;
    align-items: center;
    margin-bottom: 0;
    margin-right: 12px;

    &:last-child {
      margin-right: 0;
    }

    .el-form-item__label {
      display: flex;
      align-items: center;
      height: 32px;
      line-height: normal;
    }

    .el-form-item__content {
      line-height: 32px;
      vertical-align: middle;
    }
  }
}

.divider {
  width: 1px;
  height: 20px;
  background-color: #e2e8f0;
  margin: 0 8px;
}

.inner-card {
  :deep(.el-card__header) {
    padding: 10px 12px;
    font-weight: 500;
  }
}

.mb-0 {
  margin-bottom: 0 !important;
}

.mb-4 {
  margin-bottom: 16px;
}
.mt-4 {
  margin-top: 16px;
}
</style>
