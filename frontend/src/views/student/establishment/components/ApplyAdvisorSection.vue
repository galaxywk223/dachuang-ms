<template>
  <div class="form-section">
    <div class="section-header">
      <span class="section-title">指导教师</span>
    </div>
    <div class="dynamic-input-row">
      <el-row :gutter="16" class="mb-3">
        <el-col :span="4">
          <el-select v-model="localNewAdvisor.order" placeholder="指导次序" style="width: 100%">
            <el-option label="第一指导老师" :value="1" />
            <el-option label="第二指导老师" :value="2" />
          </el-select>
        </el-col>
        <el-col :span="8">
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
        <el-col :span="6">
          <el-input v-model="localNewAdvisor.name" placeholder="姓名" disabled />
        </el-col>
        <el-col :span="6">
          <el-input v-model="localNewAdvisor.title" placeholder="职称" disabled />
        </el-col>
      </el-row>
      <el-row :gutter="16">
        <el-col :span="10">
          <el-input v-model="localNewAdvisor.email" placeholder="电子邮箱" />
        </el-col>
        <el-col :span="10">
          <el-input v-model="localNewAdvisor.contact" placeholder="联系电话 (选填)" />
        </el-col>
        <el-col :span="4">
          <el-button type="primary" plain @click="handleAddNewAdvisor" style="width: 100%">
            <el-icon class="mr-1"><Plus /></el-icon> 添加
          </el-button>
        </el-col>
      </el-row>
    </div>

    <el-table
      :data="formData.advisors"
      style="width: 100%; margin-top: 12px;"
      border
      :header-cell-style="{ background: '#f8fafc', color: '#475569' }"
    >
      <el-table-column label="次序" width="120">
        <template #default="scope">
          <el-tag :type="scope.row.order === 1 ? 'primary' : 'success'" effect="plain">
            {{ scope.row.order === 1 ? '第一指导老师' : '第二指导老师' }}
          </el-tag>
        </template>
      </el-table-column>
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
          <el-button link type="danger" size="small" @click="removeAdvisor(scope.$index)">删除</el-button>
        </template>
      </el-table-column>
      <template #empty>
        <div class="empty-text">暂无指导教师，请在上方添加</div>
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
