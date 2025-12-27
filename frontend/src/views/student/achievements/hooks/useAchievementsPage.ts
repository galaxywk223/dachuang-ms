import { computed, onMounted, reactive, ref } from "vue";
import dayjs from "dayjs";
import { ElMessage, ElMessageBox, type FormInstance, type UploadFile } from "element-plus";

import {
  addProjectAchievement,
  getMyProjects,
  getProjectAchievementList,
  removeProjectAchievement,
} from "@/api/projects";
import { DICT_CODES } from "@/api/dictionaries";
import { useDictionary } from "@/composables/useDictionary";

export function useAchievementsPage() {
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
  const achievementTypeOptions = computed(
    () => getOptions(DICT_CODES.ACHIEVEMENT_TYPE) as any[]
  );

  const activeProject = computed(
    () => projects.value.find((item) => item.id === activeProjectId.value) || null
  );

  const selectedType = computed(() => {
    if (!form.achievement_type) return null;
    const target = String(form.achievement_type);
    return (
      achievementTypeOptions.value.find(
        (item) => String(item.id ?? item.value) === target
      ) || null
    );
  });

  const selectedTypeValue = computed(() => selectedType.value?.value || "");

  const COMPANY_TYPES = ["COMPANY", "STARTUP", "COMPANY_FORMATION"];
  const CONFERENCE_TYPES = ["CONFERENCE", "ACADEMIC_CONFERENCE"];
  const REPORT_TYPES = ["REPORT", "RESEARCH_REPORT", "SURVEY_REPORT"];
  const MEDIA_TYPES = ["MULTIMEDIA", "AUDIO_VIDEO", "VIDEO"];

  const isCompanyType = computed(() =>
    COMPANY_TYPES.includes(selectedTypeValue.value)
  );
  const isConferenceType = computed(() =>
    CONFERENCE_TYPES.includes(selectedTypeValue.value)
  );
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
      if (!form.competition_name || !form.award_level) {
        return "竞赛成果需填写竞赛名称和获奖等级";
      }
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
        if (form.publication_date) {
          payload.append("publication_date", form.publication_date);
        }
        if (form.doi) payload.append("doi", form.doi);
        if (form.patent_no) payload.append("patent_no", form.patent_no);
        if (form.patent_type) payload.append("patent_type", form.patent_type);
        if (form.applicant) payload.append("applicant", form.applicant);
        if (form.copyright_no) payload.append("copyright_no", form.copyright_no);
        if (form.copyright_owner) {
          payload.append("copyright_owner", form.copyright_owner);
        }
        if (form.competition_name) {
          payload.append("competition_name", form.competition_name);
        }
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
          if (form.conference_level) {
            extraData.conference_level = form.conference_level;
          }
          if (form.conference_date) {
            extraData.conference_date = form.conference_date;
          }
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

  return {
    achievements,
    activeProject,
    activeProjectId,
    canAdd,
    currentAchievement,
    dialogVisible,
    form,
    formRef,
    formatDate,
    handleDelete,
    handleFileChange,
    handleFileRemove,
    handleProjectChange,
    handleView,
    isCompanyType,
    isConferenceType,
    isMediaType,
    isReportType,
    listLoading,
    loading,
    openDialog,
    projects,
    rules,
    achievementTypeOptions,
    resetForm,
    selectedTypeValue,
    submitAchievement,
    submitting,
    viewDialogVisible,
    fileList,
  };
}
