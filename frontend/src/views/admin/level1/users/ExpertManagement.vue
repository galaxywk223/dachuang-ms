<template>
  <div class="teacher-management-page">
    <el-card class="main-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="header-title">专家库管理</span>
            <el-tag type="info" size="small" effect="plain" round class="count-tag ml-3">
              共 {{ total }} 项
            </el-tag>
          </div>
        </div>
      </template>

      <div class="filter-section">
        <el-form :inline="true" :model="filters" class="filter-form">
          <el-form-item label="搜索">
            <el-input
              v-model="filters.search"
              placeholder="姓名 / 工号"
              clearable
              :prefix-icon="Search"
              style="width: 200px"
              @keyup.enter="handleSearch"
            />
          </el-form-item>

          <el-form-item label="学院">
            <el-select
              v-model="filters.college"
              placeholder="选择学院"
              clearable
              filterable
              style="width: 180px"
            >
              <el-option
                v-for="item in collegeOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="专家">
            <el-select v-model="filters.is_expert" placeholder="全部" style="width: 160px">
              <el-option
                v-for="item in expertStatusOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="resetFilters">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <div class="table-section">
        <el-table v-loading="loading" :data="tableData" style="width: 100%" stripe>
          <el-table-column prop="employee_id" label="工号" width="120" sortable />
          <el-table-column prop="real_name" label="姓名" width="120" />
          <el-table-column prop="title" label="职称" width="120">
            <template #default="{ row }">
              {{ getLabel(DICT_CODES.ADVISOR_TITLE, row.title) }}
            </template>
          </el-table-column>
          <el-table-column prop="is_expert" label="专家" width="120">
            <template #default="{ row }">
              <el-switch
                :model-value="row.is_expert"
                @change="(value) => handleToggleExpert(row, value)"
              />
            </template>
          </el-table-column>
          <el-table-column prop="college" label="所属学院" width="180">
            <template #default="{ row }">
              {{ getLabel(DICT_CODES.COLLEGE, row.college) }}
            </template>
          </el-table-column>
          <el-table-column prop="phone" label="手机号" width="130" />
          <el-table-column prop="email" label="邮箱" min-width="180" />
          <el-table-column label="状态" width="100">
            <template #default="scope">
              <el-tag :type="scope.row.is_active ? 'success' : 'danger'" size="small">
                {{ scope.row.is_active ? '正常' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-footer">
          <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next, jumper"
            :total="total"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
            background
            size="small"
          />
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { Search } from "@element-plus/icons-vue";

import { DICT_CODES } from "@/api/dictionaries";
import { useExpertManagement } from "./hooks/useExpertManagement";

const {
  loading,
  tableData,
  total,
  currentPage,
  pageSize,
  filters,
  collegeOptions,
  expertStatusOptions,
  loadDictionaries,
  getLabel,
  loadData,
  handleSearch,
  resetFilters,
  handleSizeChange,
  handleCurrentChange,
  handleToggleExpert,
} = useExpertManagement();

onMounted(() => {
  loadDictionaries([DICT_CODES.COLLEGE, DICT_CODES.ADVISOR_TITLE]);
  loadData();
});
</script>

<style scoped lang="scss" src="./TeacherManagement.scss"></style>
