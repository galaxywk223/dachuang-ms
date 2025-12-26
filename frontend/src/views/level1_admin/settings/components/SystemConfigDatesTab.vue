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
                <el-switch v-model="applicationWindow.enabled" active-text="开启" :disabled="isReadOnly" />
              </div>
              <el-date-picker
                v-model="applicationWindow.range"
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
                <el-switch v-model="expertReviewWindow.enabled" active-text="开启" :disabled="isReadOnly" />
              </div>
              <el-date-picker
                v-model="expertReviewWindow.range"
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
                <el-switch v-model="midtermWindow.enabled" active-text="开启" :disabled="isReadOnly" />
              </div>
              <el-date-picker
                v-model="midtermWindow.range"
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
                <el-switch v-model="closureWindow.enabled" active-text="开启" :disabled="isReadOnly" />
              </div>
              <el-date-picker
                v-model="closureWindow.range"
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
            <el-switch v-model="reviewWindow.application.teacher.enabled" size="small" :disabled="isReadOnly" />
            <el-date-picker
              v-model="reviewWindow.application.teacher.range"
              type="daterange"
              size="small"
              style="width: 200px; margin-top: 4px"
              value-format="YYYY-MM-DD"
              range-separator="-"
              :disabled="isReadOnly"
            />
          </div>
          <div class="col-role">
            <el-switch v-model="reviewWindow.application.level2.enabled" size="small" :disabled="isReadOnly" />
            <el-date-picker
              v-model="reviewWindow.application.level2.range"
              type="daterange"
              size="small"
              style="width: 200px; margin-top: 4px"
              value-format="YYYY-MM-DD"
              range-separator="-"
              :disabled="isReadOnly"
            />
          </div>
          <div class="col-role">
            <el-switch v-model="reviewWindow.application.level1.enabled" size="small" :disabled="isReadOnly" />
            <el-date-picker
              v-model="reviewWindow.application.level1.range"
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
            <el-switch v-model="reviewWindow.midterm.teacher.enabled" size="small" :disabled="isReadOnly" />
            <el-date-picker
              v-model="reviewWindow.midterm.teacher.range"
              type="daterange"
              size="small"
              style="width: 200px; margin-top: 4px"
              value-format="YYYY-MM-DD"
              range-separator="-"
              :disabled="isReadOnly"
            />
          </div>
          <div class="col-role">
            <el-switch v-model="reviewWindow.midterm.level2.enabled" size="small" :disabled="isReadOnly" />
            <el-date-picker
              v-model="reviewWindow.midterm.level2.range"
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
            <el-switch v-model="reviewWindow.closure.teacher.enabled" size="small" :disabled="isReadOnly" />
            <el-date-picker
              v-model="reviewWindow.closure.teacher.range"
              type="daterange"
              size="small"
              style="width: 200px; margin-top: 4px"
              value-format="YYYY-MM-DD"
              range-separator="-"
              :disabled="isReadOnly"
            />
          </div>
          <div class="col-role">
            <el-switch v-model="reviewWindow.closure.level2.enabled" size="small" :disabled="isReadOnly" />
            <el-date-picker
              v-model="reviewWindow.closure.level2.range"
              type="daterange"
              size="small"
              style="width: 200px; margin-top: 4px"
              value-format="YYYY-MM-DD"
              range-separator="-"
              :disabled="isReadOnly"
            />
          </div>
          <div class="col-role">
            <el-switch v-model="reviewWindow.closure.level1.enabled" size="small" :disabled="isReadOnly" />
            <el-date-picker
              v-model="reviewWindow.closure.level1.range"
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
import { computed } from "vue";

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

const emit = defineEmits<{
  (event: "update:globalDateRange", value: string[]): void;
}>();

const localGlobalDateRange = computed({
  get: () => props.globalDateRange,
  set: (value: string[]) => emit("update:globalDateRange", value),
});
</script>
