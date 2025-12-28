<template>
  <el-form label-width="120px" class="config-form" label-position="top">
    <div class="section-block batch-opt-bar">
      <span class="label">一键设置所有时间：</span>
      <el-date-picker
        v-model="localGlobalDateRange"
        type="daterange"
        range-separator="至"
        start-placeholder="开始日期"
        end-placeholder="截止日期"
        value-format="YYYY-MM-DD"
        size="default"
        class="mr-2"
        style="width: 260px"
        :disabled="isReadOnly"
      />
      <el-button
        type="primary"
        plain
        @click="applyBatchDates"
        :disabled="!globalDateRange || isReadOnly"
      >
        应用
      </el-button>
      <span class="tip ml-2 text-gray text-xs">注：将批量设置下方所有时间段</span>
    </div>

    <div class="section-block">
      <div class="block-title">提交窗口设置</div>
      <el-row :gutter="24">
        <el-col :span="12">
          <el-card shadow="never" class="sub-card">
            <template #header><span class="sub-title">项目申报提交</span></template>
            <div class="card-body">
              <div class="flex-row">
                <el-switch v-model="localApplicationWindow.enabled" active-text="开启" :disabled="isReadOnly" />
              </div>
              <el-date-picker
                v-model="localApplicationWindow.range"
                type="daterange"
                range-separator="至"
                start-placeholder="开始"
                end-placeholder="截止"
                value-format="YYYY-MM-DD"
                :disabled="isReadOnly"
                style="width: 100%; margin-top: 12px"
              />
            </div>
          </el-card>
        </el-col>
        <el-col :span="12">
          <el-card shadow="never" class="sub-card">
            <template #header><span class="sub-title">专家评审时间</span></template>
            <div class="card-body">
              <div class="flex-row">
                <el-switch v-model="localExpertReviewWindow.enabled" active-text="开启" :disabled="isReadOnly" />
              </div>
              <el-date-picker
                v-model="localExpertReviewWindow.range"
                type="daterange"
                range-separator="至"
                start-placeholder="开始"
                end-placeholder="截止"
                value-format="YYYY-MM-DD"
                :disabled="isReadOnly"
                style="width: 100%; margin-top: 12px"
              />
            </div>
          </el-card>
        </el-col>
        <el-col :span="12" class="mt-4">
          <el-card shadow="never" class="sub-card">
            <template #header><span class="sub-title">中期检查提交</span></template>
            <div class="card-body">
              <div class="flex-row">
                <el-switch v-model="localMidtermWindow.enabled" active-text="开启" :disabled="isReadOnly" />
              </div>
              <el-date-picker
                v-model="localMidtermWindow.range"
                type="daterange"
                range-separator="至"
                start-placeholder="开始"
                end-placeholder="截止"
                value-format="YYYY-MM-DD"
                :disabled="isReadOnly"
                style="width: 100%; margin-top: 12px"
              />
            </div>
          </el-card>
        </el-col>
        <el-col :span="12" class="mt-4">
          <el-card shadow="never" class="sub-card">
            <template #header><span class="sub-title">结题报告提交</span></template>
            <div class="card-body">
              <div class="flex-row">
                <el-switch v-model="localClosureWindow.enabled" active-text="开启" :disabled="isReadOnly" />
              </div>
              <el-date-picker
                v-model="localClosureWindow.range"
                type="daterange"
                range-separator="至"
                start-placeholder="开始"
                end-placeholder="截止"
                value-format="YYYY-MM-DD"
                :disabled="isReadOnly"
                style="width: 100%; margin-top: 12px"
              />
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <div class="section-block mt-6">
      <div class="block-title">各级审核时间配置</div>
      <div class="review-matrix">
        <div class="matrix-header">
          <div class="col-phase">阶段</div>
          <div class="col-role">指导教师审核</div>
          <div class="col-role">学院审核</div>
          <div class="col-role">校级审核</div>
        </div>
        <div class="matrix-row">
          <div class="col-phase">申报审核</div>
          <div class="col-role">
            <el-switch v-model="localReviewWindow.application.teacher.enabled" size="small" :disabled="isReadOnly" />
            <el-date-picker
              v-model="localReviewWindow.application.teacher.range"
              type="daterange"
              size="small"
              style="width: 200px; margin-top: 4px"
              value-format="YYYY-MM-DD"
              range-separator="-"
              :disabled="isReadOnly"
            />
          </div>
          <div class="col-role">
            <el-switch v-model="localReviewWindow.application.level2.enabled" size="small" :disabled="isReadOnly" />
            <el-date-picker
              v-model="localReviewWindow.application.level2.range"
              type="daterange"
              size="small"
              style="width: 200px; margin-top: 4px"
              value-format="YYYY-MM-DD"
              range-separator="-"
              :disabled="isReadOnly"
            />
          </div>
          <div class="col-role">
            <el-switch v-model="localReviewWindow.application.level1.enabled" size="small" :disabled="isReadOnly" />
            <el-date-picker
              v-model="localReviewWindow.application.level1.range"
              type="daterange"
              size="small"
              style="width: 200px; margin-top: 4px"
              value-format="YYYY-MM-DD"
              range-separator="-"
              :disabled="isReadOnly"
            />
          </div>
        </div>
        <div class="matrix-row">
          <div class="col-phase">中期审核</div>
          <div class="col-role">
            <el-switch v-model="localReviewWindow.midterm.teacher.enabled" size="small" :disabled="isReadOnly" />
            <el-date-picker
              v-model="localReviewWindow.midterm.teacher.range"
              type="daterange"
              size="small"
              style="width: 200px; margin-top: 4px"
              value-format="YYYY-MM-DD"
              range-separator="-"
              :disabled="isReadOnly"
            />
          </div>
          <div class="col-role">
            <el-switch v-model="localReviewWindow.midterm.level2.enabled" size="small" :disabled="isReadOnly" />
            <el-date-picker
              v-model="localReviewWindow.midterm.level2.range"
              type="daterange"
              size="small"
              style="width: 200px; margin-top: 4px"
              value-format="YYYY-MM-DD"
              range-separator="-"
              :disabled="isReadOnly"
            />
          </div>
          <div class="col-role bg-gray">
            <span class="text-xs text-gray">无需校级审核</span>
          </div>
        </div>
        <div class="matrix-row">
          <div class="col-phase">结题审核</div>
          <div class="col-role">
            <el-switch v-model="localReviewWindow.closure.teacher.enabled" size="small" :disabled="isReadOnly" />
            <el-date-picker
              v-model="localReviewWindow.closure.teacher.range"
              type="daterange"
              size="small"
              style="width: 200px; margin-top: 4px"
              value-format="YYYY-MM-DD"
              range-separator="-"
              :disabled="isReadOnly"
            />
          </div>
          <div class="col-role">
            <el-switch v-model="localReviewWindow.closure.level2.enabled" size="small" :disabled="isReadOnly" />
            <el-date-picker
              v-model="localReviewWindow.closure.level2.range"
              type="daterange"
              size="small"
              style="width: 200px; margin-top: 4px"
              value-format="YYYY-MM-DD"
              range-separator="-"
              :disabled="isReadOnly"
            />
          </div>
          <div class="col-role">
            <el-switch v-model="localReviewWindow.closure.level1.enabled" size="small" :disabled="isReadOnly" />
            <el-date-picker
              v-model="localReviewWindow.closure.level1.range"
              type="daterange"
              size="small"
              style="width: 200px; margin-top: 4px"
              value-format="YYYY-MM-DD"
              range-separator="-"
              :disabled="isReadOnly"
            />
          </div>
        </div>
      </div>
    </div>
  </el-form>
</template>

<script setup lang="ts">
import { computed, reactive, watch } from "vue";

const props = defineProps<{
  globalDateRange: string[];
  applyBatchDates: () => void;
  isReadOnly: boolean;
  applicationWindow: { enabled: boolean; range: string[] };
  midtermWindow: { enabled: boolean; range: string[] };
  closureWindow: { enabled: boolean; range: string[] };
  expertReviewWindow: { enabled: boolean; range: string[] };
  reviewWindow: {
    application: {
      teacher: { enabled: boolean; range: string[] };
      level2: { enabled: boolean; range: string[] };
      level1: { enabled: boolean; range: string[] };
    };
    midterm: {
      teacher: { enabled: boolean; range: string[] };
      level2: { enabled: boolean; range: string[] };
    };
    closure: {
      teacher: { enabled: boolean; range: string[] };
      level2: { enabled: boolean; range: string[] };
      level1: { enabled: boolean; range: string[] };
    };
  };
}>();

type WindowConfig = { enabled: boolean; range: string[] };
type ReviewWindowConfig = {
  application: {
    teacher: WindowConfig;
    level2: WindowConfig;
    level1: WindowConfig;
  };
  midterm: {
    teacher: WindowConfig;
    level2: WindowConfig;
  };
  closure: {
    teacher: WindowConfig;
    level2: WindowConfig;
    level1: WindowConfig;
  };
};

const emit = defineEmits<{
  (event: "update:globalDateRange", value: string[]): void;
  (event: "update:applicationWindow", value: WindowConfig): void;
  (event: "update:midtermWindow", value: WindowConfig): void;
  (event: "update:closureWindow", value: WindowConfig): void;
  (event: "update:expertReviewWindow", value: WindowConfig): void;
  (event: "update:reviewWindow", value: ReviewWindowConfig): void;
}>();

const localGlobalDateRange = computed({
  get: () => props.globalDateRange,
  set: (value: string[]) => emit("update:globalDateRange", value),
});

const cloneWindow = (source: WindowConfig): WindowConfig => ({
  enabled: source.enabled,
  range: [...source.range],
});

const cloneReviewWindow = (source: ReviewWindowConfig): ReviewWindowConfig =>
  JSON.parse(JSON.stringify(source)) as ReviewWindowConfig;

const localApplicationWindow = reactive(cloneWindow(props.applicationWindow));
const localMidtermWindow = reactive(cloneWindow(props.midtermWindow));
const localClosureWindow = reactive(cloneWindow(props.closureWindow));
const localExpertReviewWindow = reactive(cloneWindow(props.expertReviewWindow));
const localReviewWindow = reactive(cloneReviewWindow(props.reviewWindow));

watch(
  () => props.applicationWindow,
  (value) => Object.assign(localApplicationWindow, cloneWindow(value)),
  { deep: true }
);
watch(
  () => props.midtermWindow,
  (value) => Object.assign(localMidtermWindow, cloneWindow(value)),
  { deep: true }
);
watch(
  () => props.closureWindow,
  (value) => Object.assign(localClosureWindow, cloneWindow(value)),
  { deep: true }
);
watch(
  () => props.expertReviewWindow,
  (value) => Object.assign(localExpertReviewWindow, cloneWindow(value)),
  { deep: true }
);
watch(
  () => props.reviewWindow,
  (value) => Object.assign(localReviewWindow, cloneReviewWindow(value)),
  { deep: true }
);

watch(
  localApplicationWindow,
  (value) => emit("update:applicationWindow", { enabled: value.enabled, range: value.range }),
  { deep: true }
);
watch(
  localMidtermWindow,
  (value) => emit("update:midtermWindow", { enabled: value.enabled, range: value.range }),
  { deep: true }
);
watch(
  localClosureWindow,
  (value) => emit("update:closureWindow", { enabled: value.enabled, range: value.range }),
  { deep: true }
);
watch(
  localExpertReviewWindow,
  (value) => emit("update:expertReviewWindow", { enabled: value.enabled, range: value.range }),
  { deep: true }
);
watch(
  localReviewWindow,
  (value) => emit("update:reviewWindow", cloneReviewWindow(value)),
  { deep: true }
);
</script>
