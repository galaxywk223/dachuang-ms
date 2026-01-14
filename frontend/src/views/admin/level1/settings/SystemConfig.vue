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
          <el-tab-pane label="限制与校验" name="limits">
            <SystemConfigLimitsTab
              :limit-rules="limitRules"
              :validation-rules="validationRules"
              v-model:college-quota-text="collegeQuotaText"
              v-model:allowed-types-by-college-text="allowedTypesByCollegeText"
              v-model:allowed-levels-by-college-text="
                allowedLevelsByCollegeText
              "
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
          <el-tab-pane label="管理员分配" name="admin-assignments">
            <BatchAdminAssignmentConfig v-if="batchId" :batch-id="batchId" />
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
import SystemConfigLimitsTab from "./components/SystemConfigLimitsTab.vue";
import BatchWorkflowConfig from "@/components/business/BatchWorkflowConfig.vue";
import BatchAdminAssignmentConfig from "@/components/business/BatchAdminAssignmentConfig.vue";

defineOptions({ name: "Level1SystemConfigView" });

type BatchInfo = {
  id: number;
  name?: string;
  year?: number;
  status?: string;
};

type SettingsPayload = Record<string, unknown>;

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
const expertReviewWindow = reactive({ enabled: false, range: [] as string[] });

const reviewWindow = reactive({
  application: {
    teacher: { enabled: false, range: [] as string[] },
    level2: { enabled: false, range: [] as string[] },
    level1: { enabled: false, range: [] as string[] },
  },
  midterm: {
    teacher: { enabled: false, range: [] as string[] },
    level2: { enabled: false, range: [] as string[] },
  },
  closure: {
    teacher: { enabled: false, range: [] as string[] },
    level2: { enabled: false, range: [] as string[] },
    level1: { enabled: false, range: [] as string[] },
  },
});

const limitRules = reactive({
  max_advisors: 2,
  max_members: 5,
  max_teacher_active: 5,
  max_student_active: 1,
  max_student_member: 1,
  teacher_excellent_bonus: 0,
  dedupe_title: true,
  advisor_title_required: false,
  college_quota: {} as Record<string, number>,
});

const processRules = reactive({
  allow_active_reapply: false,
  reject_to_previous: false,
  show_material_in_closure_review: true,
});

const reviewRules = reactive({
  teacher_application_comment_min: 0,
});

const collegeQuotaText = ref("{}");
const allowedTypesByCollegeText = ref("{}");
const allowedLevelsByCollegeText = ref("{}");

const validationRules = reactive({
  title_regex: "",
  title_min_length: 0,
  title_max_length: 200,
  allowed_project_types: [] as string[],
  allowed_project_types_by_college: {} as Record<string, string[]>,
  allowed_levels_by_college: {} as Record<string, string[]>,
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

const getWindowSegment = (source: Record<string, unknown>, key: string) => {
  const segment = source[key];
  return isRecord(segment)
    ? (segment as { enabled?: boolean; start?: string; end?: string })
    : {};
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

    const expert = (data.EXPERT_REVIEW_WINDOW as Record<string, unknown>) || {};
    expertReviewWindow.enabled = !!expert.enabled;
    fillRange(expertReviewWindow, expert as { start?: string; end?: string });

    const review = (data.REVIEW_WINDOW as Record<string, unknown>) || {};
    const appReview = (review.application as Record<string, unknown>) || {};
    const midReview = (review.midterm as Record<string, unknown>) || {};
    const cloReview = (review.closure as Record<string, unknown>) || {};

    const appTeacher = getWindowSegment(appReview, "teacher");
    const appLevel2 = getWindowSegment(appReview, "level2");
    const appLevel1 = getWindowSegment(appReview, "level1");
    reviewWindow.application.teacher.enabled = !!appTeacher.enabled;
    fillRange(reviewWindow.application.teacher, appTeacher);
    reviewWindow.application.level2.enabled = !!appLevel2.enabled;
    fillRange(reviewWindow.application.level2, appLevel2);
    reviewWindow.application.level1.enabled = !!appLevel1.enabled;
    fillRange(reviewWindow.application.level1, appLevel1);

    const midTeacher = getWindowSegment(midReview, "teacher");
    const midLevel2 = getWindowSegment(midReview, "level2");
    reviewWindow.midterm.teacher.enabled = !!midTeacher.enabled;
    fillRange(reviewWindow.midterm.teacher, midTeacher);
    reviewWindow.midterm.level2.enabled = !!midLevel2.enabled;
    fillRange(reviewWindow.midterm.level2, midLevel2);

    const cloTeacher = getWindowSegment(cloReview, "teacher");
    const cloLevel2 = getWindowSegment(cloReview, "level2");
    const cloLevel1 = getWindowSegment(cloReview, "level1");
    reviewWindow.closure.teacher.enabled = !!cloTeacher.enabled;
    fillRange(reviewWindow.closure.teacher, cloTeacher);
    reviewWindow.closure.level2.enabled = !!cloLevel2.enabled;
    fillRange(reviewWindow.closure.level2, cloLevel2);
    reviewWindow.closure.level1.enabled = !!cloLevel1.enabled;
    fillRange(reviewWindow.closure.level1, cloLevel1);

    Object.assign(limitRules, data.LIMIT_RULES || {});
    collegeQuotaText.value = JSON.stringify(
      limitRules.college_quota || {},
      null,
      2
    );

    Object.assign(processRules, data.PROCESS_RULES || {});
    Object.assign(reviewRules, data.REVIEW_RULES || {});
    Object.assign(validationRules, data.VALIDATION_RULES || {});
    allowedTypesByCollegeText.value = JSON.stringify(
      validationRules.allowed_project_types_by_college || {},
      null,
      2
    );
    allowedLevelsByCollegeText.value = JSON.stringify(
      validationRules.allowed_levels_by_college || {},
      null,
      2
    );
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

const buildReviewWindowPayload = () => {
  return {
    application: {
      teacher: toWindowPayload(reviewWindow.application.teacher),
      level2: toWindowPayload(reviewWindow.application.level2),
      level1: toWindowPayload(reviewWindow.application.level1),
    },
    midterm: {
      teacher: toWindowPayload(reviewWindow.midterm.teacher),
      level2: toWindowPayload(reviewWindow.midterm.level2),
    },
    closure: {
      teacher: toWindowPayload(reviewWindow.closure.teacher),
      level2: toWindowPayload(reviewWindow.closure.level2),
      level1: toWindowPayload(reviewWindow.closure.level1),
    },
  };
};

const saveAll = async () => {
  if (!batchId.value) return;
  savingAll.value = true;
  try {
    let quota = {};
    try {
      quota = JSON.parse(collegeQuotaText.value || "{}");
    } catch {
      ElMessage.error("学院名额配置不是有效的JSON");
      return;
    }
    let allowedTypesByCollege = {};
    let allowedLevelsByCollege = {};
    try {
      allowedTypesByCollege = JSON.parse(
        allowedTypesByCollegeText.value || "{}"
      );
      allowedLevelsByCollege = JSON.parse(
        allowedLevelsByCollegeText.value || "{}"
      );
    } catch {
      ElMessage.error("项目类型/级别限制配置不是有效的JSON");
      return;
    }

    const payloads = [
      updateSettingByCode(
        "APPLICATION_WINDOW",
        {
          name: "项目申报时间设置",
          data: toWindowPayload(applicationWindow),
        },
        batchId.value
      ),
      updateSettingByCode(
        "MIDTERM_WINDOW",
        {
          name: "中期提交时间设置",
          data: toWindowPayload(midtermWindow),
        },
        batchId.value
      ),
      updateSettingByCode(
        "CLOSURE_WINDOW",
        {
          name: "结题提交时间设置",
          data: toWindowPayload(closureWindow),
        },
        batchId.value
      ),
      updateSettingByCode(
        "EXPERT_REVIEW_WINDOW",
        {
          name: "专家评审时间设置",
          data: toWindowPayload(expertReviewWindow),
        },
        batchId.value
      ),
      updateSettingByCode(
        "REVIEW_WINDOW",
        {
          name: "审核时间设置",
          data: buildReviewWindowPayload(),
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
            data: { ...limitRules, college_quota: quota },
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
              allowed_project_types_by_college: allowedTypesByCollege,
              allowed_levels_by_college: allowedLevelsByCollege,
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
