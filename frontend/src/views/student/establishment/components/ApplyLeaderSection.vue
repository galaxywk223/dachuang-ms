<template>
  <div class="form-section">
    <div class="section-header">
      <span class="section-title">负责人信息</span>
    </div>
    <div class="form-container">
      <el-row :gutter="24">
        <el-col :span="12">
          <el-form-item label="负责人姓名">
            <el-input
              :model-value="currentUser.name"
              disabled
              class="is-disabled-soft"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="负责人学号">
            <el-input
              :model-value="currentUser.student_id"
              disabled
              class="is-disabled-soft"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="联系电话" prop="leader_contact">
            <el-input
              v-model="localFormData.leader_contact"
              placeholder="手机号"
            />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="电子邮箱" prop="leader_email">
            <el-input v-model="localFormData.leader_email" placeholder="邮箱" />
          </el-form-item>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, watch } from "vue";

type LeaderFormData = {
  leader_contact?: string;
  leader_email?: string;
};

const props = defineProps<{
  formData: LeaderFormData;
  currentUser: { name: string; student_id: string };
}>();

const emit = defineEmits<{
  (event: "update:formData", value: LeaderFormData): void;
}>();

const localFormData = reactive<LeaderFormData>({
  leader_contact: "",
  leader_email: "",
});

watch(
  () => props.formData,
  (value) => {
    Object.assign(localFormData, value);
  },
  { immediate: true, deep: true }
);

watch(
  localFormData,
  (value) => {
    emit("update:formData", { ...value });
  },
  { deep: true }
);
</script>

<style scoped>
.form-container {
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 24px;
  transition: all 0.3s ease;
}

.form-container:hover {
  border-color: #cbd5e1;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

:deep(.el-input__wrapper) {
  box-shadow: 0 0 0 1px #e2e8f0 inset;
}
:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #94a3b8 inset;
}
:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #409eff inset;
}

.is-disabled-soft :deep(.el-input__wrapper) {
  background-color: #f1f5f9;
  box-shadow: none;
}
</style>
