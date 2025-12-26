<template>
  <div class="achievements-page">
    <el-card class="main-card" shadow="never" v-loading="loading">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="header-title">成果管理</span>
            <el-tag v-if="activeProject" size="small" effect="plain" type="info" class="ml-3">
              {{ activeProject.title }}
            </el-tag>
          </div>
          <div class="header-actions">
            <el-select
              v-model="activeProjectId"
              placeholder="选择项目"
              filterable
              clearable
              style="width: 260px"
              @change="handleProjectChange"
            >
              <el-option
                v-for="item in projects"
                :key="item.id"
                :label="`${item.project_no || ''} ${item.title}`"
                :value="item.id"
              />
            </el-select>
            <el-tooltip
              :content="canAdd ? '新增成果' : '当前项目状态不允许新增成果'"
              placement="top"
            >
              <el-button type="primary" :disabled="!canAdd" @click="openDialog">
                新增成果
              </el-button>
            </el-tooltip>
          </div>
        </div>
      </template>

      <div v-if="projects.length === 0" class="empty-container">
        <el-empty description="暂无可管理的项目" />
      </div>

      <div v-else>
        <el-alert
          title="项目立项后可持续登记成果，支持在线预览与附件上传"
          type="info"
          show-icon
          :closable="false"
          class="mb-4"
        />

        <el-table
          v-loading="listLoading"
          :data="achievements"
          stripe
          border
          style="width: 100%"
          :header-cell-style="{ background: '#f8fafc', color: '#475569' }"
        >
          <el-table-column prop="achievement_type_display" label="类型" width="140" />
          <el-table-column prop="title" label="成果名称" min-width="220" show-overflow-tooltip />
          <el-table-column prop="description" label="成果描述" min-width="240" show-overflow-tooltip />
          <el-table-column label="附件" width="120" align="center">
            <template #default="{ row }">
              <el-link v-if="row.attachment" :href="row.attachment" target="_blank" type="primary">查看</el-link>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column label="登记时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="160" align="center" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="handleView(row)">详情</el-button>
              <el-button link type="danger" @click="handleDelete(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-empty
          v-if="!listLoading && achievements.length === 0"
          description="暂无成果记录"
          :image-size="160"
          class="mt-4"
        />
      </div>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      title="新增成果"
      width="720px"
      destroy-on-close
      @closed="resetForm"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="110px">
        <el-form-item label="成果类型" prop="achievement_type">
          <el-select v-model="form.achievement_type" placeholder="请选择类型" style="width: 100%">
            <el-option
              v-for="item in achievementTypeOptions"
              :key="item.id || item.value"
              :label="item.label"
              :value="item.id || item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="成果名称" prop="title">
          <el-input v-model="form.title" placeholder="请输入成果名称" />
        </el-form-item>
        <el-form-item label="成果描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            maxlength="200"
            show-word-limit
            placeholder="简要描述成果内容"
          />
        </el-form-item>

        <template v-if="selectedTypeValue === 'PAPER'">
          <el-form-item label="作者" required>
            <el-input v-model="form.authors" placeholder="作者，用逗号分隔" />
          </el-form-item>
          <el-form-item label="期刊/会议" required>
            <el-input v-model="form.journal" placeholder="期刊或会议名称" />
          </el-form-item>
          <el-form-item label="发表日期">
            <el-date-picker
              v-model="form.publication_date"
              type="date"
              placeholder="选择日期"
              style="width: 100%"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>
          <el-form-item label="DOI">
            <el-input v-model="form.doi" placeholder="请输入DOI号" />
          </el-form-item>
        </template>

        <template v-if="selectedTypeValue === 'PATENT'">
          <el-form-item label="专利号">
            <el-input v-model="form.patent_no" placeholder="请输入专利号" />
          </el-form-item>
          <el-form-item label="专利类型">
            <el-input v-model="form.patent_type" placeholder="如：发明专利" />
          </el-form-item>
          <el-form-item label="申请人" required>
            <el-input v-model="form.applicant" placeholder="请输入申请人" />
          </el-form-item>
        </template>

        <template v-if="selectedTypeValue === 'SOFTWARE_COPYRIGHT'">
          <el-form-item label="登记号">
            <el-input v-model="form.copyright_no" placeholder="请输入登记号" />
          </el-form-item>
          <el-form-item label="著作权人" required>
            <el-input v-model="form.copyright_owner" placeholder="请输入著作权人" />
          </el-form-item>
        </template>

        <template v-if="selectedTypeValue === 'COMPETITION_AWARD'">
          <el-form-item label="竞赛名称" required>
            <el-input v-model="form.competition_name" placeholder="请输入竞赛名称" />
          </el-form-item>
          <el-form-item label="获奖等级" required>
            <el-input v-model="form.award_level" placeholder="如：国家级一等奖" />
          </el-form-item>
          <el-form-item label="获奖日期">
            <el-date-picker
              v-model="form.award_date"
              type="date"
              placeholder="选择日期"
              style="width: 100%"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>
        </template>

        <template v-if="isCompanyType">
          <el-form-item label="公司名称" required>
            <el-input v-model="form.company_name" placeholder="请输入公司名称" />
          </el-form-item>
          <el-form-item label="角色/职责">
            <el-input v-model="form.company_role" placeholder="如：法人/技术负责人" />
          </el-form-item>
          <el-form-item label="成立日期">
            <el-date-picker
              v-model="form.company_date"
              type="date"
              placeholder="选择日期"
              style="width: 100%"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>
        </template>

        <template v-if="isConferenceType">
          <el-form-item label="会议名称" required>
            <el-input v-model="form.conference_name" placeholder="请输入会议名称" />
          </el-form-item>
          <el-form-item label="会议级别">
            <el-input v-model="form.conference_level" placeholder="如：国际会议/国内会议" />
          </el-form-item>
          <el-form-item label="会议日期">
            <el-date-picker
              v-model="form.conference_date"
              type="date"
              placeholder="选择日期"
              style="width: 100%"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>
        </template>

        <template v-if="isReportType">
          <el-form-item label="报告名称" required>
            <el-input v-model="form.report_title" placeholder="请输入报告名称" />
          </el-form-item>
          <el-form-item label="报告类型">
            <el-input v-model="form.report_type" placeholder="如：研究报告/调查报告" />
          </el-form-item>
        </template>

        <template v-if="isMediaType">
          <el-form-item label="作品名称" required>
            <el-input v-model="form.media_title" placeholder="请输入作品名称" />
          </el-form-item>
          <el-form-item label="作品形式">
            <el-input v-model="form.media_format" placeholder="如：视频/音频/多媒体" />
          </el-form-item>
          <el-form-item label="作品链接">
            <el-input v-model="form.media_link" placeholder="可填写网盘或展示链接" />
          </el-form-item>
        </template>

        <el-form-item label="成果附件">
          <el-upload
            class="upload-block"
            drag
            action=""
            :auto-upload="false"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            :file-list="fileList"
            :limit="1"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">拖拽文件到此处或 <em>点击上传</em></div>
            <template #tip>
              <div class="el-upload__tip">支持PDF/图片/压缩包</div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="submitting" @click="submitAchievement">提交</el-button>
        </span>
      </template>
    </el-dialog>

    <el-dialog v-model="viewDialogVisible" title="成果详情" width="640px">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="成果类型">
          {{ currentAchievement?.achievement_type_display || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="成果名称">
          {{ currentAchievement?.title || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="成果描述">
          {{ currentAchievement?.description || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="作者/申请人">
          {{ currentAchievement?.authors || currentAchievement?.applicant || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="期刊/会议">
          {{ currentAchievement?.journal || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="专利/软著信息">
          {{ currentAchievement?.patent_no || currentAchievement?.copyright_no || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="竞赛信息">
          {{ currentAchievement?.competition_name || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="附件">
          <el-link v-if="currentAchievement?.attachment" :href="currentAchievement.attachment" target="_blank" type="primary">
            点击查看
          </el-link>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="扩展信息">
          <pre v-if="currentAchievement?.extra_data" class="extra-data">{{ JSON.stringify(currentAchievement.extra_data, null, 2) }}</pre>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="登记时间">
          {{ formatDate(currentAchievement?.created_at) }}
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from "vue";
import dayjs from "dayjs";
import { ElMessage, ElMessageBox, type FormInstance, type UploadFile } from "element-plus";
import { UploadFilled } from "@element-plus/icons-vue";
import { getMyProjects, getProjectAchievementList, addProjectAchievement, removeProjectAchievement } from "@/api/project";
import { useDictionary } from "@/composables/useDictionary";
import { DICT_CODES } from "@/api/dictionary";

const loading = ref(false);
const listLoading = ref(false);
const projects = ref<any[]>([]);
const achievements = ref<any[]>([]);
const activeProjectId = ref<number | null>(null);

const dialogVisible = ref(false);
const viewDialogVisible = ref(false);
const submitting = ref(false);
const currentAchievement = ref<any>(null);
const fileList = ref<UploadFile[]>([]);
const formRef = ref<FormInstance>();

const form = reactive({
  achievement_type: "",
  title: "",
  description: "",
  authors: "",
  journal: "",
  publication_date: "",
  doi: "",
  patent_no: "",
  patent_type: "",
  applicant: "",
  copyright_no: "",
  copyright_owner: "",
  competition_name: "",
  award_level: "",
  award_date: "",
  company_name: "",
  company_role: "",
  company_date: "",
  conference_name: "",
  conference_level: "",
  conference_date: "",
  report_title: "",
  report_type: "",
  media_title: "",
  media_format: "",
  media_link: "",
  attachment: null as File | null,
});

const rules = {
  achievement_type: [{ required: true, message: "请选择成果类型", trigger: "change" }],
  title: [{ required: true, message: "请输入成果名称", trigger: "blur" }],
  description: [{ required: true, message: "请输入成果描述", trigger: "blur" }],
};

const { loadDictionaries, getOptions } = useDictionary();
const achievementTypeOptions = computed(() => getOptions(DICT_CODES.ACHIEVEMENT_TYPE) as any[]);

const activeProject = computed(() =>
  projects.value.find((item) => item.id === activeProjectId.value) || null
);

const selectedType = computed(() => {
  if (!form.achievement_type) return null;
  const target = String(form.achievement_type);
  return achievementTypeOptions.value.find((item) => String(item.id ?? item.value) === target) || null;
});

const selectedTypeValue = computed(() => selectedType.value?.value || "");

const COMPANY_TYPES = ["COMPANY", "STARTUP", "COMPANY_FORMATION"];
const CONFERENCE_TYPES = ["CONFERENCE", "ACADEMIC_CONFERENCE"];
const REPORT_TYPES = ["REPORT", "RESEARCH_REPORT", "SURVEY_REPORT"];
const MEDIA_TYPES = ["MULTIMEDIA", "AUDIO_VIDEO", "VIDEO"];

const isCompanyType = computed(() => COMPANY_TYPES.includes(selectedTypeValue.value));
const isConferenceType = computed(() => CONFERENCE_TYPES.includes(selectedTypeValue.value));
const isReportType = computed(() => REPORT_TYPES.includes(selectedTypeValue.value));
const isMediaType = computed(() => MEDIA_TYPES.includes(selectedTypeValue.value));

const canAdd = computed(() => {
  if (!activeProject.value) return false;
  const allowedStatuses = ["IN_PROGRESS", "CLOSURE_DRAFT", "CLOSURE_SUBMITTED"];
  return allowedStatuses.includes(activeProject.value.status);
});

const formatDate = (date?: string) => {
  if (!date) return "-";
  return dayjs(date).format("YYYY-MM-DD HH:mm");
};

const fetchProjects = async () => {
  loading.value = true;
  try {
    const response: any = await getMyProjects({});
    if (response.code === 200) {
      projects.value = response.data || [];
      if (!activeProjectId.value && projects.value.length > 0) {
        activeProjectId.value = projects.value[0].id;
      }
    }
  } catch (error: any) {
    ElMessage.error(error.message || "获取项目列表失败");
  } finally {
    loading.value = false;
  }
};

const fetchAchievements = async () => {
  if (!activeProjectId.value) {
    achievements.value = [];
    return;
  }
  listLoading.value = true;
  try {
    const response: any = await getProjectAchievementList(activeProjectId.value);
    if (response.code === 200) {
      achievements.value = response.data || [];
    } else {
      achievements.value = [];
    }
  } catch (error: any) {
    ElMessage.error(error.message || "获取成果列表失败");
  } finally {
    listLoading.value = false;
  }
};

const handleProjectChange = () => {
  fetchAchievements();
};

const openDialog = () => {
  if (!canAdd.value) {
    ElMessage.warning("当前项目状态不允许新增成果");
    return;
  }
  dialogVisible.value = true;
};

const handleFileChange = (file: UploadFile) => {
  if (file.raw) {
    form.attachment = file.raw;
    fileList.value = [file];
  }
};

const handleFileRemove = () => {
  form.attachment = null;
  fileList.value = [];
};

const validateExtraFields = () => {
  if (selectedTypeValue.value === "PAPER") {
    if (!form.authors || !form.journal) return "论文成果需填写作者和期刊信息";
  }
  if (selectedTypeValue.value === "PATENT") {
    if (!form.applicant) return "专利成果需填写申请人";
  }
  if (selectedTypeValue.value === "SOFTWARE_COPYRIGHT") {
    if (!form.copyright_owner) return "软著成果需填写著作权人";
  }
  if (selectedTypeValue.value === "COMPETITION_AWARD") {
    if (!form.competition_name || !form.award_level) return "竞赛成果需填写竞赛名称和获奖等级";
  }
  if (isCompanyType.value) {
    if (!form.company_name) return "公司成果需填写公司名称";
  }
  if (isConferenceType.value) {
    if (!form.conference_name) return "会议成果需填写会议名称";
  }
  if (isReportType.value) {
    if (!form.report_title) return "报告成果需填写报告名称";
  }
  if (isMediaType.value) {
    if (!form.media_title) return "音视频成果需填写作品名称";
  }
  return "";
};

const submitAchievement = async () => {
  const projectId = activeProjectId.value;
  if (!formRef.value || projectId === null) return;
  await formRef.value.validate(async (valid) => {
    if (!valid) return;

    const extraError = validateExtraFields();
    if (extraError) {
      ElMessage.warning(extraError);
      return;
    }

    submitting.value = true;
    try {
      const payload = new FormData();
      payload.append("achievement_type", String(form.achievement_type));
      payload.append("title", form.title);
      payload.append("description", form.description);

      if (form.authors) payload.append("authors", form.authors);
      if (form.journal) payload.append("journal", form.journal);
      if (form.publication_date) payload.append("publication_date", form.publication_date);
      if (form.doi) payload.append("doi", form.doi);
      if (form.patent_no) payload.append("patent_no", form.patent_no);
      if (form.patent_type) payload.append("patent_type", form.patent_type);
      if (form.applicant) payload.append("applicant", form.applicant);
      if (form.copyright_no) payload.append("copyright_no", form.copyright_no);
      if (form.copyright_owner) payload.append("copyright_owner", form.copyright_owner);
      if (form.competition_name) payload.append("competition_name", form.competition_name);
      if (form.award_level) payload.append("award_level", form.award_level);
      if (form.award_date) payload.append("award_date", form.award_date);
      const extraData: Record<string, string> = {};
      if (isCompanyType.value) {
        extraData.company_name = form.company_name;
        if (form.company_role) extraData.company_role = form.company_role;
        if (form.company_date) extraData.company_date = form.company_date;
      }
      if (isConferenceType.value) {
        extraData.conference_name = form.conference_name;
        if (form.conference_level) extraData.conference_level = form.conference_level;
        if (form.conference_date) extraData.conference_date = form.conference_date;
      }
      if (isReportType.value) {
        extraData.report_title = form.report_title;
        if (form.report_type) extraData.report_type = form.report_type;
      }
      if (isMediaType.value) {
        extraData.media_title = form.media_title;
        if (form.media_format) extraData.media_format = form.media_format;
        if (form.media_link) extraData.media_link = form.media_link;
      }
      if (Object.keys(extraData).length > 0) {
        payload.append("extra_data", JSON.stringify(extraData));
      }
      if (form.attachment) payload.append("attachment", form.attachment);

      const response: any = await addProjectAchievement(projectId, payload);
      if (response.code === 200) {
        ElMessage.success("成果登记成功");
        dialogVisible.value = false;
        resetForm();
        fetchAchievements();
      } else {
        ElMessage.error(response.message || "提交失败");
      }
    } catch (error: any) {
      ElMessage.error(error.message || "提交失败");
    } finally {
      submitting.value = false;
    }
  });
};

const resetForm = () => {
  formRef.value?.resetFields();
  Object.assign(form, {
    achievement_type: "",
    title: "",
    description: "",
    authors: "",
    journal: "",
    publication_date: "",
    doi: "",
    patent_no: "",
    patent_type: "",
    applicant: "",
    copyright_no: "",
    copyright_owner: "",
    competition_name: "",
    award_level: "",
    award_date: "",
    company_name: "",
    company_role: "",
    company_date: "",
    conference_name: "",
    conference_level: "",
    conference_date: "",
    report_title: "",
    report_type: "",
    media_title: "",
    media_format: "",
    media_link: "",
    attachment: null,
  });
  fileList.value = [];
};

const handleView = (row: any) => {
  currentAchievement.value = row;
  viewDialogVisible.value = true;
};

const handleDelete = async (row: any) => {
  if (!activeProjectId.value) return;
  try {
    await ElMessageBox.confirm("确认删除该成果记录？", "提示", {
      type: "warning",
      confirmButtonText: "删除",
      cancelButtonText: "取消",
    });
    const response: any = await removeProjectAchievement(activeProjectId.value, row.id);
    if (response.code === 200) {
      ElMessage.success("删除成功");
      fetchAchievements();
    } else {
      ElMessage.error(response.message || "删除失败");
    }
  } catch {
    // cancel
  }
};

onMounted(async () => {
  await loadDictionaries([DICT_CODES.ACHIEVEMENT_TYPE]);
  await fetchProjects();
  await fetchAchievements();
});
</script>

@use "@/styles/variables.scss" as *;

.achievements-page {
  padding: 20px;
}

.main-card {
  border-radius: 8px;
  :deep(.el-card__header) {
      padding: 16px 20px;
      font-weight: 600;
      border-bottom: 1px solid $color-border-light;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.header-left {
    display: flex;
    align-items: center;
}

.header-title {
    font-size: 16px;
    color: $slate-800;
}

.header-actions {
    display: flex;
    align-items: center;
    gap: 12px;
}

.ml-3 {
    margin-left: 12px;
}

.mb-4 {
    margin-bottom: 16px;
}

.mt-4 {
    margin-top: 16px;
}

.extra-data {
    margin: 0;
    white-space: pre-wrap;
    word-break: break-word;
    font-size: 12px;
    color: #64748b;
}

