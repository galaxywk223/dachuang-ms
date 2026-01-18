<template>
  <div class="form-section">
    <div class="section-header">
      <span class="section-title">指导教师</span>
    </div>
    <div class="advisor-selection-container">
      <el-row :gutter="20" class="mb-4">
        <el-col :span="10">
          <el-input
            v-model="localNewAdvisor.job_number"
            placeholder="工号 (回车查询)"
            @blur="handleSearchNewAdvisor"
            @keyup.enter="handleSearchNewAdvisor"
          >
            <template #append>
              <el-button :icon="Search" @click="handleSearchNewAdvisor" />
            </template>
          </el-input>
        </el-col>
        <el-col :span="7">
          <el-input
            v-model="localNewAdvisor.name"
            placeholder="姓名"
            disabled
          />
        </el-col>
        <el-col :span="7">
          <el-input
            v-model="localNewAdvisor.title"
            placeholder="职称"
            disabled
          />
        </el-col>
      </el-row>
      <el-row :gutter="20">
        <el-col :span="10">
          <el-input v-model="localNewAdvisor.email" placeholder="电子邮箱" />
        </el-col>
        <el-col :span="10">
          <el-input
            v-model="localNewAdvisor.contact"
            placeholder="联系电话 (选填)"
          />
        </el-col>
        <el-col :span="4">
          <el-button
            type="primary"
            class="add-btn"
            @click="handleAddNewAdvisor"
          >
            <el-icon class="mr-1"><Plus /></el-icon> 添加
          </el-button>
        </el-col>
      </el-row>
    </div>

    <el-table
      :data="formData.advisors"
      style="width: 100%; margin-top: 16px"
      border
      :header-cell-style="{
        background: '#f1f5f9',
        color: '#475569',
        fontWeight: '600',
      }"
      class="advisor-table"
    >
      <el-table-column prop="job_number" label="工号" width="120" />
      <el-table-column prop="name" label="姓名" width="100" />
      <el-table-column prop="title" label="职称" width="100">
        <template #default="scope">
          {{ getLabel(advisorTitleOptions, scope.row.title) }}
        </template>
      </el-table-column>
      <el-table-column prop="contact" label="电话" />
      <el-table-column prop="email" label="邮箱" />
      <el-table-column label="操作" width="80" align="center">
        <template #default="scope">
          <el-button
            link
            type="danger"
            size="small"
            @click="removeAdvisor(scope.$index)"
            >删除</el-button
          >
        </template>
      </el-table-column>
      <template #empty>
        <div class="py-8 text-gray-400">暂无指导教师，请在上方添加</div>
      </template>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { Search, Plus } from "@element-plus/icons-vue";
import { reactive, watch } from "vue";

type AdvisorRow = {
  order: number;
  job_number: string;
  name: string;
  title: string;
  email: string;
  contact: string;
};

type AdvisorFormData = {
  advisors: AdvisorRow[];
};

type OptionItem = {
  value: string;
  label: string;
};

const props = defineProps<{
  formData: AdvisorFormData;
  newAdvisor: AdvisorRow;
  advisorTitleOptions: OptionItem[];
  getLabel: (options: OptionItem[], value: string) => string;
  handleSearchNewAdvisor: () => void;
  handleAddNewAdvisor: () => void;
  removeAdvisor: (index: number) => void;
}>();

const emit = defineEmits<{
  (event: "update:newAdvisor", value: AdvisorRow): void;
}>();

const localNewAdvisor = reactive<AdvisorRow>({
  order: 1,
  job_number: "",
  name: "",
  title: "",
  email: "",
  contact: "",
});

watch(
  () => props.newAdvisor,
  (value) => {
    Object.assign(localNewAdvisor, value);
  },
  { immediate: true, deep: true }
);

watch(
  localNewAdvisor,
  (value) => {
    emit("update:newAdvisor", { ...value });
  },
  { deep: true }
);
</script>

<style scoped>
.advisor-selection-container {
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  transition: all 0.3s ease;
}

.advisor-selection-container:hover {
  border-color: #cbd5e1;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.mb-4 {
  margin-bottom: 20px;
}

.add-btn {
  width: 100%;
  height: 32px; /* Match input height default */
}

/* Make inputs look a bit more polished if needed, but Element Plus defaults are usually okay */
:deep(.el-input__wrapper) {
  box-shadow: 0 0 0 1px #e2e8f0 inset;
}
:deep(.el-input__wrapper:hover) {
  box-shadow: 0 0 0 1px #94a3b8 inset;
}
:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1px #409eff inset;
}
</style>
