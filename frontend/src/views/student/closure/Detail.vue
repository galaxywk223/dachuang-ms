<template>
  <div class="closure-detail-page">
    <el-card class="main-card" shadow="never" v-loading="loading">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="header-title">结题详情</span>
            <el-tag
              :type="getStatusType(projectInfo.status)"
              size="small"
              effect="plain"
              round
              class="ml-3"
            >
              {{ projectInfo.status_display }}
            </el-tag>
          </div>
          <div class="header-actions">
            <el-button @click="handleBack">返回</el-button>
            <el-button
              v-if="projectInfo.status === 'CLOSED'"
              type="success"
              @click="handleDownloadCertificate"
            >
              下载结题证书
            </el-button>
          </div>
        </div>
      </template>

      <!-- 项目基本信息 -->
      <div class="info-section">
        <div class="section-header">
          <span class="section-title">项目基本信息</span>
        </div>
        <el-descriptions :column="3" border class="section-content">
          <el-descriptions-item label="项目名称" :span="3">
            {{ projectInfo.title }}
          </el-descriptions-item>
          <el-descriptions-item label="项目编号">
            {{ projectInfo.project_no || "-" }}
          </el-descriptions-item>
          <el-descriptions-item label="项目级别">
            {{ projectInfo.level_display || "-" }}
          </el-descriptions-item>
          <el-descriptions-item label="项目类别">
            {{ projectInfo.category_display || "-" }}
          </el-descriptions-item>
          <el-descriptions-item label="负责人">
            {{ projectInfo.leader_name || "-" }}
          </el-descriptions-item>
          <el-descriptions-item label="负责人学号">
            {{ projectInfo.leader_student_id || "-" }}
          </el-descriptions-item>
          <el-descriptions-item label="联系电话">
            {{ projectInfo.leader_contact || "-" }}
          </el-descriptions-item>
          <el-descriptions-item label="电子邮箱">
            {{ projectInfo.leader_email || "-" }}
          </el-descriptions-item>
          <el-descriptions-item label="学院">
            {{ projectInfo.college || "-" }}
          </el-descriptions-item>
          <el-descriptions-item label="项目经费">
            {{ projectInfo.budget || 0 }} 元
          </el-descriptions-item>
          <el-descriptions-item
            label="结题申请时间"
            v-if="projectInfo.closure_applied_at"
          >
            {{ formatDateTime(projectInfo.closure_applied_at) }}
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 指导教师信息 -->
      <div
        class="info-section"
        v-if="projectInfo.advisors_info && projectInfo.advisors_info.length > 0"
      >
        <div class="section-header">
          <span class="section-title">指导教师</span>
        </div>
        <el-table
          :data="projectInfo.advisors_info"
          border
          class="section-content"
          :header-cell-style="{ background: '#f8fafc', color: '#475569' }"
        >
          <el-table-column
            type="index"
            label="序号"
            width="60"
            align="center"
          />
          <el-table-column prop="name" label="姓名" align="center" />
          <el-table-column prop="job_number" label="工号" align="center" />
          <el-table-column prop="title" label="职称" align="center" />
          <el-table-column prop="contact" label="联系电话" align="center" />
          <el-table-column
            prop="email"
            label="电子邮箱"
            align="center"
            show-overflow-tooltip
          />
        </el-table>
      </div>

      <!-- 项目成员信息 -->
      <div
        class="info-section"
        v-if="projectInfo.members_info && projectInfo.members_info.length > 0"
      >
        <div class="section-header">
          <span class="section-title">项目成员</span>
        </div>
        <el-table
          :data="projectInfo.members_info"
          border
          class="section-content"
          :header-cell-style="{ background: '#f8fafc', color: '#475569' }"
        >
          <el-table-column
            type="index"
            label="序号"
            width="60"
            align="center"
          />
          <el-table-column label="姓名" align="center">
            <template #default="{ row }">
              {{ row.user_name || row.name || "-" }}
            </template>
          </el-table-column>
          <el-table-column prop="student_id" label="学号" align="center" />
          <el-table-column label="角色" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.role === 'LEADER'" type="danger" size="small"
                >负责人</el-tag
              >
              <el-tag v-else type="info" size="small">成员</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 结题材料 -->
      <div class="info-section">
        <div class="section-header">
          <span class="section-title">结题材料</span>
        </div>
        <div class="section-content">
          <el-descriptions :column="1" border>
            <el-descriptions-item label="结题报告">
              <div v-if="projectInfo.final_report_url" class="file-item">
                <span class="file-name">{{
                  projectInfo.final_report_name || "结题报告"
                }}</span>
                <el-button
                  type="primary"
                  link
                  size="small"
                  @click="
                    handleDownload(
                      projectInfo.final_report_url,
                      projectInfo.final_report_name
                    )
                  "
                >
                  下载
                </el-button>
              </div>
              <span v-else class="text-gray-400">未上传</span>
            </el-descriptions-item>
            <el-descriptions-item label="支撑附件">
              <div v-if="projectInfo.achievement_file_url" class="file-item">
                <span class="file-name">{{
                  projectInfo.achievement_file_name || "附件"
                }}</span>
                <el-button
                  type="primary"
                  link
                  size="small"
                  @click="
                    handleDownload(
                      projectInfo.achievement_file_url,
                      projectInfo.achievement_file_name
                    )
                  "
                >
                  下载
                </el-button>
              </div>
              <span v-else class="text-gray-400">未上传</span>
            </el-descriptions-item>
            <el-descriptions-item label="成果简介">
              <div class="achievement-summary">
                {{ projectInfo.achievement_summary || "暂无" }}
              </div>
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>

      <!-- 项目成果列表 -->
      <div class="info-section">
        <div class="section-header">
          <span class="section-title">项目成果列表</span>
          <el-tag type="info" size="small" class="ml-2"
            >共 {{ achievements.length }} 项</el-tag
          >
        </div>
        <el-table
          :data="achievements"
          border
          class="section-content"
          :header-cell-style="{ background: '#f8fafc', color: '#475569' }"
          empty-text="暂无成果"
        >
          <el-table-column
            type="index"
            label="序号"
            width="60"
            align="center"
          />
          <el-table-column label="成果类型" width="120" align="center">
            <template #default="{ row }">
              <el-tag size="small">
                {{
                  row.achievement_type_display ||
                  getLabel(DICT_CODES.ACHIEVEMENT_TYPE, row.achievement_type) ||
                  "-"
                }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column
            prop="title"
            label="成果名称"
            min-width="180"
            show-overflow-tooltip
          />
          <el-table-column
            label="详细信息"
            min-width="200"
            show-overflow-tooltip
          >
            <template #default="{ row }">
              <div v-if="row.achievement_type === 'PAPER'">
                <div v-if="row.journal">期刊: {{ row.journal }}</div>
                <div v-if="row.authors">作者: {{ row.authors }}</div>
                <div v-if="row.publication_date">
                  发表时间: {{ row.publication_date }}
                </div>
                <div v-if="row.doi">DOI: {{ row.doi }}</div>
              </div>
              <div v-else-if="row.achievement_type === 'PATENT'">
                <div v-if="row.patent_no">专利号: {{ row.patent_no }}</div>
                <div v-if="row.patent_type">类型: {{ row.patent_type }}</div>
                <div v-if="row.applicant">申请人: {{ row.applicant }}</div>
              </div>
              <div v-else-if="row.achievement_type === 'COMPETITION_AWARD'">
                <div v-if="row.competition_name">
                  竞赛: {{ row.competition_name }}
                </div>
                <div v-if="row.award_level">等级: {{ row.award_level }}</div>
                <div v-if="row.award_date">获奖日期: {{ row.award_date }}</div>
              </div>
              <div v-else-if="isCompanyType(row.achievement_type)">
                <div v-if="getExtraData(row, 'company_name')">
                  公司: {{ getExtraData(row, "company_name") }}
                </div>
                <div v-if="getExtraData(row, 'company_role')">
                  角色: {{ getExtraData(row, "company_role") }}
                </div>
                <div v-if="getExtraData(row, 'company_date')">
                  日期: {{ getExtraData(row, "company_date") }}
                </div>
              </div>
              <div v-else-if="isConferenceType(row.achievement_type)">
                <div v-if="getExtraData(row, 'conference_name')">
                  会议: {{ getExtraData(row, "conference_name") }}
                </div>
                <div v-if="getExtraData(row, 'conference_level')">
                  级别: {{ getExtraData(row, "conference_level") }}
                </div>
                <div v-if="getExtraData(row, 'conference_date')">
                  日期: {{ getExtraData(row, "conference_date") }}
                </div>
              </div>
              <div v-else-if="isReportType(row.achievement_type)">
                <div v-if="getExtraData(row, 'report_title')">
                  报告: {{ getExtraData(row, "report_title") }}
                </div>
                <div v-if="getExtraData(row, 'report_type')">
                  类型: {{ getExtraData(row, "report_type") }}
                </div>
              </div>
              <div v-else-if="isMediaType(row.achievement_type)">
                <div v-if="getExtraData(row, 'media_title')">
                  作品: {{ getExtraData(row, "media_title") }}
                </div>
                <div v-if="getExtraData(row, 'media_format')">
                  形式: {{ getExtraData(row, "media_format") }}
                </div>
                <div v-if="getExtraData(row, 'media_link')">
                  <el-link
                    :href="getExtraData(row, 'media_link')"
                    target="_blank"
                    type="primary"
                    >查看链接</el-link
                  >
                </div>
              </div>
              <div v-else class="text-gray-400">-</div>
            </template>
          </el-table-column>
          <el-table-column
            prop="description"
            label="描述/备注"
            min-width="150"
            show-overflow-tooltip
          />
          <el-table-column label="附件" width="100" align="center">
            <template #default="{ row }">
              <el-link
                v-if="row.attachment_url"
                :href="row.attachment_url"
                target="_blank"
                type="primary"
                size="small"
              >
                查看
              </el-link>
              <span v-else class="text-gray-400">无</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { useClosureDetail } from "./hooks/useClosureDetail";

defineOptions({
  name: "StudentClosureDetailView",
});

const {
  loading,
  projectInfo,
  achievements,
  DICT_CODES,
  getLabel,
  handleDownload,
  handleDownloadCertificate,
  handleBack,
} = useClosureDetail();

// 辅助函数
const formatDateTime = (dateStr: string) => {
  if (!dateStr) return "-";
  const date = new Date(dateStr);
  return date.toLocaleString("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
};

const getStatusType = (status?: string) => {
  if (!status) return "info";
  const statusMap: Record<string, string> = {
    CLOSED: "success",
    CLOSURE_SUBMITTED: "warning",
    CLOSURE_LEVEL2_REVIEWING: "warning",
    CLOSURE_LEVEL1_REVIEWING: "warning",
    CLOSURE_LEVEL2_APPROVED: "success",
    CLOSURE_LEVEL1_APPROVED: "success",
    CLOSURE_LEVEL2_REJECTED: "danger",
    CLOSURE_LEVEL1_REJECTED: "danger",
    CLOSURE_RETURNED: "warning",
  };
  return statusMap[status] || "info";
};

const COMPANY_TYPES = ["COMPANY", "STARTUP", "COMPANY_FORMATION"];
const CONFERENCE_TYPES = ["CONFERENCE", "ACADEMIC_CONFERENCE"];
const REPORT_TYPES = ["REPORT", "RESEARCH_REPORT", "SURVEY_REPORT"];
const MEDIA_TYPES = ["MULTIMEDIA", "AUDIO_VIDEO", "VIDEO"];

const isCompanyType = (type?: string) => type && COMPANY_TYPES.includes(type);
const isConferenceType = (type?: string) =>
  type && CONFERENCE_TYPES.includes(type);
const isReportType = (type?: string) => type && REPORT_TYPES.includes(type);
const isMediaType = (type?: string) => type && MEDIA_TYPES.includes(type);

const getExtraData = (
  row: { extra_data?: Record<string, string> },
  key: string
) => {
  return row.extra_data?.[key] || "";
};
</script>

<style scoped lang="scss">
.closure-detail-page {
  padding: 20px;

  .main-card {
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      .header-left {
        display: flex;
        align-items: center;
        gap: 8px;

        .header-title {
          font-size: 18px;
          font-weight: 600;
          color: #1f2937;
        }
      }

      .header-actions {
        display: flex;
        gap: 8px;
      }
    }
  }

  .info-section {
    margin-bottom: 24px;

    &:last-child {
      margin-bottom: 0;
    }

    .section-header {
      display: flex;
      align-items: center;
      margin-bottom: 16px;
      padding-bottom: 8px;
      border-bottom: 2px solid #e5e7eb;

      .section-title {
        font-size: 16px;
        font-weight: 600;
        color: #374151;
      }
    }

    .section-content {
      margin-top: 12px;
    }

    .file-item {
      display: flex;
      align-items: center;
      gap: 12px;

      .file-name {
        flex: 1;
        color: #4b5563;
      }
    }

    .achievement-summary {
      line-height: 1.6;
      color: #4b5563;
      white-space: pre-wrap;
      word-break: break-word;
    }
  }

  .text-gray-400 {
    color: #9ca3af;
  }

  .ml-2 {
    margin-left: 8px;
  }

  .ml-3 {
    margin-left: 12px;
  }
}
</style>
