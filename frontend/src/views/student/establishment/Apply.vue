<template>
  <div class="apply-page">
    <el-card class="main-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-left">
             <span class="header-title">基本信息填报</span>
          </div>
          <div class="header-actions">
             <el-button @click="handleReset">重置</el-button>
             <el-button type="info" plain @click="saveAsDraft">保存草稿</el-button>
             <el-button type="primary" @click="submitForm">提交申请</el-button>
          </div>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-position="right"
        label-width="120px"
        status-icon
        size="default"
        class="main-form"
      >
        <ApplyBasicInfoSection
          :form-data="formData"
          :source-options="sourceOptions"
          :level-options="levelOptions"
          :category-options="categoryOptions"
          :key-field-cascader-options="keyFieldCascaderOptions"
          :college-options="collegeOptions"
          :major-options="majorOptions"
          v-model:key-field-cascader-value="keyFieldCascaderValue"
        />

        <ApplyLeaderSection :form-data="formData" :current-user="currentUser" />

        <ApplyAdvisorSection
          :form-data="formData"
          :new-advisor="newAdvisor"
          :advisor-title-options="advisorTitleOptions"
          :get-label="getLabel"
          :handle-search-new-advisor="handleSearchNewAdvisor"
          :handle-add-new-advisor="handleAddNewAdvisor"
          :remove-advisor="removeAdvisor"
        />

        <ApplyMemberSection
          :form-data="formData"
          :new-member="newMember"
          :handle-search-new-member="handleSearchNewMember"
          :handle-add-new-member="handleAddNewMember"
          :remove-member="removeMember"
        />

        <ApplyContentSection
          :form-data="formData"
          :expected-form="expectedForm"
          :achievement-type-options="achievementTypeOptions"
          :get-label="getLabel"
          :add-expected-result="addExpectedResult"
          :remove-expected-result="removeExpectedResult"
        />

        <ApplyAttachmentSection
          v-model:file-list="fileList"
          :current-template-url="currentTemplateUrl"
          :handle-download-template="handleDownloadTemplate"
          :handle-file-change="handleFileChange"
          :handle-file-remove="handleFileRemove"
        />

      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import ApplyBasicInfoSection from "./components/ApplyBasicInfoSection.vue";
import ApplyLeaderSection from "./components/ApplyLeaderSection.vue";
import ApplyAdvisorSection from "./components/ApplyAdvisorSection.vue";
import ApplyMemberSection from "./components/ApplyMemberSection.vue";
import ApplyContentSection from "./components/ApplyContentSection.vue";
import ApplyAttachmentSection from "./components/ApplyAttachmentSection.vue";
import { useProjectApplication } from "./useProjectApplication";

const {
  formRef,
  formData,
  rules,
  sourceOptions,
  levelOptions,
  categoryOptions,
  keyFieldCascaderOptions,
  keyFieldCascaderValue,
  collegeOptions,
  majorOptions,
  currentUser,
  newAdvisor,
  newMember,
  expectedForm,
  achievementTypeOptions,
  advisorTitleOptions,
  fileList,
  currentTemplateUrl,
  handleDownloadTemplate,
  handleFileChange,
  handleFileRemove,
  handleSearchNewAdvisor,
  handleAddNewAdvisor,
  removeAdvisor,
  handleSearchNewMember,
  handleAddNewMember,
  removeMember,
  addExpectedResult,
  removeExpectedResult,
  getLabel,
  submitForm,
  saveAsDraft,
  handleReset,
} = useProjectApplication();

void formRef;
</script>

<style scoped lang="scss">
@use "./Apply.scss";
</style>
