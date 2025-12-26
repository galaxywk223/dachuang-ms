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
  </el-form>
</template>

<script setup lang="ts">
import { computed } from "vue";

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
  collegeQuotaText: string;
  isProcessLocked: boolean;
}>();

const emit = defineEmits<{
  (event: "update:collegeQuotaText", value: string): void;
}>();

const localCollegeQuotaText = computed({
  get: () => props.collegeQuotaText,
  set: (value: string) => emit("update:collegeQuotaText", value),
});
</script>
