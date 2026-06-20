<template>
  <div class="project-detail-page page-shell" v-loading="pageLoading">
    <div class="form-container">
      <div class="detail-toolbar">
        <div class="detail-copy">
          <span class="header-title">{{ pageTitle }}</span>
          <div class="detail-meta">
            <el-tag size="small" type="primary" effect="light">一级管理员</el-tag>
            <StatusPill
              v-if="form.status_display"
              :status="form.status"
              :label="form.status_display"
            />
            <el-tag
              v-if="form.project_no"
              size="small"
              effect="light"
              type="success"
            >
              编号: {{ form.project_no }}
            </el-tag>
          </div>
        </div>
        <div class="detail-actions">
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
                <el-select
                  v-model="form.source"
                  placeholder="请选择"
                  class="w-full"
                >
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
                <el-select
                  v-model="form.level"
                  placeholder="请选择"
                  class="w-full"
                >
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
                <el-select
                  v-model="form.category"
                  placeholder="请选择"
                  class="w-full"
                >
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
                <el-select
                  v-model="form.major_code"
                  class="w-full"
                  filterable
                  disabled
                >
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
            <span class="section-title">立项结果</span>
            <StatusPill :status="form.publish_status" :label="form.publish_status_display || '未进入发布'" />
          </div>
          <el-row :gutter="24" class="result-grid">
            <el-col :span="6">
              <div class="result-item">
                <span class="label">学院排序</span>
                <strong>{{ form.recommendation_rank || "-" }}</strong>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="result-item">
                <span class="label">推荐级别</span>
                <strong>{{ form.recommended_level_display || "-" }}</strong>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="result-item">
                <span class="label">推荐经费</span>
                <strong>{{ form.recommended_budget ?? "-" }}</strong>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="result-item">
                <span class="label">最终级别</span>
                <strong>{{ form.final_level_display || form.level || "-" }}</strong>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="result-item">
                <span class="label">最终经费</span>
                <strong>{{ form.final_budget ?? form.approved_budget ?? "-" }}</strong>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="result-item">
                <span class="label">发布时间</span>
                <strong>{{ formatDateTime(form.published_at) }}</strong>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="result-item">
                <span class="label">发布人</span>
                <strong>{{ form.published_by_name || "-" }}</strong>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="result-item">
                <span class="label">推荐意见</span>
                <strong>{{ form.recommendation_comment || "-" }}</strong>
              </div>
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
                <el-input
                  v-model="form.leader_name"
                  disabled
                  class="is-disabled-soft"
                />
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
                <el-input
                  v-model="form.leader_contact"
                  disabled
                  class="is-disabled-soft"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="电子邮箱">
                <el-input
                  v-model="form.leader_email"
                  disabled
                  class="is-disabled-soft"
                />
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
                <el-tag
                  :type="scope.row.order === 1 ? 'primary' : 'success'"
                  effect="plain"
                >
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
            <span class="section-title">申报材料</span>
          </div>
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="申报书">
                <el-link
                  v-if="form.proposal_file_url"
                  @click="downloadProjectMaterial('proposal_file')"
                >
                  {{ form.proposal_file_name || "下载申报书" }}
                </el-link>
                <span v-else>无</span>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="其他附件">
                <el-link
                  v-if="form.attachment_file_url"
                  @click="downloadProjectMaterial('attachment_file')"
                >
                  {{ form.attachment_file_name || "下载附件" }}
                </el-link>
                <span v-else>无</span>
              </el-form-item>
            </el-col>
          </el-row>
        </div>

      </el-form>

      <div v-if="timeline.length" class="timeline-panel">
        <div class="section-header">
          <span class="section-title">流程时间线</span>
        </div>
        <el-timeline>
          <el-timeline-item
            v-for="(item, index) in timeline"
            :key="`${item.type || 'event'}-${index}`"
            :timestamp="formatDateTime(item.time)"
            placement="top"
          >
            <div class="timeline-card">
              <div class="timeline-title">
                <span>{{ item.title || "流程事件" }}</span>
                <el-tag v-if="item.status" size="small" effect="plain">
                  {{ item.status }}
                </el-tag>
              </div>
              <p>{{ item.description || "-" }}</p>
              <span v-if="item.reviewer" class="timeline-reviewer">
                处理人：{{ item.reviewer }}
              </span>
            </div>
          </el-timeline-item>
        </el-timeline>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import StatusPill from "@/components/common/StatusPill.vue";
import { useProjectDetail } from "./hooks/useProjectDetail";

defineOptions({ name: "Level1ProjectDetailView" });

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
  timeline,
  getLabel,
  formatDateTime,
  handleSubmit,
  switchToEdit,
  handleExportDoc,
  downloadProjectMaterial,
} = useProjectDetail();
void formRef;
</script>

<style scoped lang="scss" src="./Detail.scss"></style>
