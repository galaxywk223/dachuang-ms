<template>
  <el-form label-position="top" class="config-form grid-form">
    <el-form-item label="指导教师最大数量">
      <el-input-number
        v-model="localLimitRules.max_advisors"
        :min="0"
        :disabled="isProcessLocked"
      />
    </el-form-item>
    <el-form-item label="项目成员最大数量">
      <el-input-number
        v-model="localLimitRules.max_members"
        :min="0"
        :disabled="isProcessLocked"
      />
    </el-form-item>
    <el-form-item label="导师在研项目上限">
      <el-input-number
        v-model="localLimitRules.max_teacher_active"
        :min="0"
        :disabled="isProcessLocked"
      />
    </el-form-item>
    <el-form-item label="学生作为负责人上限">
      <el-input-number
        v-model="localLimitRules.max_student_active"
        :min="0"
        :disabled="isProcessLocked"
      />
    </el-form-item>
    <el-form-item label="学生作为成员上限">
      <el-input-number
        v-model="localLimitRules.max_student_member"
        :min="0"
        :disabled="isProcessLocked"
      />
    </el-form-item>
    <el-form-item label="项目名称查重">
      <el-switch
        v-model="localLimitRules.dedupe_title"
        :disabled="isProcessLocked"
      />
    </el-form-item>
    <el-form-item label="项目名称最小长度">
      <el-input-number
        v-model="localValidationRules.title_min_length"
        :min="0"
        :disabled="isProcessLocked"
      />
    </el-form-item>
    <el-form-item label="项目名称最大长度">
      <el-input-number
        v-model="localValidationRules.title_max_length"
        :min="0"
        :disabled="isProcessLocked"
      />
    </el-form-item>
  </el-form>
</template>

<script setup lang="ts">
import { reactive, watch } from "vue";

const props = defineProps<{
  limitRules: {
    max_advisors: number;
    max_members: number;
    max_teacher_active: number;
    max_student_active: number;
    max_student_member: number;
    dedupe_title: boolean;
  };
  validationRules: {
    title_min_length: number;
    title_max_length: number;
  };
  isProcessLocked: boolean;
}>();

const emit = defineEmits<{
  (event: "update:limitRules", value: typeof props.limitRules): void;
  (event: "update:validationRules", value: typeof props.validationRules): void;
}>();

const localLimitRules = reactive({ ...props.limitRules });
const localValidationRules = reactive({ ...props.validationRules });

watch(
  () => props.validationRules,
  (val) => {
    Object.assign(localValidationRules, val);
  },
  { deep: true }
);

watch(
  () => props.limitRules,
  (val) => {
    Object.assign(localLimitRules, val);
  },
  { deep: true }
);

watch(
  localLimitRules,
  (val) => {
    emit("update:limitRules", { ...val });
  },
  { deep: true }
);

watch(
  localValidationRules,
  (val) => {
    emit("update:validationRules", { ...val });
  },
  { deep: true }
);
</script>
<style scoped lang="scss">
.config-form {
  max-width: 800px;
  padding-top: 20px;
}

.grid-form {
  display: grid;
  grid-template-columns: repeat(2, minmax(240px, 1fr));
  gap: 16px 24px;

  :deep(.el-form-item) {
    margin-bottom: 0;
  }
}

@media (max-width: 900px) {
  .grid-form {
    grid-template-columns: minmax(0, 1fr);
  }
}

.form-hint {
  font-size: 12px;
  color: #94a3b8;
  line-height: 1.4;
  margin-top: 4px;
}
</style>
