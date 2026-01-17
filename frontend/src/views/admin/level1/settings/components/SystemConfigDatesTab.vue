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
      <span class="tip ml-2 text-gray text-xs"
        >注：将批量设置下方所有时间段</span
      >
    </div>

    <div class="section-block">
      <div class="block-title">流程时间窗口</div>
      <el-row :gutter="24">
        <el-col :span="8">
          <el-card shadow="never" class="sub-card">
            <template #header
              ><span class="sub-title">立项流程</span></template
            >
            <div class="card-body">
              <div class="flex-row">
                <el-switch
                  v-model="localApplicationWindow.enabled"
                  active-text="开启"
                  :disabled="isReadOnly"
                />
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
        <el-col :span="8">
          <el-card shadow="never" class="sub-card">
            <template #header
              ><span class="sub-title">中期流程</span></template
            >
            <div class="card-body">
              <div class="flex-row">
                <el-switch
                  v-model="localMidtermWindow.enabled"
                  active-text="开启"
                  :disabled="isReadOnly"
                />
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
        <el-col :span="8">
          <el-card shadow="never" class="sub-card">
            <template #header
              ><span class="sub-title">结题流程</span></template
            >
            <div class="card-body">
              <div class="flex-row">
                <el-switch
                  v-model="localClosureWindow.enabled"
                  active-text="开启"
                  :disabled="isReadOnly"
                />
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
}>();

type WindowConfig = { enabled: boolean; range: string[] };

const emit = defineEmits<{
  (event: "update:globalDateRange", value: string[]): void;
  (event: "update:applicationWindow", value: WindowConfig): void;
  (event: "update:midtermWindow", value: WindowConfig): void;
  (event: "update:closureWindow", value: WindowConfig): void;
}>();

const localGlobalDateRange = computed({
  get: () => props.globalDateRange,
  set: (value: string[]) => emit("update:globalDateRange", value),
});

const cloneWindow = (source: WindowConfig): WindowConfig => ({
  enabled: source.enabled,
  range: [...source.range],
});

const localApplicationWindow = reactive(cloneWindow(props.applicationWindow));
const localMidtermWindow = reactive(cloneWindow(props.midtermWindow));
const localClosureWindow = reactive(cloneWindow(props.closureWindow));

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
  localApplicationWindow,
  (value) =>
    emit("update:applicationWindow", {
      enabled: value.enabled,
      range: value.range,
    }),
  { deep: true }
);
watch(
  localMidtermWindow,
  (value) =>
    emit("update:midtermWindow", {
      enabled: value.enabled,
      range: value.range,
    }),
  { deep: true }
);
watch(
  localClosureWindow,
  (value) =>
    emit("update:closureWindow", {
      enabled: value.enabled,
      range: value.range,
    }),
  { deep: true }
);
</script>
<style scoped lang="scss">
.config-form {
  max-width: 100%;
  padding-top: 10px;
}

.batch-opt-bar {
  background-color: #f8fafc;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 24px;

  .label {
    font-weight: 600;
    color: #334155;
  }

  .tip {
    color: #64748b;
    font-size: 13px;
    margin-left: auto;
  }
}

.section-block {
  margin-bottom: 32px;
}

.block-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 16px;
  padding-left: 12px;
  border-left: 4px solid #3b82f6;
  line-height: 1.2;
}

.sub-card {
  height: 100%;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  transition: all 0.2s;

  &:hover {
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
      0 2px 4px -1px rgba(0, 0, 0, 0.06);
  }

  :deep(.el-card__header) {
    padding: 12px 16px;
    background-color: #f8fafc;
    border-bottom: 1px solid #e2e8f0;
  }

  .sub-title {
    font-weight: 600;
    color: #334155;
    font-size: 14px;
  }

  .card-body {
    padding: 0;
  }

  .flex-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
  }
}

.text-gray {
  color: #94a3b8;
}

.text-xs {
  font-size: 12px;
}

.mr-2 {
  margin-right: 8px;
}
</style>
