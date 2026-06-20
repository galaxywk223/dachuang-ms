<template>
  <div class="apply-page">
    <el-card class="main-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="header-title">结题申请</span>
            <el-tag
              size="small"
              type="success"
              effect="plain"
              round
              class="ml-3"
              >项目结题</el-tag
            >
          </div>
          <div class="header-actions">
            <el-button @click="router.back()">返回</el-button>
            <el-button
              type="info"
              plain
              :loading="loading"
              :disabled="loading"
              @click="saveAsDraft"
              >保存草稿</el-button
            >
            <el-button
              type="primary"
              :loading="loading"
              :disabled="loading"
              @click="submitForm"
              >提交申请</el-button
            >
            <el-button
              type="danger"
              plain
              :disabled="!canDeleteSubmission || loading"
              @click="handleDeleteSubmission"
            >
              删除提交
            </el-button>
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
        v-loading="loading"
      >
        <!-- Project Info -->
        <div class="form-section">
          <div class="section-header">
            <span class="section-title">项目基本信息</span>
          </div>
          <el-row :gutter="32">
            <el-col :span="8">
              <el-form-item label="项目名称">
                <el-input
                  :model-value="projectInfo.title"
                  disabled
                  class="is-disabled-soft"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="项目编号">
                <el-input
                  :model-value="projectInfo.project_no"
                  disabled
                  class="is-disabled-soft"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="负责人">
                <el-input
                  :model-value="projectInfo.leader_name"
                  disabled
                  class="is-disabled-soft"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="级别">
                <el-input
                  :model-value="projectInfo.level_display"
                  disabled
                  class="is-disabled-soft"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="类别">
                <el-input
                  :model-value="projectInfo.category_display"
                  disabled
                  class="is-disabled-soft"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="经费">
                <el-input
                  :model-value="projectInfo.budget"
                  disabled
                  class="is-disabled-soft"
                >
                  <template #append>元</template>
                </el-input>
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <!-- Closure Materials -->
        <div class="form-section">
          <div class="section-header">
            <span class="section-title">结题材料</span>
          </div>
          <el-row :gutter="32">
            <el-col :span="12">
              <el-form-item label="结题报告" prop="final_report">
                <el-upload
                  action="#"
                  :auto-upload="false"
                  :on-change="handleReportChange"
                  :file-list="reportFileList"
                  :limit="1"
                  accept=".pdf,.doc,.docx"
                  class="upload-demo w-full"
                  drag
                >
                  <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                  <div class="el-upload__text">
                    拖拽上传结题报告 (PDF/Word) <em>点击上传</em>
                  </div>
                </el-upload>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="支撑附件" prop="achievement_file">
                <el-upload
                  action="#"
                  :auto-upload="false"
                  :on-change="handleAchievementFileChange"
                  :file-list="achievementFileList"
                  :limit="1"
                  accept=".zip,.rar,.pdf,.doc,.docx"
                  class="upload-demo w-full"
                  drag
                >
                  <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                  <div class="el-upload__text">
                    拖拽上传其他附件 (ZIP/PDF/Word) <em>点击上传</em>
                  </div>
                </el-upload>
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <!-- Achievements List -->
        <div class="form-section">
          <div class="section-header">
            <span class="section-title">项目成果列表</span>
            <el-button
              type="primary"
              plain
              size="small"
              :icon="Plus"
              @click="openAchievementDialog()"
              >添加成果</el-button
            >
          </div>

          <el-table
            :data="achievements"
            border
            style="width: 100%; margin-top: 12px"
            :header-cell-style="{ background: '#f8fafc', color: '#475569' }"
          >
            <el-table-column
              type="index"
              label="序号"
              width="60"
              align="center"
            />
            <el-table-column prop="achievement_type" label="类型" width="100">
              <template #default="{ row }">
                <el-tag size="small">{{
                  getLabel(DICT_CODES.ACHIEVEMENT_TYPE, row.achievement_type)
                }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column
              prop="title"
              label="成果名称"
              show-overflow-tooltip
            />
            <el-table-column
              prop="description"
              label="描述/备注"
              show-overflow-tooltip
            />
            <el-table-column label="附件" width="100" align="center">
              <template #default="{ row }">
                <el-tag v-if="row.file" type="success" size="small"
                  >已选择</el-tag
                >
                <el-link
                  v-else-if="row.attachment_url"
                  type="primary"
                  class="text-xs"
                  @click="downloadAchievementAttachment(row)"
                  >已上传</el-link
                >
                <span v-else class="text-gray-400 text-xs">无</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" align="center">
              <template #default="{ row, $index }">
                <el-button
                  link
                  type="primary"
                  @click="openAchievementDialog(row, $index)"
                  >编辑</el-button
                >
                <el-button link type="danger" @click="removeAchievement($index)"
                  >删除</el-button
                >
              </template>
            </el-table-column>
            <template #empty>
              <div class="empty-text">暂无成果，请点击上方按钮添加</div>
            </template>
          </el-table>
        </div>
      </el-form>

      <!-- Achievement Dialog -->
      <el-dialog
        v-model="dialogVisible"
        :title="dialogIndex === -1 ? '添加成果' : '编辑成果'"
        width="600px"
        destroy-on-close
        append-to-body
      >
        <el-form :model="achievementForm" label-width="100px">
          <el-form-item label="成果类型" required>
            <el-select
              v-model="achievementForm.achievement_type"
              placeholder="请选择类型"
              style="width: 100%"
            >
              <el-option
                v-for="item in achievementTypeOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="成果名称" required>
            <el-input
              v-model="achievementForm.title"
              placeholder="论文题目/专利名称/奖项名称"
            />
          </el-form-item>

          <!-- Type Specific Fields -->
          <template v-if="achievementForm.achievement_type === 'PAPER'">
            <el-form-item label="期刊/会议">
              <el-input
                v-model="achievementForm.journal"
                placeholder="发表期刊或会议名称"
              />
            </el-form-item>
            <el-form-item label="发表时间">
              <el-date-picker
                v-model="achievementForm.publication_date"
                type="date"
                placeholder="选择日期"
                style="width: 100%"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
            <el-form-item label="DOI">
              <el-input v-model="achievementForm.doi" placeholder="DOI号" />
            </el-form-item>
            <el-form-item label="作者列表">
              <el-input
                v-model="achievementForm.authors"
                placeholder="所有作者，用逗号分隔"
              />
            </el-form-item>
          </template>

          <template v-if="achievementForm.achievement_type === 'PATENT'">
            <el-form-item label="专利号">
              <el-input v-model="achievementForm.patent_no" />
            </el-form-item>
            <el-form-item label="专利类型">
              <el-input
                v-model="achievementForm.patent_type"
                placeholder="如：发明专利、实用新型"
              />
            </el-form-item>
            <el-form-item label="申请人">
              <el-input v-model="achievementForm.applicant" />
            </el-form-item>
          </template>

          <template
            v-if="achievementForm.achievement_type === 'COMPETITION_AWARD'"
          >
            <el-form-item label="竞赛名称">
              <el-input v-model="achievementForm.competition_name" />
            </el-form-item>
            <el-form-item label="获奖等级">
              <el-input
                v-model="achievementForm.award_level"
                placeholder="如：国家级一等奖"
              />
            </el-form-item>
            <el-form-item label="获奖日期">
              <el-date-picker
                v-model="achievementForm.award_date"
                type="date"
                placeholder="选择日期"
                style="width: 100%"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </template>

          <template v-if="isCompanyType">
            <el-form-item label="公司名称">
              <el-input
                v-model="achievementForm.company_name"
                placeholder="请输入公司名称"
              />
            </el-form-item>
            <el-form-item label="角色/职责">
              <el-input
                v-model="achievementForm.company_role"
                placeholder="如：法人/技术负责人"
              />
            </el-form-item>
            <el-form-item label="成立日期">
              <el-date-picker
                v-model="achievementForm.company_date"
                type="date"
                placeholder="选择日期"
                style="width: 100%"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </template>

          <template v-if="isConferenceType">
            <el-form-item label="会议名称">
              <el-input
                v-model="achievementForm.conference_name"
                placeholder="请输入会议名称"
              />
            </el-form-item>
            <el-form-item label="会议级别">
              <el-input
                v-model="achievementForm.conference_level"
                placeholder="如：国际会议/国内会议"
              />
            </el-form-item>
            <el-form-item label="会议日期">
              <el-date-picker
                v-model="achievementForm.conference_date"
                type="date"
                placeholder="选择日期"
                style="width: 100%"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </template>

          <template v-if="isReportType">
            <el-form-item label="报告名称">
              <el-input
                v-model="achievementForm.report_title"
                placeholder="请输入报告名称"
              />
            </el-form-item>
            <el-form-item label="报告类型">
              <el-input
                v-model="achievementForm.report_type"
                placeholder="如：研究报告/调查报告"
              />
            </el-form-item>
          </template>

          <template v-if="isMediaType">
            <el-form-item label="作品名称">
              <el-input
                v-model="achievementForm.media_title"
                placeholder="请输入作品名称"
              />
            </el-form-item>
            <el-form-item label="作品形式">
              <el-input
                v-model="achievementForm.media_format"
                placeholder="如：视频/音频/多媒体"
              />
            </el-form-item>
            <el-form-item label="作品链接">
              <el-input
                v-model="achievementForm.media_link"
                placeholder="可填写网盘或展示链接"
              />
            </el-form-item>
          </template>

          <el-form-item label="描述/备注">
            <el-input
              type="textarea"
              v-model="achievementForm.description"
              :rows="2"
            />
          </el-form-item>

          <el-form-item label="成果附件">
            <el-upload
              action="#"
              :auto-upload="false"
              :on-change="handleDialogFileChange"
              :file-list="dialogFileList"
              :limit="1"
              class="w-full"
            >
              <el-button type="primary" link>点击上传附件</el-button>
              <template #tip>
                <div class="el-upload__tip">PDF/Word/图片/压缩包</div>
              </template>
            </el-upload>
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmAchievement">确定</el-button>
        </template>
      </el-dialog>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { Plus, UploadFilled } from "@element-plus/icons-vue";

import { useClosureApply } from "./hooks/useClosureApply";

defineOptions({
  name: "StudentClosureApplyView",
});

const {
  achievementFileList,
  achievementForm,
  achievementTypeOptions,
  achievements,
  DICT_CODES,
  dialogFileList,
  dialogIndex,
  dialogVisible,
  formData,
  formRef,
  getLabel,
  handleAchievementFileChange,
  handleDialogFileChange,
  handleReportChange,
  isCompanyType,
  isConferenceType,
  isMediaType,
  isReportType,
  loading,
  openAchievementDialog,
  projectInfo,
  reportFileList,
  router,
  rules,
  saveAsDraft,
  submitForm,
  canDeleteSubmission,
  handleDeleteSubmission,
  confirmAchievement,
  downloadAchievementAttachment,
  removeAchievement,
} = useClosureApply();

// Used by template ref="formRef"
void formRef;
</script>

<style scoped lang="scss">
@use "./Apply.scss";
</style>
