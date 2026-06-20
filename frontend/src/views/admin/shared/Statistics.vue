<template>
  <div class="dashboard-page page-shell">
    <div class="toolbar-panel">
      <div class="toolbar-actions">
        <el-tag effect="light" type="success">可视化分析</el-tag>
        <el-tag effect="light" type="info">风险识别</el-tag>
      </div>
      <div class="toolbar-actions">
        <el-button type="primary" @click="loadDashboard">刷新数据</el-button>
      </div>
    </div>

    <el-row :gutter="16" class="metric-row">
      <el-col
        v-for="item in metricCards"
        :key="item.key"
        :xs="24"
        :sm="12"
        :md="6"
        :lg="6"
        :xl="3"
      >
        <MetricCard
          :label="item.label"
          :value="item.value"
          :hint="item.hint"
          :tone="item.tone"
          density="compact"
        />
      </el-col>
    </el-row>

    <el-row :gutter="16" class="panel-row">
      <el-col :xs="24" :lg="12">
        <PanelCard class="stat-panel" title="阶段漏斗" caption="项目从申报到结题的阶段分布">
          <BaseChart :option="stageOption" />
        </PanelCard>
      </el-col>
      <el-col :xs="24" :lg="12">
        <PanelCard class="stat-panel" title="学院对比" caption="学院项目数、发布数与结题数对比">
          <BaseChart :option="collegeOption" />
        </PanelCard>
      </el-col>
    </el-row>

    <el-row :gutter="16" class="panel-row">
      <el-col :xs="24" :lg="10">
        <PanelCard class="stat-panel" title="状态分布" caption="当前项目状态结构">
          <div class="status-chart-scroll">
            <BaseChart class="status-chart" :option="statusOption" />
          </div>
        </PanelCard>
      </el-col>
      <el-col :xs="24" :lg="14">
        <PanelCard class="stat-panel" title="风险视图" caption="长期待审、材料缺失等关键风险">
          <template #actions>
            <StatusPill
              :status="risks.length ? 'RUNNING' : 'SUCCESS'"
              :label="`${risks.length} 条风险`"
            />
          </template>
          <template v-if="risks.length">
            <el-table :data="risks" stripe height="318">
              <el-table-column label="风险类型" min-width="170">
                <template #default="{ row }">
                  <StatusPill
                    :status="row.level === 'danger' ? 'FAILED' : 'RUNNING'"
                    :label="row.message"
                  />
                </template>
              </el-table-column>
              <el-table-column
                prop="project_title"
                label="关联项目"
                min-width="220"
                show-overflow-tooltip
              />
            </el-table>
          </template>
          <EmptyState
            v-else
            title="暂无明显风险"
            description="当前批次未识别到长期待审或材料缺失项目。"
            mark="✓"
          />
        </PanelCard>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import type { EChartsOption } from "echarts";
import BaseChart from "@/components/common/BaseChart.vue";
import EmptyState from "@/components/common/EmptyState.vue";
import MetricCard from "@/components/common/MetricCard.vue";
import PanelCard from "@/components/common/PanelCard.vue";
import StatusPill from "@/components/common/StatusPill.vue";
import { getManagementDashboard } from "@/api/projects/admin";

defineOptions({ name: "AdminStatistics" });

type ApiResponse<T> = { data?: T };
type MetricTone = "primary" | "success" | "warning" | "info" | "danger";
type MetricMap = Record<string, number>;
type RiskItem = {
  level?: string;
  message: string;
  project_title?: string;
  [key: string]: unknown;
};
type DashboardData = {
  metrics: MetricMap;
  stage_funnel: { stage: string; count: number }[];
  college_compare: {
    leader__college?: string;
    total: number;
    published: number;
    completed: number;
  }[];
  status_distribution: { status: string; count: number }[];
  risks: RiskItem[];
};

const chartColors = ["#147f73", "#2563eb", "#f59e0b", "#16a34a", "#ef4444", "#64748b"];

const statusNameMap: Record<string, string> = {
  DRAFT: "草稿",
  SUBMITTED: "已提交",
  TEACHER_AUDITING: "导师审核",
  TEACHER_APPROVED: "导师通过",
  TEACHER_REJECTED: "导师退回",
  COLLEGE_AUDITING: "学院审核",
  LEVEL1_AUDITING: "校级审核",
  APPLICATION_RETURNED: "立项退回",
  IN_PROGRESS: "进行中",
  LEVEL2_AUDITING: "二级审核",
  APPROVED: "已立项",
  REJECTED: "已退回",
  MID_TERM_DRAFT: "中期草稿",
  MID_TERM_SUBMITTED: "中期提交",
  MID_TERM_REVIEWING: "中期审核",
  READY_FOR_CLOSURE: "待结题",
  MID_TERM_REJECTED: "中期退回",
  MID_TERM_RETURNED: "中期返修",
  CLOSURE_DRAFT: "结题草稿",
  CLOSURE_SUBMITTED: "结题提交",
  CLOSURE_LEVEL2_REVIEWING: "结题院审",
  CLOSURE_LEVEL2_APPROVED: "院审通过",
  CLOSURE_LEVEL2_REJECTED: "院审退回",
  CLOSURE_LEVEL1_REVIEWING: "结题校审",
  CLOSURE_LEVEL1_APPROVED: "校审通过",
  CLOSURE_LEVEL1_REJECTED: "校审退回",
  CLOSURE_RETURNED: "结题返修",
  COMPLETED: "已完成",
  CLOSED: "已结题",
  TERMINATED: "已终止",
  ARCHIVED: "已归档",
};

const data = ref<DashboardData>({
  metrics: {},
  stage_funnel: [],
  college_compare: [],
  status_distribution: [],
  risks: [],
});

const metricCards = computed<
  {
    key: string;
    label: string;
    value: number;
    hint: string;
    tone: MetricTone;
  }[]
>(() => [
  { key: "applications", label: "申报数", value: data.value.metrics.applications ?? 0, hint: "当前批次有效申报", tone: "primary" },
  { key: "published", label: "发布数", value: data.value.metrics.published ?? 0, hint: "已完成立项公示", tone: "success" },
  { key: "pending", label: "待处理", value: data.value.metrics.pending ?? 0, hint: "仍在审核流转", tone: "warning" },
  { key: "budget_used", label: "经费执行", value: data.value.metrics.budget_used ?? 0, hint: "已登记执行金额", tone: "info" },
  { key: "returned", label: "退回数", value: data.value.metrics.returned ?? 0, hint: "需关注修改质量", tone: "danger" },
  { key: "completed", label: "结题数", value: data.value.metrics.completed ?? 0, hint: "完成归档项目", tone: "success" },
  { key: "achievements", label: "成果数", value: data.value.metrics.achievements ?? 0, hint: "已登记成果记录", tone: "primary" },
  { key: "budget_approved", label: "批准经费", value: data.value.metrics.budget_approved ?? 0, hint: "最终确认经费", tone: "info" },
]);

const axisBase = {
  axisLine: { lineStyle: { color: "#d8e0ea" } },
  axisTick: { show: false },
  axisLabel: { color: "#64748b" },
};

const tooltipBase = {
  backgroundColor: "rgba(15, 23, 42, 0.92)",
  borderWidth: 0,
  textStyle: { color: "#fff" },
};

const displayStatusName = (status?: string) => {
  if (!status) return "未设置";
  return statusNameMap[status] ?? status;
};

const stageOption = computed<EChartsOption>(() => ({
  color: chartColors,
  grid: { left: 36, right: 18, top: 28, bottom: 34 },
  tooltip: { ...tooltipBase, trigger: "axis" },
  xAxis: { ...axisBase, type: "category", data: data.value.stage_funnel.map((item) => item.stage) },
  yAxis: { ...axisBase, type: "value", splitLine: { lineStyle: { color: "#eef2f7" } } },
  series: [
    {
      type: "bar",
      data: data.value.stage_funnel.map((item) => item.count),
      itemStyle: { borderRadius: [10, 10, 0, 0], color: "#147f73" },
      barWidth: 28,
    },
  ],
}));

const collegeOption = computed<EChartsOption>(() => ({
  color: ["#147f73", "#2563eb", "#f59e0b"],
  grid: { left: 36, right: 18, top: 28, bottom: 56 },
  tooltip: { ...tooltipBase, trigger: "axis" },
  legend: { bottom: 0, icon: "roundRect", textStyle: { color: "#64748b" } },
  xAxis: {
    ...axisBase,
    type: "category",
    data: data.value.college_compare.map((item) => item.leader__college || "未设置"),
  },
  yAxis: { ...axisBase, type: "value", splitLine: { lineStyle: { color: "#eef2f7" } } },
  series: [
    { name: "项目数", type: "bar", data: data.value.college_compare.map((item) => item.total), barWidth: 18, itemStyle: { borderRadius: [8, 8, 0, 0] } },
    { name: "已发布", type: "bar", data: data.value.college_compare.map((item) => item.published), barWidth: 18, itemStyle: { borderRadius: [8, 8, 0, 0] } },
    { name: "已结题", type: "bar", data: data.value.college_compare.map((item) => item.completed), barWidth: 18, itemStyle: { borderRadius: [8, 8, 0, 0] } },
  ],
}));

const statusOption = computed<EChartsOption>(() => ({
  color: chartColors,
  tooltip: { ...tooltipBase, trigger: "item" },
  legend: {
    type: "scroll",
    orient: "vertical",
    right: 4,
    top: 24,
    bottom: 12,
    icon: "circle",
    itemWidth: 10,
    itemHeight: 10,
    itemGap: 14,
    pageIconColor: "#147f73",
    pageIconInactiveColor: "#cbd5e1",
    pageTextStyle: { color: "#64748b" },
    textStyle: {
      color: "#64748b",
      width: 82,
      overflow: "truncate",
    },
  },
  series: [
    {
      type: "pie",
      radius: ["44%", "66%"],
      center: ["39%", "50%"],
      avoidLabelOverlap: true,
      label: {
        color: "#475569",
        overflow: "truncate",
        width: 96,
      },
      labelLine: {
        length: 12,
        length2: 14,
      },
      data: data.value.status_distribution.map((item) => ({
        name: displayStatusName(item.status),
        value: item.count,
      })),
    },
  ],
}));

const risks = computed(() => data.value.risks);

const loadDashboard = async () => {
  const response = (await getManagementDashboard()) as ApiResponse<DashboardData>;
  if (response.data) {
    data.value = response.data;
  }
};

onMounted(loadDashboard);
</script>

<style scoped lang="scss">
.metric-row {
  row-gap: 12px;
}

.el-row {
  row-gap: 16px;
}

.panel-row {
  align-items: stretch;

  :deep(.el-col) {
    display: flex;
  }
}

.stat-panel {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;

  :deep(.el-card__body) {
    display: flex;
    flex: 1;
    flex-direction: column;
  }

  :deep(.base-chart) {
    flex: 1;
    min-height: 318px;
  }

  :deep(.status-chart) {
    width: 100%;
    min-width: 520px;
    min-height: 360px;
  }
}

.status-chart-scroll {
  flex: 1;
  width: 100%;
  overflow-x: auto;
  overflow-y: hidden;
}
</style>
