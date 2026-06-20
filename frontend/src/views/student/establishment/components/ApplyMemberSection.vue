<template>
  <div class="form-section">
    <div class="section-header">
      <span class="section-title">项目成员</span>
    </div>
    <div class="member-selection-container">
      <el-row :gutter="20">
        <el-col :span="10">
          <el-input
            v-model="localNewMember.student_id"
            placeholder="成员学号 (回车查询)"
            @blur="handleSearchNewMember"
            @keyup.enter="handleSearchNewMember"
          >
            <template #append>
              <el-button :icon="Search" @click="handleSearchNewMember" />
            </template>
          </el-input>
        </el-col>
        <el-col :span="10">
          <el-input
            v-model="localNewMember.name"
            placeholder="成员姓名"
            disabled
          />
        </el-col>
        <el-col :span="4">
          <el-button type="primary" class="add-btn" @click="handleAddNewMember">
            <el-icon class="mr-1"><Plus /></el-icon> 添加成员
          </el-button>
        </el-col>
      </el-row>
    </div>

    <el-table
      :data="formData.members"
      style="width: 100%; margin-top: 16px"
      border
      :header-cell-style="{
        background: '#f1f5f9',
        color: '#475569',
        fontWeight: '600',
      }"
      class="member-table"
    >
      <el-table-column prop="student_id" label="学号" width="180" />
      <el-table-column prop="name" label="姓名" />
      <el-table-column label="操作" width="80" align="center">
        <template #default="scope">
          <el-button
            link
            type="danger"
            size="small"
            @click="removeMember(scope.$index)"
            >删除</el-button
          >
        </template>
      </el-table-column>
      <template #empty>
        <div class="py-8 text-gray-400">暂无成员，请在上方添加</div>
      </template>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { Search, Plus } from "@element-plus/icons-vue";
import { reactive, watch } from "vue";

type MemberRow = {
  student_id: string;
  name: string;
};

type MemberFormData = {
  members: MemberRow[];
};

const props = defineProps<{
  formData: MemberFormData;
  newMember: MemberRow;
  handleSearchNewMember: () => void;
  handleAddNewMember: () => void;
  removeMember: (index: number) => void;
}>();

const emit = defineEmits<{
  (event: "update:newMember", value: MemberRow): void;
}>();

const localNewMember = reactive<MemberRow>({
  student_id: "",
  name: "",
});

watch(
  () => props.newMember,
  (value) => {
    Object.assign(localNewMember, value);
  },
  { immediate: true, deep: true }
);

watch(
  localNewMember,
  (value) => {
    emit("update:newMember", { ...value });
  },
  { deep: true }
);
</script>

<style scoped>
.member-selection-container {
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  transition: all 0.3s ease;
}

.member-selection-container:hover {
  border-color: #cbd5e1;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}

.add-btn {
  width: 100%;
  height: 32px;
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
</style>
