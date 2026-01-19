<template>
  <div class="system-config-page">
    <el-card class="main-card" shadow="never">
      <template #header>
        <div class="custom-header">
          <div class="header-left">
            <span class="header-title">批次配置</span>
            <span v-if="batchTitle" class="batch-title ml-2">{{
              batchTitle
            }}</span>
            <el-tag
              v-if="batchStatusLabel"
              :type="batchStatusType"
              effect="plain"
              class="ml-2"
              size="small"
            >
              {{ batchStatusLabel }}
            </el-tag>
          </div>
          <div class="header-right">
            <el-button @click="goBack" class="mr-2">返回</el-button>
            <el-button
              type="primary"
              :loading="savingAll"
              :disabled="!batchId || isReadOnly"
              @click="saveAll"
            >
              保存全部
            </el-button>
          </div>
        </div>
      </template>

      <div v-if="!batchId" class="empty-wrap">
        <el-empty description="请从批次管理进入配置" />
      </div>
      <template v-else>
        <el-alert class="config-tip" type="info" :closable="false" show-icon>
          <template #default>
            当前配置仅对本批次生效；进行中仅允许调整日期窗口，已结束或归档为只读。
          </template>
        </el-alert>

        <el-tabs v-model="activeTab">
          <el-tab-pane label="时间窗口" name="dates">
            <SystemConfigDatesTab
              v-model:global-date-range="globalDateRange"
              :apply-batch-dates="applyBatchDates"
              :is-read-only="isReadOnly"
              :application-window="applicationWindow"
              :midterm-window="midtermWindow"
              :closure-window="closureWindow"
              @update:application-window="
                (value) => Object.assign(applicationWindow, value)
              "
              @update:midterm-window="
                (value) => Object.assign(midtermWindow, value)
              "
              @update:closure-window="
                (value) => Object.assign(closureWindow, value)
              "
            />
          </el-tab-pane>
          <el-tab-pane label="限制与校验" name="limits">
            <SystemConfigLimitsTab
              :limit-rules="limitRules"
              :validation-rules="validationRules"
              :is-process-locked="isProcessLocked"
              @update:limit-rules="(value) => Object.assign(limitRules, value)"
              @update:validation-rules="
                (value) => Object.assign(validationRules, value)
              "
            />
          </el-tab-pane>

          <el-tab-pane label="工作流配置" name="workflow">
            <BatchWorkflowConfig v-if="batchId" :batch-id="batchId" />
          </el-tab-pane>
        </el-tabs>
      </template>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, computed, watch } from "vue";
import { useRouter, useRoute } from "vue-router";
import { ElMessage } from "element-plus";
import {
  getEffectiveSettings,
  updateSettingByCode,
} from "@/api/system-settings";
import { getProjectBatch } from "@/api/system-settings/batches";
import SystemConfigDatesTab from "./components/SystemConfigDatesTab.vue";
import SystemConfigLimitsTab from "./components/SystemConfigLimitsTab.vue";
import BatchWorkflowConfig from "@/components/business/BatchWorkflowConfig.vue";

defineOptions({ name: "Level1SystemConfigView" });

type BatchInfo = {
  id: number;
  name?: string;
  year?: number;
  status?: string;
};

type SettingsPayload = {
  APPLICATION_WINDOW?: Record<string, unknown>;
  MIDTERM_WINDOW?: Record<string, unknown>;
  CLOSURE_WINDOW?: Record<string, unknown>;
  LIMIT_RULES?: Record<string, unknown>;
  PROCESS_RULES?: {
    allow_active_reapply?: boolean;
    show_material_in_closure_review?: boolean;
  };
  REVIEW_RULES?: Record<string, unknown>;
  VALIDATION_RULES?: Record<string, unknown>;
};

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null;

const getErrorMessage = (error: unknown, fallback: string) => {
  if (!isRecord(error)) return fallback;
  const response = error.response;
  if (
    isRecord(response) &&
    isRecord(response.data) &&
    typeof response.data.message === "string"
  ) {
    return response.data.message;
  }
  if (typeof error.message === "string") return error.message;
  return fallback;
};

const route = useRoute();
const router = useRouter();

const activeTab = ref("dates");
const savingAll = ref(false);
const batchInfo = ref<BatchInfo | null>(null);
const globalDateRange = ref([] as string[]);

const batchId = computed(() => {
  const raw = route.params.id || route.query.batch_id;
  if (!raw) return null;
  const value = Array.isArray(raw) ? raw[0] : raw;
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
});

const batchStatusOptions = [
  { value: "draft", label: "草稿" },
  { value: "active", label: "进行中" },
  { value: "finished", label: "已结束" },
  { value: "archived", label: "已归档" },
];

const getStatusLabel = (status?: string) => {
  const match = batchStatusOptions.find((item) => item.value === status);
  return match ? match.label : "未知";
};

const getStatusTagType = (status?: string) => {
  switch (status) {
    case "active":
      return "success";
    case "finished":
      return "info";
    case "archived":
      return "info";
    default:
      return "";
  }
};

const batchTitle = computed(() => {
  if (!batchInfo.value) return "";
  return `${batchInfo.value.name} (${batchInfo.value.year})`;
});

const batchStatusLabel = computed(() =>
  batchInfo.value ? getStatusLabel(batchInfo.value.status) : ""
);
const batchStatusType = computed(() =>
  getStatusTagType(batchInfo.value?.status)
);
const isArchived = computed(() => batchInfo.value?.status === "archived");
const isFinished = computed(() => batchInfo.value?.status === "finished");
const isActive = computed(() => batchInfo.value?.status === "active");
const isReadOnly = computed(() => isArchived.value || isFinished.value);
const isProcessLocked = computed(() => isReadOnly.value || isActive.value);

const applicationWindow = reactive({ enabled: false, range: [] as string[] });
const midtermWindow = reactive({ enabled: false, range: [] as string[] });
const closureWindow = reactive({ enabled: false, range: [] as string[] });

const limitRules = reactive({
  max_advisors: 2,
  max_members: 5,
  max_teacher_active: 5,
  max_student_active: 1,
  max_student_member: 1,
  dedupe_title: true,
});

const processRules = reactive({
  allow_active_reapply: false,
  show_material_in_closure_review: true,
});

const reviewRules = reactive({
  teacher_application_comment_min: 0,
});

const validationRules = reactive({
  title_min_length: 0,
  title_max_length: 200,
});

const goBack = () => {
  router.push({ name: "level1-settings-batches" });
};

const fillRange = (
  target: { range: string[] },
  data: { start?: string; end?: string }
) => {
  target.range = data.start && data.end ? [data.start, data.end] : [];
};

const applyBatchDates = () => {
  if (isReadOnly.value) return;
  if (!globalDateRange.value || globalDateRange.value.length !== 2) return;
  const range = [...globalDateRange.value];
  const applyRange = (target: { enabled: boolean; range: string[] }) => {
    target.enabled = true;
    target.range = [...range];
  };
  applyRange(applicationWindow);
  applyRange(midtermWindow);
  applyRange(closureWindow);
};


const loadBatch = async () => {
  if (!batchId.value) {
    batchInfo.value = null;
    return;
  }
  try {
    const res = await getProjectBatch(batchId.value);
    batchInfo.value = (
      isRecord(res) && "data" in res ? res.data : res
    ) as BatchInfo | null;
  } catch (error) {
    console.error(error);
    ElMessage.error(getErrorMessage(error, "加载批次失败"));
  }
};

const loadSettings = async () => {
  if (!batchId.value) return;
  try {
    const res = await getEffectiveSettings(batchId.value);
    const data = (
      isRecord(res) && "data" in res ? res.data : res
    ) as SettingsPayload;

    const app = (data.APPLICATION_WINDOW as Record<string, unknown>) || {};
    applicationWindow.enabled = !!app.enabled;
    fillRange(applicationWindow, app as { start?: string; end?: string });

    const mid = (data.MIDTERM_WINDOW as Record<string, unknown>) || {};
    midtermWindow.enabled = !!mid.enabled;
    fillRange(midtermWindow, mid as { start?: string; end?: string });

    const clo = (data.CLOSURE_WINDOW as Record<string, unknown>) || {};
    closureWindow.enabled = !!clo.enabled;
    fillRange(closureWindow, clo as { start?: string; end?: string });

    Object.assign(limitRules, data.LIMIT_RULES || {});
    processRules.allow_active_reapply = Boolean(
      data.PROCESS_RULES?.allow_active_reapply
    );
    processRules.show_material_in_closure_review = Boolean(
      data.PROCESS_RULES?.show_material_in_closure_review ?? true
    );
    Object.assign(reviewRules, data.REVIEW_RULES || {});
    Object.assign(validationRules, data.VALIDATION_RULES || {});
  } catch (error) {
    console.error(error);
    ElMessage.error(getErrorMessage(error, "加载配置失败"));
  }
};

const toWindowPayload = (source: { enabled: boolean; range: string[] }) => {
  return {
    enabled: source.enabled,
    start: source.range?.[0] || "",
    end: source.range?.[1] || "",
  };
};

const saveAll = async () => {
  if (!batchId.value) return;
  savingAll.value = true;
  try {
    const payloads = [
      updateSettingByCode(
        "APPLICATION_WINDOW",
        {
          name: "立项流程时间设置",
          data: toWindowPayload(applicationWindow),
        },
        batchId.value
      ),
      updateSettingByCode(
        "MIDTERM_WINDOW",
        {
          name: "中期流程时间设置",
          data: toWindowPayload(midtermWindow),
        },
        batchId.value
      ),
      updateSettingByCode(
        "CLOSURE_WINDOW",
        {
          name: "结题流程时间设置",
          data: toWindowPayload(closureWindow),
        },
        batchId.value
      ),
    ];

    if (!isProcessLocked.value) {
      payloads.push(
        updateSettingByCode(
          "LIMIT_RULES",
          {
            name: "限制与校验规则",
            data: { ...limitRules },
          },
          batchId.value
        ),
        updateSettingByCode(
          "PROCESS_RULES",
          {
            name: "流程规则配置",
            data: { ...processRules },
          },
          batchId.value
        ),
        updateSettingByCode(
          "REVIEW_RULES",
          {
            name: "审核规则配置",
            data: { ...reviewRules },
          },
          batchId.value
        ),
        updateSettingByCode(
          "VALIDATION_RULES",
          {
            name: "校验规则配置",
            data: {
              ...validationRules,
            },
          },
          batchId.value
        )
      );
    }

    await Promise.all(payloads);
    ElMessage.success("保存成功");
    goBack();
  } catch (error) {
    console.error(error);
    ElMessage.error(getErrorMessage(error, "保存失败"));
  } finally {
    savingAll.value = false;
  }
};
watch(
  () => batchId.value,
  async (id) => {
    if (!id) return;
    await loadBatch();
    await loadSettings();
  },
  { immediate: true }
);
</script>

<style scoped lang="scss">
@use "./SystemConfig.scss";
</style>
