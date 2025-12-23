<template>
  <div class="projects-page">
    <!-- 筛选区域 -->
    <div class="filter-section">
      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="名称/编号">
          <el-input
            v-model="filters.search"
            placeholder="项目名称或编号"
            clearable
            :prefix-icon="Search"
            style="width: 200px"
          />
        </el-form-item>

        <el-form-item label="级别">
          <el-select
            v-model="filters.level"
            placeholder="全部级别"
            clearable
            style="width: 120px"
          >
            <el-option
              v-for="item in levelOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="类别">
          <el-select
            v-model="filters.category"
            placeholder="全部类别"
            clearable
            style="width: 120px"
          >
            <el-option
              v-for="item in categoryOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="状态">
          <el-select
            v-model="filters.status"
            placeholder="全部状态"
            clearable
            style="width: 120px"
          >
            <el-option
              v-for="item in statusOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSearch" :icon="Search"
            >查询</el-button
          >
          <el-button @click="handleReset" :icon="RefreshLeft">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 表格区域 -->
    <div class="table-container">
      <div class="table-header">
        <div class="title-bar">
          <span class="title">系统项目管理</span>
          <el-tag
            type="info"
            size="small"
            effect="plain"
            round
            class="count-tag"
            >共 {{ total }} 项</el-tag
          >
        </div>
        <div class="actions">
          <el-button
            type="success"
            plain
            :icon="Download"
            @click="handleBatchExport"
          >
            导出数据
          </el-button>
          <el-button
            type="warning"
            plain
            :icon="Download"
            @click="handleBatchDownload"
          >
            下载附件
          </el-button>
          <el-dropdown @command="handleBatchCommand">
            <el-button type="primary" plain>
              批量操作
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="status">批量状态变更</el-dropdown-item>
                <el-dropdown-item command="docs">批量导出申报书</el-dropdown-item>
                <el-dropdown-item command="notices">批量生成立项通知书</el-dropdown-item>
                <el-dropdown-item command="certs">批量生成结题证书</el-dropdown-item>
                <el-dropdown-item command="push">批量推送至省平台</el-dropdown-item>
                <el-dropdown-item command="notify">批量通知</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>

      <el-table
        v-loading="loading"
        :data="projects"
        style="width: 100%"
        :header-cell-style="{
          background: '#f8fafc',
          color: '#475569',
          fontWeight: '600',
          height: '48px',
        }"
        :cell-style="{ color: '#334155', height: '48px' }"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" align="center" />

        <el-table-column
          prop="project_no"
          label="项目编号"
          width="130"
          show-overflow-tooltip
        >
          <template #default="{ row }">
            <span class="font-mono">{{ row.project_no || "-" }}</span>
          </template>
        </el-table-column>

        <el-table-column
          prop="title"
          label="项目名称"
          min-width="200"
          show-overflow-tooltip
          fixed="left"
        >
          <template #default="{ row }">
            <span class="project-title">{{ row.title }}</span>
          </template>
        </el-table-column>

        <el-table-column
          prop="level"
          label="项目级别"
          width="100"
          align="center"
        >
          <template #default="{ row }">
            <el-tag
              :type="getLevelType(row.level)"
              effect="plain"
              size="small"
              >{{ row.level_display || getLabel(levelOptions, row.level) }}</el-tag
            >
          </template>
        </el-table-column>

        <el-table-column
          prop="category"
          label="项目类别"
          width="120"
          align="center"
        >
          <template #default="{ row }">
            <el-tag effect="light" size="small" type="info">{{
              row.category_display || getLabel(categoryOptions, row.category)
            }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column label="重点领域项目" width="110" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.is_key_field" type="success" size="small">是</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>

        <el-table-column label="重点领域代码" width="110" align="center">
          <template #default="{ row }">
             <span>{{ row.key_domain_code || '-' }}</span>
          </template>
        </el-table-column>

        <el-table-column
          prop="leader_name"
          label="负责人姓名"
          width="100"
          align="center"
        >
          <template #default="{ row }">
             {{ row.leader_name || '-' }}
          </template>
        </el-table-column>

        <el-table-column
          prop="leader_student_id"
          label="负责人学号"
          width="120"
          align="center"
        >
           <template #default="{ row }">
               {{ row.leader_student_id || '-' }}
           </template>
        </el-table-column>

        <el-table-column
          prop="college"
          label="学院"
          width="140"
          show-overflow-tooltip
          align="center"
        >
            <template #default="{ row }">
                {{ row.college || '-' }}
            </template>
        </el-table-column>

        <el-table-column
          prop="leader_contact"
          label="联系电话"
          width="120"
          align="center"
        >
            <template #default="{ row }">
                {{ row.leader_contact || '-' }}
            </template>
        </el-table-column>

        <el-table-column
          prop="leader_email"
          label="邮箱"
          width="180"
          show-overflow-tooltip
          align="center"
        >
            <template #default="{ row }">
                {{ row.leader_email || '-' }}
            </template>
        </el-table-column>

        <el-table-column
          prop="budget"
          label="项目经费"
          width="100"
          align="center"
        >
           <template #default="{ row }">
              {{ row.budget }}
           </template>
        </el-table-column>

        <el-table-column
          prop="approved_budget"
          label="批准经费"
          width="100"
          align="center"
        >
           <template #default="{ row }">
              {{ row.approved_budget ?? '-' }}
           </template>
        </el-table-column>

        <el-table-column label="审核节点" width="140" align="center" fixed="right">
          <template #default="{ row }">
            <div class="status-dot">
              <span class="dot" :class="getStatusClass(row.status)"></span>
              <span>{{ row.status_display }}</span>
            </div>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="180" align="center" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleView(row)"
              >查看</el-button
            >
            <el-button link type="primary" @click="handleEdit(row)"
              >编辑</el-button
            >
            <el-button link type="danger" @click="handleDelete(row)"
              >删除</el-button
            >
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-footer">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
          background
          size="small"
          class="custom-pagination"
        />
      </div>
    </div>

    <el-dialog v-model="batchStatusDialogVisible" title="批量状态变更" width="480px">
      <el-form label-position="top">
        <el-form-item label="目标状态">
          <el-select v-model="batchStatusForm.status" placeholder="请选择状态" style="width: 100%">
            <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="batchStatusDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="batchStatusLoading" @click="submitBatchStatus">确认</el-button>
        </span>
      </template>
    </el-dialog>

    <el-dialog v-model="batchNotifyDialogVisible" title="批量通知" width="520px">
      <el-form label-position="top">
        <el-form-item label="通知标题">
          <el-input v-model="batchNotifyForm.title" placeholder="请输入标题" />
        </el-form-item>
        <el-form-item label="通知内容">
          <el-input v-model="batchNotifyForm.content" type="textarea" :rows="4" placeholder="请输入内容" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="batchNotifyDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="batchNotifyLoading" @click="submitBatchNotify">发送</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { Search, RefreshLeft, Download, ArrowDown } from "@element-plus/icons-vue";
import { useAllProjects } from "./useAllProjects";

const {
  loading,
  projects,
  currentPage,
  pageSize,
  total,
  filters,
  levelOptions,
  categoryOptions,
  statusOptions,
  handleSearch,
  handleReset,
  handlePageChange,
  handleSizeChange,
  handleView,
  handleEdit,
  handleDelete,
  handleSelectionChange,
  handleBatchExport,
  handleBatchDownload,
  handleBatchExportDocs,
  handleBatchExportNotices,
  handleBatchExportCertificates,
  handlePushToExternal,
  openBatchStatusDialog,
  submitBatchStatus,
  openBatchNotifyDialog,
  submitBatchNotify,
  batchStatusDialogVisible,
  batchNotifyDialogVisible,
  batchStatusLoading,
  batchNotifyLoading,
  batchStatusForm,
  batchNotifyForm,
  getLevelType,
  getLabel,
  getStatusClass,
} = useAllProjects();

const handleBatchCommand = (command: string) => {
  if (command === "status") openBatchStatusDialog();
  if (command === "docs") handleBatchExportDocs();
  if (command === "notices") handleBatchExportNotices();
  if (command === "certs") handleBatchExportCertificates();
  if (command === "push") handlePushToExternal();
  if (command === "notify") openBatchNotifyDialog();
};
</script>

<style scoped lang="scss" src="./AllProjects.scss"></style>
