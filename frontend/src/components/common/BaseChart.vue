<template>
  <div class="base-chart" ref="chartEl"></div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from "vue";
import { BarChart, LineChart, PieChart } from "echarts/charts";
import {
  GridComponent,
  LegendComponent,
  TitleComponent,
  TooltipComponent,
} from "echarts/components";
import { init, use, type ECharts } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import type { EChartsOption } from "echarts";

use([
  BarChart,
  LineChart,
  PieChart,
  GridComponent,
  LegendComponent,
  TitleComponent,
  TooltipComponent,
  CanvasRenderer,
]);

const props = defineProps<{
  option: EChartsOption;
}>();

const chartEl = ref<HTMLDivElement>();
let chart: ECharts | null = null;

const render = () => {
  if (!chartEl.value) return;
  if (!chart) {
    chart = init(chartEl.value);
  }
  chart.setOption(props.option, true);
};

const resize = () => {
  chart?.resize();
};

onMounted(() => {
  render();
  window.addEventListener("resize", resize);
});

watch(
  () => props.option,
  () => render(),
  { deep: true }
);

onBeforeUnmount(() => {
  window.removeEventListener("resize", resize);
  chart?.dispose();
  chart = null;
});
</script>

<style scoped lang="scss">
.base-chart {
  width: 100%;
  min-height: 280px;
}
</style>
