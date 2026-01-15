<template>
  <div class="dictionary-page">
    <div class="page-header-wrapper" v-if="!dictTypeCode">
      <div class="title-bar">
        <span class="title">{{ route.meta.title || "系统参数管理" }}</span>
      </div>
    </div>

    <div class="content-container">
      <el-row :gutter="20">
        <!-- Dictionary Types List - 只在未指定dictTypeCode时显示 -->
        <el-col :span="6" v-if="!dictTypeCode">
          <el-card
            class="types-card"
            shadow="never"
            :body-style="{ padding: '0' }"
          >
            <template #header>
              <div class="card-header">
                <span>参数类型</span>
              </div>
            </template>
            <div class="types-list">
              <div
                v-for="type in dictionaryTypes"
                :key="type.code"
                class="type-item"
                :class="{ active: currentType?.code === type.code }"
                @click="handleTypeSelect(type)"
              >
                <el-icon class="icon"><Collection /></el-icon>
                <span class="type-name">{{ type.name }}</span>
                <el-icon class="arrow"><ArrowRight /></el-icon>
              </div>
            </div>
          </el-card>
        </el-col>

        <!-- Dictionary Items Management -->
        <el-col :span="dictTypeCode ? 24 : 18">
          <el-card class="items-card main-card" shadow="never">
            <template #header>
              <div class="card-header">
                <div class="header-left">
                  <span class="header-title">{{
                    currentType?.name || "请选择左侧参数类型"
                  }}</span>
                  <span class="header-desc" v-if="currentType">{{
                    currentType.description
                  }}</span>
                </div>
                <div
                  class="header-actions"
                  v-if="currentType && !currentType.isLocal"
                >
                  <el-button @click="openImportDialog">
                    <el-icon><Upload /></el-icon> 导入
                  </el-button>
                  <el-button type="warning" plain @click="clearItems">
                    <el-icon><Delete /></el-icon> 清空
                  </el-button>
                  <el-button type="primary" @click="openAddDialog">
                    <el-icon><Plus /></el-icon> 添加条目
                  </el-button>
                </div>
                <!-- Custom Header Actions Slot -->
                <div
                  class="header-actions"
                  v-else-if="currentType && currentType.isLocal"
                >
                  <slot name="header-actions" :type="currentType"></slot>
                </div>
              </div>
            </template>

            <!-- Items Table -->
            <div v-if="currentType">
              <!-- Custom Local Content -->
              <div v-if="currentType.isLocal" class="local-content">
                <slot name="custom-content" :type="currentType"></slot>
              </div>

              <!-- Standard Dictionary Content -->
              <div v-else>
                <el-table
                  v-loading="loading"
                  :data="items"
                  style="width: 100%"
                  stripe
                  border
                  :header-cell-style="{
                    background: '#f8fafc',
                    color: '#475569',
                    fontWeight: '600',
                  }"
                >
                  <el-table-column
                    prop="label"
                    label="显示名称"
                    min-width="150"
                  />
                  <el-table-column
                    v-if="showCode"
                    prop="value"
                    label="代码"
                    min-width="120"
                  />
                  <el-table-column
                    v-if="currentType?.code === 'project_level'"
                    label="预算(元)"
                    min-width="100"
                  >
                    <template #default="{ row }">
                      {{
                        row.extra_data && row.extra_data.budget
                          ? row.extra_data.budget
                          : "-"
                      }}
                    </template>
                  </el-table-column>
                  <!-- <el-table-column prop="sort_order" label="排序" width="80" align="center" /> -->

                  <el-table-column
                    label="操作"
                    width="160"
                    align="center"
                    fixed="right"
                  >
                    <template #default="{ row }">
                      <el-button
                        link
                        type="primary"
                        size="small"
                        @click="editItem(row)"
                        >编辑</el-button
                      >
                      <el-button
                        link
                        type="danger"
                        size="small"
                        @click="deleteItem(row)"
                        >删除</el-button
                      >
                    </template>
                  </el-table-column>
                </el-table>

                <div class="empty-tip" v-if="!loading && items.length === 0">
                  暂无数据
                </div>
              </div>
            </div>
            <div v-else class="empty-selection">
              <el-empty description="请选择左侧的参数类型进行管理" />
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- Add/Edit Item Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEditMode ? '编辑条目' : `添加 ${currentType?.name || ''} 条目`"
      width="500px"
      align-center
      destroy-on-close
      @closed="resetForm"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="名称" prop="label">
          <el-input v-model="form.label" placeholder="请输入名称" />
        </el-form-item>
        <el-form-item v-if="showCode" label="代码" prop="value">
          <el-input v-model="form.value" placeholder="请输入代码" />
        </el-form-item>
        <el-form-item v-if="showBudget" label="经费预算" prop="budget">
          <el-input-number
            v-model="form.budget"
            :min="0"
            :step="100"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item v-if="showTemplate" label="申请书模板">
          <el-upload
            ref="uploadRef"
            action="#"
            :auto-upload="false"
            :on-change="handleFileChange"
            :on-remove="handleRemoveFile"
            :file-list="fileList"
            :limit="1"
          >
            <template #trigger>
              <el-button type="primary" plain>选择文件</el-button>
            </template>
            <template #tip>
              <div class="el-upload__tip">
                只能上传 PDF/Word 文件，且不超过 5MB
              </div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="submitForm"
            >确定</el-button
          >
        </span>
      </template>
    </el-dialog>

    <el-dialog
      v-model="importDialogVisible"
      title="批量导入条目"
      width="560px"
      align-center
      destroy-on-close
      @closed="resetImport"
    >
      <el-form label-width="90px">
        <el-form-item label="导入文件">
          <el-upload
            action="#"
            :auto-upload="false"
            :limit="1"
            accept=".xlsx,.xls,.csv,.txt"
            :on-change="handleImportFileChange"
          >
            <template #trigger>
              <el-button type="primary" plain>选择文件</el-button>
            </template>
            <template #tip>
              <div class="el-upload__tip">
                支持 XLSX/XLS/CSV/TXT，每行一条；可用逗号或制表符分隔名称与代码
              </div>
            </template>
          </el-upload>
        </el-form-item>
        <el-form-item label="或粘贴">
          <el-input
            v-model="importText"
            type="textarea"
            :rows="6"
            placeholder="每行一条，格式：显示名称,代码（无代码可省略）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="importDialogVisible = false">取消</el-button>
          <el-button
            type="primary"
            :loading="importLoading"
            @click="submitImport"
            >开始导入</el-button
          >
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from "vue-router";
import {
  Plus,
  Collection,
  ArrowRight,
  Upload,
  Delete,
} from "@element-plus/icons-vue";
import { useSystemDictionaries, type DictionaryType } from "./hooks/useSystemDictionaries";

// 支持props传入，也支持从route.meta获取
const props = withDefaults(
  defineProps<{
    category?: string;
    dictTypeCode?: string;
    extraTypes?: DictionaryType[];
  }>(),
  {
    category: undefined,
    dictTypeCode: undefined,
    extraTypes: () => [],
  }
);

const route = useRoute();

// 优先使用props，其次使用route.meta
const effectiveCategory = props.category || (route.meta.category as string);
const effectiveDictTypeCode = props.dictTypeCode;

const {
  dictionaryTypes,
  currentType,
  items,
  loading,
  dialogVisible,
  submitting,
  isEditMode,
  formRef,
  fileList,
  showCode,
  showBudget,
  showTemplate,
  importDialogVisible,
  importLoading,
  importText,
  form,
  rules,
  handleTypeSelect,
  openImportDialog,
  handleImportFileChange,
  submitImport,
  clearItems,
  resetImport,
  openAddDialog,
  editItem,
  resetForm,
  handleFileChange,
  handleRemoveFile,
  submitForm,
  deleteItem,
} = useSystemDictionaries({
  category: effectiveCategory,
  dictTypeCode: effectiveDictTypeCode,
  extraTypes: props.extraTypes,
});
void formRef;
</script>

<style scoped lang="scss" src="./SystemDictionaries.scss"></style>
