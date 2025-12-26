<template>
  <div class="project-detail-page" v-loading="pageLoading">
    <div class="form-container">
      <div class="page-header">
        <div class="title-bar">
          <span class="title">{{ pageTitle }}</span>
          <el-tag size="small" type="primary" effect="plain" round>一级管理员</el-tag>
          <el-tag
            v-if="form.status_display"
            size="small"
            effect="plain"
            type="info"
            round
          >
            {{ form.status_display }}
          </el-tag>
          <el-tag
            v-if="form.project_no"
            size="small"
            effect="plain"
            round
            type="success"
          >
            编号: {{ form.project_no }}
          </el-tag>
        </div>
        <div class="actions">
          <el-button @click="router.back()">返回</el-button>
          <el-button v-if="isViewMode" type="success" @click="handleExportDoc">
            导出申报书
          </el-button>
          <el-button v-if="isViewMode" type="primary" @click="switchToEdit">
            进入编辑
          </el-button>
          <el-button
            v-else
            type="primary"
            :loading="saving"
            @click="handleSubmit"
          >
            保存修改
          </el-button>
        </div>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="right"
        label-width="120px"
        status-icon
        size="default"
        class="main-form"
        :disabled="isViewMode"
      >
        <div class="form-section">
          <div class="section-header">
            <span class="section-title">基本信息</span>
          </div>
          <el-row :gutter="32">
            <el-col :span="8">
              <el-form-item label="项目来源" prop="source">
                <el-select v-model="form.source" placeholder="请选择" class="w-full">
                  <el-option
                    v-for="item in sourceOptions"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="项目级别" prop="level">
                <el-select v-model="form.level" placeholder="请选择" class="w-full">
                  <el-option
                    v-for="item in levelOptions"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="项目类别" prop="category">
                <el-select v-model="form.category" placeholder="请选择" class="w-full">
                  <el-option
                    v-for="item in categoryOptions"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="重点领域" prop="is_key_field">
                <el-cascader
                  v-model="keyFieldCascaderValue"
                  :options="keyFieldCascaderOptions"
                  placeholder="请选择"
                  class="w-full"
                  :props="{ expandTrigger: 'hover' }"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="项目名称" prop="title">
                <el-input v-model="form.title" placeholder="请输入项目全称" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="经费预算" prop="budget">
                <el-input-number
                  v-model="form.budget"
                  :min="0"
                  :precision="2"
                  class="w-full"
                  controls-position="right"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="批准经费" prop="approved_budget">
                <el-input-number
                  v-model="form.approved_budget"
                  :min="0"
                  :precision="2"
                  class="w-full"
                  controls-position="right"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="所属学院">
                <el-select v-model="form.college" class="w-full" disabled>
                  <el-option
                    v-for="item in collegeOptions"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="所属专业">
                <el-select v-model="form.major_code" class="w-full" filterable disabled>
                  <el-option
                    v-for="item in majorOptions"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value"
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <div class="form-section">
          <div class="section-header">
            <span class="section-title">负责人信息</span>
          </div>
          <el-row :gutter="32">
            <el-col :span="8">
              <el-form-item label="负责人姓名">
                <el-input v-model="form.leader_name" disabled class="is-disabled-soft" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="负责人学号">
                <el-input
                  v-model="form.leader_student_id"
                  disabled
                  class="is-disabled-soft"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="联系电话">
                <el-input v-model="form.leader_contact" disabled class="is-disabled-soft" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="电子邮箱">
                <el-input v-model="form.leader_email" disabled class="is-disabled-soft" />
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <div class="form-section">
          <div class="section-header">
            <span class="section-title">指导教师</span>
          </div>
          <el-table
            :data="form.advisors"
            style="width: 100%"
            border
            :header-cell-style="{ background: '#f8fafc', color: '#475569' }"
          >
            <el-table-column label="次序" width="120">
              <template #default="scope">
                <el-tag :type="scope.row.order === 1 ? 'primary' : 'success'" effect="plain">
                  {{ scope.row.order === 1 ? "第一指导老师" : "第二指导老师" }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="job_number" label="工号" width="120" />
            <el-table-column prop="name" label="姓名" width="120" />
            <el-table-column prop="title" label="职称" width="120">
              <template #default="scope">
                {{ getLabel(advisorTitleOptions, scope.row.title) }}
              </template>
            </el-table-column>
            <el-table-column prop="contact" label="电话" />
            <el-table-column prop="email" label="邮箱" />
            <template #empty>
              <div class="empty-text">暂无指导教师信息</div>
            </template>
          </el-table>
        </div>

        <div class="form-section">
          <div class="section-header">
            <span class="section-title">团队成员</span>
          </div>
          <el-table
            :data="form.members"
            style="width: 100%"
            border
            :header-cell-style="{ background: '#f8fafc', color: '#475569' }"
          >
            <el-table-column prop="student_id" label="学号" width="140" />
            <el-table-column prop="name" label="姓名" width="140" />
            <el-table-column prop="role" label="角色">
              <template #default="scope">
                <el-tag size="small" effect="plain" type="info">
                  {{ scope.row.role === "LEADER" ? "负责人" : "成员" }}
                </el-tag>
              </template>
            </el-table-column>
            <template #empty>
              <div class="empty-text">暂无成员信息</div>
            </template>
          </el-table>
        </div>

        <div class="form-section">
          <div class="section-header">
            <span class="section-title">项目信息</span>
          </div>
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="预期成果" prop="expected_results">
                <el-input
                  type="textarea"
                  v-model="form.expected_results"
                  :rows="5"
                  placeholder="预期的项目成果"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="项目简介" prop="description">
                <el-input
                  type="textarea"
                  v-model="form.description"
                  :rows="5"
                  placeholder="项目简介"
                />
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <div class="form-section">
          <div class="section-header">
            <span class="section-title">项目合同与任务书</span>
          </div>
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="项目合同">
                <template v-if="isViewMode">
                  <el-link
                    v-if="form.contract_file_url"
                    :href="form.contract_file_url"
                    target="_blank"
                  >
                    {{ form.contract_file_name || "下载合同" }}
                  </el-link>
                  <span v-else>无</span>
                </template>
                <template v-else>
                  <el-upload
                    action="#"
                    :auto-upload="false"
                    :limit="1"
                    :on-change="handleContractFileChange"
                  >
                    <el-button type="primary" plain>选择合同文件</el-button>
                  </el-upload>
                  <div v-if="form.contract_file_url" class="file-hint">
                    当前：{{ form.contract_file_name || "已上传" }}
                  </div>
                </template>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="项目任务书">
                <template v-if="isViewMode">
                  <el-link
                    v-if="form.task_book_file_url"
                    :href="form.task_book_file_url"
                    target="_blank"
                  >
                    {{ form.task_book_file_name || "下载任务书" }}
                  </el-link>
                  <span v-else>无</span>
                </template>
                <template v-else>
                  <el-upload
                    action="#"
                    :auto-upload="false"
                    :limit="1"
                    :on-change="handleTaskBookFileChange"
                  >
                    <el-button type="primary" plain>选择任务书文件</el-button>
                  </el-upload>
                  <div v-if="form.task_book_file_url" class="file-hint">
                    当前：{{ form.task_book_file_name || "已上传" }}
                  </div>
                </template>
              </el-form-item>
            </el-col>
          </el-row>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useProjectDetail } from "./hooks/useProjectDetail";

const {
  router,
  pageLoading,
  saving,
  formRef,
  form,
  isViewMode,
  pageTitle,
  rules,
  levelOptions,
  categoryOptions,
  sourceOptions,
  collegeOptions,
  majorOptions,
  advisorTitleOptions,
  keyFieldCascaderOptions,
  keyFieldCascaderValue,
  getLabel,
  handleSubmit,
  switchToEdit,
  handleExportDoc,
  handleContractFileChange,
  handleTaskBookFileChange,
} = useProjectDetail();
void formRef;
</script>

<style scoped lang="scss" src="./ProjectDetail.scss"></style>
