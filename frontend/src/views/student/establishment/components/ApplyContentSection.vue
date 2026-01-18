<template>
  <div class="form-section">
    <div class="section-header">
      <span class="section-title">申报内容</span>
    </div>
    <div class="form-container">
      <el-row :gutter="24">
        <el-col :span="24">
          <el-form-item label="预期成果" prop="expected_results">
            <el-select
              v-model="selectedAchievement"
              placeholder="请选择预期成果"
              class="expected-select"
              clearable
            >
              <el-option
                v-for="item in achievementTypeOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="24">
          <el-form-item label="项目简介" prop="description">
            <el-input
              v-model="localFormData.description"
              type="textarea"
              :rows="6"
              maxlength="500"
              show-word-limit
              placeholder="请简要介绍项目背景、创新点及研究内容"
            />
          </el-form-item>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, watch } from "vue";

type ExpectedRow = {
  achievement_type?: string;
  expected_count?: number;
};

type ContentFormData = {
  expected_results?: string;
  expected_results_data: ExpectedRow[];
  description?: string;
};

type OptionItem = {
  value: string;
  label: string;
};

const props = defineProps<{
  formData: ContentFormData;
  achievementTypeOptions: OptionItem[];
  getLabel: (options: OptionItem[], value: string) => string;
}>();

const emit = defineEmits<{
  (event: "update:formData", value: ContentFormData): void;
}>();

const localFormData = reactive<ContentFormData>({
  expected_results: "",
  expected_results_data: [],
  description: "",
});

const getAchievementLabel = (value: string) =>
  props.getLabel(props.achievementTypeOptions, value);

const selectedAchievement = computed({
  get: () => localFormData.expected_results_data?.[0]?.achievement_type || "",
  set: (value: string) => {
    if (!value) {
      localFormData.expected_results_data = [];
      localFormData.expected_results = "";
      return;
    }
    localFormData.expected_results_data = [
      { achievement_type: value, expected_count: 1 },
    ];
    localFormData.expected_results = getAchievementLabel(value);
  },
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

watch(
  () => localFormData.expected_results_data,
  (list) => {
    if (localFormData.expected_results || list.length === 0) return;
    const first = list[0]?.achievement_type || "";
    if (first) {
      localFormData.expected_results = getAchievementLabel(first);
    }
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

.expected-select {
  width: 100%;
}

:deep(.el-input__wrapper),
:deep(.el-textarea__inner) {
  box-shadow: 0 0 0 1px #e2e8f0 inset;
}

:deep(.el-input__wrapper:hover),
:deep(.el-textarea__inner:hover) {
  box-shadow: 0 0 0 1px #94a3b8 inset;
}

:deep(.el-input__wrapper.is-focus),
:deep(.el-textarea__inner:focus) {
  box-shadow: 0 0 0 1px #409eff inset;
}
</style>
