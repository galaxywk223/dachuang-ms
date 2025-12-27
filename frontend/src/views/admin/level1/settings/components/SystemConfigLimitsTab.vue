<template>
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
      <el-input-number
        v-model="limitRules.teacher_excellent_bonus"
        :min="0"
        :disabled="isProcessLocked"
      />
    </el-form-item>
    <el-form-item label="项目名称查重">
      <el-switch v-model="limitRules.dedupe_title" :disabled="isProcessLocked" />
    </el-form-item>
    <el-form-item label="指导教师职称必填">
      <el-switch v-model="limitRules.advisor_title_required" :disabled="isProcessLocked" />
    </el-form-item>
    <el-form-item label="学院名额配置(JSON)">
      <el-input
        v-model="localCollegeQuotaText"
        type="textarea"
        :rows="4"
        placeholder='{"CS": 30, "EE": 20}'
        :disabled="isProcessLocked"
      />
    </el-form-item>

    <el-divider content-position="left">校验规则</el-divider>

    <el-form-item label="项目名称最小长度">
      <el-input-number
        v-model="validationRules.title_min_length"
        :min="0"
        :disabled="isProcessLocked"
      />
    </el-form-item>
    <el-form-item label="项目名称最大长度">
      <el-input-number
        v-model="validationRules.title_max_length"
        :min="0"
        :disabled="isProcessLocked"
      />
    </el-form-item>
    <el-form-item label="项目名称正则">
      <el-input
        v-model="validationRules.title_regex"
        placeholder="例如: ^[\\u4e00-\\u9fa5A-Za-z0-9]+$"
        :disabled="isProcessLocked"
      />
    </el-form-item>
    <el-form-item label="学科分类必填">
      <el-switch v-model="validationRules.discipline_required" :disabled="isProcessLocked" />
    </el-form-item>
    <el-form-item label="允许项目类别(逗号分隔)">
      <el-input
        v-model="allowedTypesText"
        placeholder="如: NATIONAL,PROVINCIAL"
        :disabled="isProcessLocked"
      />
      <div class="form-hint">留空表示不限制</div>
    </el-form-item>
    <el-form-item label="学院允许项目类别(JSON)">
      <el-input
        v-model="localAllowedTypesByCollegeText"
        type="textarea"
        :rows="4"
        placeholder='{"CS": ["NATIONAL","PROVINCIAL"]}'
        :disabled="isProcessLocked"
      />
    </el-form-item>
    <el-form-item label="学院允许项目级别(JSON)">
      <el-input
        v-model="localAllowedLevelsByCollegeText"
        type="textarea"
        :rows="4"
        placeholder='{"CS": ["KEY","GENERAL"]}'
        :disabled="isProcessLocked"
      />
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { computed, watch } from "vue";

const props = defineProps<{
  limitRules: {
    max_advisors: number;
    max_members: number;
    max_teacher_active: number;
    max_student_active: number;
    max_student_member: number;
    teacher_excellent_bonus: number;
    dedupe_title: boolean;
    advisor_title_required: boolean;
    college_quota: Record<string, number>;
  };
  validationRules: {
    title_regex: string;
    title_min_length: number;
    title_max_length: number;
    allowed_project_types: string[];
    allowed_project_types_by_college: Record<string, string[]>;
    allowed_levels_by_college: Record<string, string[]>;
    discipline_required: boolean;
  };
  collegeQuotaText: string;
  allowedTypesByCollegeText: string;
  allowedLevelsByCollegeText: string;
  isProcessLocked: boolean;
}>();

const emit = defineEmits<{
  (event: "update:collegeQuotaText", value: string): void;
  (event: "update:allowedTypesByCollegeText", value: string): void;
  (event: "update:allowedLevelsByCollegeText", value: string): void;
}>();

const localCollegeQuotaText = computed({
  get: () => props.collegeQuotaText,
  set: (value: string) => emit("update:collegeQuotaText", value),
});

const localAllowedTypesByCollegeText = computed({
  get: () => props.allowedTypesByCollegeText,
  set: (value: string) => emit("update:allowedTypesByCollegeText", value),
});

const localAllowedLevelsByCollegeText = computed({
  get: () => props.allowedLevelsByCollegeText,
  set: (value: string) => emit("update:allowedLevelsByCollegeText", value),
});

const allowedTypesText = computed({
  get: () => (props.validationRules.allowed_project_types || []).join(","),
  set: (value: string) => {
    const list = value_toggle(value);
    props.validationRules.allowed_project_types = list;
  },
});

const value_toggle = (value: string) => {
  if (!value) return [];
  return value
    .split(",")
    .map((v) => v.trim())
    .filter((v) => v);
};

watch(
  () => props.validationRules.allowed_project_types,
  (val) => {
    if (!val || !Array.isArray(val)) {
      props.validationRules.allowed_project_types = [];
    }
  }
);
</script>
