<template>
  <div class="teacher-management-page"> <!-- Reuse SCSS class for padding -->
    <el-card class="main-card" shadow="never">
      <template #header>
         <div class="card-header">
            <div class="header-left">
              <span class="header-title">专家库管理</span>
              <el-tag type="info" size="small" effect="plain" round class="count-tag ml-3">共 {{ total }} 项</el-tag>
            </div>
            <div class="header-actions">
              <el-button type="primary" @click="openCreateDialog">
                <el-icon class="mr-1"><Plus /></el-icon>添加专家
              </el-button>
              <el-button @click="handleImportClick">
                  <el-icon class="mr-1"><Upload /></el-icon>批量导入
              </el-button>
            </div>
         </div>
      </template>

      <!-- Filter Section -->
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

          <el-form-item label="级别">
            <el-select
              v-model="filters.expert_scope"
              placeholder="全部"
              clearable
              style="width: 160px"
            >
              <el-option
                v-for="item in expertScopeOptions"
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

      <!-- Table Section -->
      <div class="table-section">
        <el-table
          v-loading="loading"
          :data="tableData"
          style="width: 100%"
          stripe
        >
          <el-table-column prop="employee_id" label="工号" width="120" sortable />
          <el-table-column prop="real_name" label="姓名" width="120" />
          <el-table-column prop="title" label="职称" width="120">
             <template #default="{ row }">
                 {{ getLabel(DICT_CODES.ADVISOR_TITLE, row.title) }}
             </template>
          </el-table-column>
          <el-table-column prop="expert_scope" label="级别" width="120">
            <template #default="{ row }">
              <el-tag size="small" effect="plain">
                {{ getScopeLabel(row.expert_scope) }}
              </el-tag>
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
          <el-table-column label="操作" fixed="right" width="180">
            <template #default="scope">
              <el-button link type="primary" size="small" @click="handleEdit(scope.row)">编辑</el-button>
              <el-button 
                  link 
                  type="danger" 
                  size="small" 
                  @click="handleToggleStatus(scope.row)"
              >
                  {{ scope.row.is_active ? '禁用' : '激活' }}
              </el-button>
              <el-button 
                  link 
                  type="danger" 
                  size="small" 
                  @click="handleDelete(scope.row)"
              >
                  删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>

        <!-- Pagination -->
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

    <el-dialog
      v-model="addDialogVisible"
      :title="isEditMode ? '编辑专家' : '添加专家'"
      width="720px"
      :close-on-click-modal="false"
      @closed="resetFormState"
    >
      <el-form
        :ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="90px"
        class="admin-form"
      >
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="工号" prop="employee_id">
              <el-input v-model="formData.employee_id" placeholder="请输入工号" :disabled="isEditMode" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="姓名" prop="real_name">
              <el-input v-model="formData.real_name" placeholder="请输入姓名" />
            </el-form-item>
          </el-col>
          <el-col :span="12" v-if="!isEditMode">
            <el-form-item label="密码" prop="password">
              <el-input
                v-model="formData.password"
                placeholder="默认 123456"
                show-password
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="职称" prop="title">
                <el-select v-model="formData.title" placeholder="请选择职称" style="width: 100%">
                    <el-option
                        v-for="item in titleOptions"
                        :key="item.value"
                        :label="item.label"
                        :value="item.value"
                    />
                </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="级别" prop="expert_scope">
              <el-select v-model="formData.expert_scope" placeholder="请选择级别" style="width: 100%">
                <el-option
                  v-for="item in expertScopeOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="手机号" prop="phone">
              <el-input
                v-model="formData.phone"
                placeholder="可选，11位数字"
                maxlength="11"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="formData.email" placeholder="可选，学校邮箱" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="学院" prop="college">
              <el-select
                v-model="formData.college"
                placeholder="选择学院"
                filterable
                clearable
                allow-create
                default-first-option
                style="width: 100%"
                :disabled="formData.expert_scope === 'SCHOOL'"
              >
                <el-option
                  v-for="item in collegeOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="addDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitLoading" @click="handleSubmit">
            {{ isEditMode ? '保存修改' : '确认添加' }}
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- Import Dialog -->
    <el-dialog
       v-model="importDialogVisible"
       title="批量导入专家"
       width="500px"
    >
       <el-form :model="importForm" label-width="80px" style="margin-bottom: 12px;">
         <el-form-item label="级别">
           <el-select v-model="importForm.expert_scope" placeholder="请选择级别" style="width: 100%">
             <el-option
               v-for="item in expertScopeOptions"
               :key="item.value"
               :label="item.label"
               :value="item.value"
             />
           </el-select>
         </el-form-item>
       </el-form>
       <div style="text-align: center; margin-bottom: 20px;">
          <el-upload
             class="upload-demo"
             drag
             action="#"
             :auto-upload="false"
             :limit="1"
             :on-change="handleFileChange"
             accept=".xlsx, .xls"
          >
             <el-icon class="el-icon--upload"><upload-filled /></el-icon>
             <div class="el-upload__text">
                将文件拖到此处，或 <em>点击上传</em>
             </div>
             <template #tip>
                <div class="el-upload__tip">
                   只能上传 xlsx/xls 文件，且不超过 5MB
                </div>
             </template>
          </el-upload>
       </div>
       <template #footer>
          <span class="dialog-footer">
             <el-button @click="importDialogVisible = false">取消</el-button>
             <el-button type="primary" :loading="importLoading" @click="handleImportSubmit">
                开始导入
             </el-button>
          </span>
       </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { Plus, Search, Upload, UploadFilled } from "@element-plus/icons-vue";

import { useExpertManagement } from "./hooks/useExpertManagement";

const {
  addDialogVisible,
  collegeOptions,
  currentPage,
  DICT_CODES,
  expertScopeOptions,
  filters,
  formData,
  formRef,
  formRules,
  getLabel,
  getScopeLabel,
  handleCurrentChange,
  handleDelete,
  handleEdit,
  handleFileChange,
  handleImportClick,
  handleImportSubmit,
  handleSearch,
  handleSizeChange,
  handleSubmit,
  handleToggleStatus,
  importDialogVisible,
  importForm,
  importLoading,
  isEditMode,
  loading,
  openCreateDialog,
  pageSize,
  resetFormState,
  resetFilters,
  submitLoading,
  tableData,
  titleOptions,
  total,
} = useExpertManagement();
</script>

<style scoped lang="scss" src="./TeacherManagement.scss"></style>
