<template>
  <div class="system-config-page">
    <el-card class="config-card">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-button link @click="goBack">返回批次管理</el-button>
            <span class="title">批次配置</span>
            <span v-if="batchTitle" class="batch-title">{{ batchTitle }}</span>
            <el-tag v-if="batchStatusLabel" :type="batchStatusType" effect="light">
              状态：{{ batchStatusLabel }}
            </el-tag>
          </div>
          <el-button
            type="primary"
            :loading="savingAll"
            :disabled="!batchId || isReadOnly"
            @click="saveAll"
          >
            保存全部
          </el-button>
        </div>
      </template>

      <div v-if="!batchId" class="empty-wrap">
        <el-empty description="请从批次管理进入配置" />
      </div>
      <template v-else>
        <el-alert class="config-tip" type="info" :closable="false" show-icon>
          <template #default>
            当前配置仅对本批次生效；进行中/评审中仅允许调整日期窗口，已结束或归档为只读。
          </template>
        </el-alert>

        <el-tabs v-model="activeTab">
          <el-tab-pane label="日期配置" name="dates">
            <el-form label-width="160px" class="config-form">
              <el-divider content-position="left">申报/中期/结题提交时间</el-divider>
              <el-form-item label="项目申报时间">
                <el-switch v-model="applicationWindow.enabled" class="mr-2" :disabled="isReadOnly" />
                <el-date-picker
                  v-model="applicationWindow.range"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="截止日期"
                  value-format="YYYY-MM-DD"
                  :disabled="isReadOnly"
                />
                <div class="form-hint">开启后该批次仅在所选时间范围内允许申报。</div>
              </el-form-item>

              <el-form-item label="中期提交时间">
                <el-switch v-model="midtermWindow.enabled" class="mr-2" :disabled="isReadOnly" />
                <el-date-picker
                  v-model="midtermWindow.range"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="截止日期"
                  value-format="YYYY-MM-DD"
                  :disabled="isReadOnly"
                />
                <div class="form-hint">开启后该批次仅在所选时间范围内允许提交中期。</div>
              </el-form-item>

              <el-form-item label="结题提交时间">
                <el-switch v-model="closureWindow.enabled" class="mr-2" :disabled="isReadOnly" />
                <el-date-picker
                  v-model="closureWindow.range"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="截止日期"
                  value-format="YYYY-MM-DD"
                  :disabled="isReadOnly"
                />
                <div class="form-hint">开启后该批次仅在所选时间范围内允许提交结题。</div>
              </el-form-item>

              <el-divider content-position="left">专家评审时间</el-divider>
              <el-form-item label="专家评审时间">
                <el-switch v-model="expertReviewWindow.enabled" class="mr-2" :disabled="isReadOnly" />
                <el-date-picker
                  v-model="expertReviewWindow.range"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="截止日期"
                  value-format="YYYY-MM-DD"
                  :disabled="isReadOnly"
                />
                <div class="form-hint">开启后仅在该时间段允许专家组评审。</div>
              </el-form-item>

              <el-divider content-position="left">各角色审核时间</el-divider>
              <el-divider content-position="left">申报审核</el-divider>
              <el-form-item label="导师审核时间">
                <el-switch v-model="reviewWindow.application.teacher.enabled" class="mr-2" :disabled="isReadOnly" />
                <el-date-picker
                  v-model="reviewWindow.application.teacher.range"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="截止日期"
                  value-format="YYYY-MM-DD"
                  :disabled="isReadOnly"
                />
                <div class="form-hint">开启后仅在该时间段允许导师审核申报。</div>
              </el-form-item>
              <el-form-item label="学院审核时间">
                <el-switch v-model="reviewWindow.application.level2.enabled" class="mr-2" :disabled="isReadOnly" />
                <el-date-picker
                  v-model="reviewWindow.application.level2.range"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="截止日期"
                  value-format="YYYY-MM-DD"
                  :disabled="isReadOnly"
                />
                <div class="form-hint">开启后仅在该时间段允许学院审核申报。</div>
              </el-form-item>
              <el-form-item label="校级审核时间">
                <el-switch v-model="reviewWindow.application.level1.enabled" class="mr-2" :disabled="isReadOnly" />
                <el-date-picker
                  v-model="reviewWindow.application.level1.range"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="截止日期"
                  value-format="YYYY-MM-DD"
                  :disabled="isReadOnly"
                />
                <div class="form-hint">开启后仅在该时间段允许校级审核申报。</div>
              </el-form-item>

              <el-divider content-position="left">中期审核</el-divider>
              <el-form-item label="导师审核时间">
                <el-switch v-model="reviewWindow.midterm.teacher.enabled" class="mr-2" :disabled="isReadOnly" />
                <el-date-picker
                  v-model="reviewWindow.midterm.teacher.range"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="截止日期"
                  value-format="YYYY-MM-DD"
                  :disabled="isReadOnly"
                />
                <div class="form-hint">开启后仅在该时间段允许导师审核中期。</div>
              </el-form-item>
              <el-form-item label="学院审核时间">
                <el-switch v-model="reviewWindow.midterm.level2.enabled" class="mr-2" :disabled="isReadOnly" />
                <el-date-picker
                  v-model="reviewWindow.midterm.level2.range"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="截止日期"
                  value-format="YYYY-MM-DD"
                  :disabled="isReadOnly"
                />
                <div class="form-hint">开启后仅在该时间段允许学院审核中期。</div>
              </el-form-item>

              <el-divider content-position="left">结题审核</el-divider>
              <el-form-item label="导师审核时间">
                <el-switch v-model="reviewWindow.closure.teacher.enabled" class="mr-2" :disabled="isReadOnly" />
                <el-date-picker
                  v-model="reviewWindow.closure.teacher.range"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="截止日期"
                  value-format="YYYY-MM-DD"
                  :disabled="isReadOnly"
                />
                <div class="form-hint">开启后仅在该时间段允许导师审核结题。</div>
              </el-form-item>
              <el-form-item label="学院审核时间">
                <el-switch v-model="reviewWindow.closure.level2.enabled" class="mr-2" :disabled="isReadOnly" />
                <el-date-picker
                  v-model="reviewWindow.closure.level2.range"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="截止日期"
                  value-format="YYYY-MM-DD"
                  :disabled="isReadOnly"
                />
                <div class="form-hint">开启后仅在该时间段允许学院审核结题。</div>
              </el-form-item>
              <el-form-item label="校级审核时间">
                <el-switch v-model="reviewWindow.closure.level1.enabled" class="mr-2" :disabled="isReadOnly" />
                <el-date-picker
                  v-model="reviewWindow.closure.level1.range"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="截止日期"
                  value-format="YYYY-MM-DD"
                  :disabled="isReadOnly"
                />
                <div class="form-hint">开启后仅在该时间段允许校级审核结题。</div>
              </el-form-item>
            </el-form>
          </el-tab-pane>

          <el-tab-pane label="限制与校验" name="limits">
            <el-form label-width="200px" class="config-form">
              <el-form-item label="指导教师最大数量">
                <el-input-number v-model="limitRules.max_advisors" :min="0" :disabled="isProcessLocked" />
              </el-form-item>
              <el-form-item label="项目成员最大数量">
                <el-input-number v-model="limitRules.max_members" :min="0" :disabled="isProcessLocked" />
              </el-form-item>
              <el-form-item label="导师在研项目上限">
                <el-input-number v-model="limitRules.max_teacher_active" :min="0" :disabled="isProcessLocked" />
              </el-form-item>
              <el-form-item label="学生作为负责人上限">
                <el-input-number v-model="limitRules.max_student_active" :min="0" :disabled="isProcessLocked" />
              </el-form-item>
              <el-form-item label="学生作为成员上限">
                <el-input-number v-model="limitRules.max_student_member" :min="0" :disabled="isProcessLocked" />
              </el-form-item>
              <el-form-item label="优秀结题加成数">
                <el-input-number v-model="limitRules.teacher_excellent_bonus" :min="0" :disabled="isProcessLocked" />
              </el-form-item>
              <el-form-item label="项目名称查重">
                <el-switch v-model="limitRules.dedupe_title" :disabled="isProcessLocked" />
              </el-form-item>
              <el-form-item label="指导教师职称必填">
                <el-switch v-model="limitRules.advisor_title_required" :disabled="isProcessLocked" />
              </el-form-item>
              <el-form-item label="学院名额配置(JSON)">
                <el-input
                  v-model="collegeQuotaText"
                  type="textarea"
                  :rows="4"
                  placeholder='{"CS": 30, "EE": 20}'
                  :disabled="isProcessLocked"
                />
              </el-form-item>
            </el-form>
          </el-tab-pane>

          <el-tab-pane label="流程配置" name="process">
            <el-form label-width="200px" class="config-form">
              <el-form-item label="在研项目允许继续申报">
                <el-switch v-model="processRules.allow_active_reapply" :disabled="isProcessLocked" />
                <div class="form-hint">开启后，已有在研项目的学生仍可提交新申报。</div>
              </el-form-item>
              <el-form-item label="审核退回上一级">
                <el-switch v-model="processRules.reject_to_previous" :disabled="isProcessLocked" />
                <div class="form-hint">开启后，退回会返回到上一级角色重新审核。</div>
              </el-form-item>
              <el-form-item label="结题评审可见立项材料">
                <el-switch v-model="processRules.show_material_in_closure_review" :disabled="isProcessLocked" />
                <div class="form-hint">开启后，结题评审可查看立项阶段材料。</div>
              </el-form-item>
              <el-form-item label="导师审核意见最少字数">
                <el-input-number v-model="reviewRules.teacher_application_comment_min" :min="0" :disabled="isProcessLocked" />
                <div class="form-hint">设置为 0 表示不限制字数。</div>
              </el-form-item>
            </el-form>
          </el-tab-pane>
        </el-tabs>
      </template>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, computed, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { getEffectiveSettings, updateSettingByCode } from "@/api/system-settings";
import { getProjectBatch } from "@/api/project-batches";

const route = useRoute();
const router = useRouter();

const activeTab = ref("dates");
const savingAll = ref(false);
const batchInfo = ref<any | null>(null);

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
  { value: "reviewing", label: "评审中" },
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
    case "reviewing":
      return "warning";
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
const batchStatusType = computed(() => getStatusTagType(batchInfo.value?.status));
const isArchived = computed(() => batchInfo.value?.status === "archived");
const isFinished = computed(() => batchInfo.value?.status === "finished");
const isActive = computed(() => batchInfo.value?.status === "active");
const isReviewing = computed(() => batchInfo.value?.status === "reviewing");
const isReadOnly = computed(() => isArchived.value || isFinished.value);
const isProcessLocked = computed(() => isReadOnly.value || isActive.value || isReviewing.value);

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

const goBack = () => {
  router.push({ name: "level1-settings-batches" });
};

const fillRange = (target: { range: string[] }, data: any) => {
  target.range = data.start && data.end ? [data.start, data.end] : [];
};

const loadBatch = async () => {
  if (!batchId.value) {
    batchInfo.value = null;
    return;
  }
  try {
    const res: any = await getProjectBatch(batchId.value);
    batchInfo.value = res.data || res;
  } catch (error) {
    console.error(error);
    ElMessage.error("加载批次失败");
  }
};

const loadSettings = async () => {
  if (!batchId.value) return;
  try {
    const res: any = await getEffectiveSettings(batchId.value);
    const data = res.data || res;

    const app = data.APPLICATION_WINDOW || {};
    applicationWindow.enabled = !!app.enabled;
    fillRange(applicationWindow, app);

    const mid = data.MIDTERM_WINDOW || {};
    midtermWindow.enabled = !!mid.enabled;
    fillRange(midtermWindow, mid);

    const clo = data.CLOSURE_WINDOW || {};
    closureWindow.enabled = !!clo.enabled;
    fillRange(closureWindow, clo);

    const expert = data.EXPERT_REVIEW_WINDOW || {};
    expertReviewWindow.enabled = !!expert.enabled;
    fillRange(expertReviewWindow, expert);

    const review = data.REVIEW_WINDOW || {};
    const appReview = review.application || {};
    const midReview = review.midterm || {};
    const cloReview = review.closure || {};

    reviewWindow.application.teacher.enabled = !!appReview.teacher?.enabled;
    fillRange(reviewWindow.application.teacher, appReview.teacher || {});
    reviewWindow.application.level2.enabled = !!appReview.level2?.enabled;
    fillRange(reviewWindow.application.level2, appReview.level2 || {});
    reviewWindow.application.level1.enabled = !!appReview.level1?.enabled;
    fillRange(reviewWindow.application.level1, appReview.level1 || {});

    reviewWindow.midterm.teacher.enabled = !!midReview.teacher?.enabled;
    fillRange(reviewWindow.midterm.teacher, midReview.teacher || {});
    reviewWindow.midterm.level2.enabled = !!midReview.level2?.enabled;
    fillRange(reviewWindow.midterm.level2, midReview.level2 || {});

    reviewWindow.closure.teacher.enabled = !!cloReview.teacher?.enabled;
    fillRange(reviewWindow.closure.teacher, cloReview.teacher || {});
    reviewWindow.closure.level2.enabled = !!cloReview.level2?.enabled;
    fillRange(reviewWindow.closure.level2, cloReview.level2 || {});
    reviewWindow.closure.level1.enabled = !!cloReview.level1?.enabled;
    fillRange(reviewWindow.closure.level1, cloReview.level1 || {});

    Object.assign(limitRules, data.LIMIT_RULES || {});
    collegeQuotaText.value = JSON.stringify(limitRules.college_quota || {}, null, 2);

    Object.assign(processRules, data.PROCESS_RULES || {});
    Object.assign(reviewRules, data.REVIEW_RULES || {});
  } catch (error) {
    console.error(error);
    ElMessage.error("加载配置失败");
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
        )
      );
    }

    await Promise.all(payloads);
    ElMessage.success("保存成功");
    await loadSettings();
  } catch (error) {
    console.error(error);
    ElMessage.error("保存失败");
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

<style scoped>
.system-config-page {
  padding: 20px;
}
.config-card {
  border-radius: 10px;
}
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}
.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}
.title {
  font-size: 16px;
  font-weight: 600;
}
.batch-title {
  color: #475569;
  font-size: 13px;
}
.config-form {
  max-width: 880px;
}
.mr-2 {
  margin-right: 8px;
}
.config-tip {
  margin-bottom: 16px;
}
.form-hint {
  margin-top: 6px;
  color: #6b7280;
  font-size: 12px;
}
.empty-wrap {
  padding: 24px 0;
}
</style>
