<template>
  <div class="form-section">
    <div class="section-header">
      <span class="section-title">项目成员</span>
    </div>
    <div class="dynamic-input-row">
      <el-row :gutter="16">
        <el-col :span="10">
          <el-input
            v-model="newMember.student_id"
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
          <el-input v-model="newMember.name" placeholder="成员姓名" disabled />
        </el-col>
        <el-col :span="4">
          <el-button type="primary" plain @click="handleAddNewMember" style="width: 100%">
            <el-icon class="mr-1"><Plus /></el-icon> 添加成员
          </el-button>
        </el-col>
      </el-row>
    </div>

    <el-table
      :data="formData.members"
      style="width: 100%; margin-top: 12px;"
      border
      :header-cell-style="{ background: '#f8fafc', color: '#475569' }"
    >
      <el-table-column prop="student_id" label="学号" width="180" />
      <el-table-column prop="name" label="姓名" />
      <el-table-column label="操作" width="80" align="center">
        <template #default="scope">
          <el-button link type="danger" size="small" @click="removeMember(scope.$index)">删除</el-button>
        </template>
      </el-table-column>
      <template #empty>
        <div class="empty-text">暂无成员，请在上方添加</div>
      </template>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { Search, Plus } from "@element-plus/icons-vue";

defineProps<{
  formData: any;
  newMember: any;
  handleSearchNewMember: () => void;
  handleAddNewMember: () => void;
  removeMember: (index: number) => void;
}>();
</script>
