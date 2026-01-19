import { computed, onMounted, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  ElMessage,
  ElMessageBox,
  type FormInstance,
  type UploadFile,
} from "element-plus";

import {
  createClosureApplication,
  deleteClosureSubmission,
  getProjectAchievements,
  getProjectDetail,
  updateClosureApplication,
} from "@/api/projects";
import { DICT_CODES } from "@/api/dictionaries";
import { useDictionary } from "@/composables/useDictionary";

type ProjectDetail = {
  id: number;
  title?: string;
  project_no?: string;
  leader_name?: string;
  leader_info?: { real_name?: string };
  level_display?: string;
  level?: string;
  category_display?: string;
  category?: string;
  budget?: number;
  status?: string;
  final_report_url?: string;
  final_report_name?: string;
  achievement_file_url?: string;
  achievement_file_name?: string;
};

type AchievementItem = {
  id?: number | null;
  achievement_type?: string;
  achievement_type_value?: string;
  title?: string;
  description?: string;
  authors?: string;
  journal?: string;
  publication_date?: string;
  doi?: string;
  patent_no?: string;
  patent_type?: string;
  applicant?: string;
  competition_name?: string;
  award_level?: string;
  award_date?: string;
  company_name?: string;
  company_role?: string;
  company_date?: string;
  conference_name?: string;
  conference_level?: string;
  conference_date?: string;
  report_title?: string;
  report_type?: string;
  media_title?: string;
  media_format?: string;
  media_link?: string;
  extra_data?: Record<string, string>;
  attachment_url?: string;
  attachment_name?: string;
  attachment?: string;
  file?: File | null;
};

type ApiResponse<T> = {
  code?: number;
  status?: number;
  data?: T;
  message?: string;
};

const getErrorMessage = (error: unknown, fallback: string) => {
  if (error && typeof error === "object") {
    const err = error as {
      response?: { data?: { message?: string; detail?: string } };
      message?: string;
    };
    if (err.response?.data?.message) {
      return err.response.data.message;
    }
    if (err.response?.data?.detail) {
      return err.response.data.detail;
    }
    if (err.message) {
      return err.message;
    }
  }
  if (error instanceof Error) {
    return error.message || fallback;
  }
  if (typeof error === "string") {
    return error || fallback;
  }
  return fallback;
};

export function useClosureApply() {
  const route = useRoute();
  const router = useRouter();
  const formRef = ref<FormInstance>();
  const loading = ref(false);
  const project = ref<ProjectDetail | null>(null);
  const { loadDictionaries, getOptions, getLabel } = useDictionary();

  const projectId = route.query.projectId as string;

  const projectInfo = reactive({
    title: "",
    project_no: "",
    leader_name: "",
    level_display: "",
    category_display: "",
    budget: 0,
    status: "",
  });

  const formData = reactive({
    final_report: null as File | null,
    achievement_file: null as File | null,
  });

  const reportFileList = ref<UploadFile[]>([]);
  const achievementFileList = ref<UploadFile[]>([]);

  const achievements = ref<AchievementItem[]>([]);
  const dialogVisible = ref(false);
  const dialogIndex = ref(-1);
  const dialogFileList = ref<UploadFile[]>([]);
  const buildUploadFile = (
    name: string,
    status: UploadFile["status"],
    url?: string
  ): UploadFile => ({
    name,
    status,
    url,
    uid: Date.now(),
  });

  const achievementForm = reactive<AchievementItem>({
    id: null as number | null,
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
    extra_data: {},
    file: null,
  });

  const achievementTypeOptions = computed(() =>
    getOptions(DICT_CODES.ACHIEVEMENT_TYPE)
  );

  const selectedAchievementTypeValue = computed(
    () => achievementForm.achievement_type || ""
  );
  const COMPANY_TYPES = ["COMPANY", "STARTUP", "COMPANY_FORMATION"];
  const CONFERENCE_TYPES = ["CONFERENCE", "ACADEMIC_CONFERENCE"];
  const REPORT_TYPES = ["REPORT", "RESEARCH_REPORT", "SURVEY_REPORT"];
  const MEDIA_TYPES = ["MULTIMEDIA", "AUDIO_VIDEO", "VIDEO"];
  const isCompanyType = computed(() =>
    COMPANY_TYPES.includes(selectedAchievementTypeValue.value)
  );
  const isConferenceType = computed(() =>
    CONFERENCE_TYPES.includes(selectedAchievementTypeValue.value)
  );
  const isReportType = computed(() =>
    REPORT_TYPES.includes(selectedAchievementTypeValue.value)
  );
  const isMediaType = computed(() =>
    MEDIA_TYPES.includes(selectedAchievementTypeValue.value)
  );

  const rules = {
    final_report: [
      {
        validator: (
          _rule: unknown,
          _value: unknown,
          callback: (error?: Error) => void
        ) => {
          if (formData.final_report || project.value?.final_report_url) {
            callback();
            return;
          }
          callback(new Error("请上传结题报告"));
        },
        trigger: "change",
      },
    ],
  };

  const handleReportChange = (file: UploadFile) => {
    formData.final_report = file.raw as File;
    reportFileList.value = [file];
    if (file) formRef.value?.clearValidate("final_report");
  };

  const handleAchievementFileChange = (file: UploadFile) => {
    formData.achievement_file = file.raw as File;
    achievementFileList.value = [file];
  };

  const handleDialogFileChange = (file: UploadFile) => {
    achievementForm.file = file.raw as File;
    dialogFileList.value = [file];
  };

  const openAchievementDialog = (row?: AchievementItem, index = -1) => {
    dialogIndex.value = index;
    dialogVisible.value = true;
    dialogFileList.value = [];

    if (row && index > -1) {
      achievementForm.id = row.id ?? null;
      achievementForm.achievement_type = row.achievement_type || "";
      achievementForm.title = row.title || "";
      achievementForm.description = row.description || "";
      achievementForm.authors = row.authors || "";
      achievementForm.journal = row.journal || "";
      achievementForm.publication_date = row.publication_date || "";
      achievementForm.doi = row.doi || "";
      achievementForm.patent_no = row.patent_no || "";
      achievementForm.patent_type = row.patent_type || "";
      achievementForm.applicant = row.applicant || "";
      achievementForm.competition_name = row.competition_name || "";
      achievementForm.award_level = row.award_level || "";
      achievementForm.award_date = row.award_date || "";
      achievementForm.extra_data = row.extra_data || {};
      achievementForm.file = null;

      const extraData = row.extra_data || {};
      achievementForm.company_name =
        extraData.company_name || row.company_name || "";
      achievementForm.company_role =
        extraData.company_role || row.company_role || "";
      achievementForm.company_date =
        extraData.company_date || row.company_date || "";
      achievementForm.conference_name =
        extraData.conference_name || row.conference_name || "";
      achievementForm.conference_level =
        extraData.conference_level || row.conference_level || "";
      achievementForm.conference_date =
        extraData.conference_date || row.conference_date || "";
      achievementForm.report_title =
        extraData.report_title || row.report_title || "";
      achievementForm.report_type =
        extraData.report_type || row.report_type || "";
      achievementForm.media_title =
        extraData.media_title || row.media_title || "";
      achievementForm.media_format =
        extraData.media_format || row.media_format || "";
      achievementForm.media_link = extraData.media_link || row.media_link || "";
      if (row.file) {
        dialogFileList.value = [buildUploadFile(row.file.name, "ready")];
      } else if (row.attachment_url || row.attachment) {
        const url = row.attachment_url || row.attachment;
        const name =
          row.attachment_name ||
          (typeof url === "string" ? url.split("/").pop() : "") ||
          "附件";
        dialogFileList.value = [
          buildUploadFile(name, "success", typeof url === "string" ? url : ""),
        ];
      }
    } else {
      Object.assign(achievementForm, {
        id: null,
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
        extra_data: {},
        file: null,
      });
    }
  };

  const confirmAchievement = () => {
    if (!achievementForm.achievement_type || !achievementForm.title) {
      ElMessage.warning("请填写类型和标题");
      return;
    }

    const extraData: Record<string, string> = {};
    if (isCompanyType.value) {
      extraData.company_name = achievementForm.company_name || "";
      if (achievementForm.company_role)
        extraData.company_role = achievementForm.company_role;
      if (achievementForm.company_date)
        extraData.company_date = achievementForm.company_date;
    }
    if (isConferenceType.value) {
      extraData.conference_name = achievementForm.conference_name || "";
      if (achievementForm.conference_level) {
        extraData.conference_level = achievementForm.conference_level;
      }
      if (achievementForm.conference_date) {
        extraData.conference_date = achievementForm.conference_date;
      }
    }
    if (isReportType.value) {
      extraData.report_title = achievementForm.report_title || "";
      if (achievementForm.report_type)
        extraData.report_type = achievementForm.report_type;
    }
    if (isMediaType.value) {
      extraData.media_title = achievementForm.media_title || "";
      if (achievementForm.media_format) {
        extraData.media_format = achievementForm.media_format;
      }
      if (achievementForm.media_link)
        extraData.media_link = achievementForm.media_link;
    }
    const prev =
      dialogIndex.value > -1 ? achievements.value[dialogIndex.value] : null;
    const newItem = {
      ...achievementForm,
      extra_data: extraData,
      attachment_url: prev?.attachment_url || "",
      attachment_name: prev?.attachment_name || "",
    };
    if (achievementForm.file) {
      newItem.attachment_url = "";
      newItem.attachment_name = "";
    }
    if (dialogIndex.value > -1) {
      achievements.value[dialogIndex.value] = newItem;
    } else {
      achievements.value.push(newItem);
    }
    dialogVisible.value = false;
  };

  const removeAchievement = (index: number) => {
    achievements.value.splice(index, 1);
  };

  const initFromProject = async (data: ProjectDetail) => {
    project.value = data;
    projectInfo.title = data.title || "";
    projectInfo.project_no = data.project_no || "";
    projectInfo.leader_name =
      data.leader_name || data.leader_info?.real_name || "";
    projectInfo.level_display =
      data.level_display ||
      getLabel(DICT_CODES.PROJECT_LEVEL, data.level ?? "");
    projectInfo.category_display =
      data.category_display ||
      getLabel(DICT_CODES.PROJECT_CATEGORY, data.category ?? "");
    projectInfo.budget = data.budget ?? 0;
    projectInfo.status = data.status || "";


    reportFileList.value = [];
    achievementFileList.value = [];
    if (data.final_report_url) {
      reportFileList.value = [
        {
          name: data.final_report_name || "结题报告",
          url: data.final_report_url,
          status: "success",
          uid: Date.now(),
        },
      ];
    }
    if (data.achievement_file_url) {
      achievementFileList.value = [
        {
          name: data.achievement_file_name || "附件",
          url: data.achievement_file_url,
          status: "success",
          uid: Date.now() + 1,
        },
      ];
    }

    achievements.value = [];
    try {
      const achRes = (await getProjectAchievements(
        Number(projectId)
      )) as ApiResponse<AchievementItem[]>;
      if (achRes?.code === 200) {
        achievements.value = (achRes.data || []).map((item) => ({
          id: item.id,
          achievement_type:
            item.achievement_type_value || item.achievement_type,
          title: item.title || "",
          description: item.description || "",
          authors: item.authors || "",
          journal: item.journal || "",
          publication_date: item.publication_date || "",
          doi: item.doi || "",
          patent_no: item.patent_no || "",
          patent_type: item.patent_type || "",
          applicant: item.applicant || "",
          competition_name: item.competition_name || "",
          award_level: item.award_level || "",
          award_date: item.award_date || "",
          extra_data: item.extra_data || {},
          attachment_url: item.attachment_url || item.attachment || "",
          attachment_name: item.attachment_name || "",
          file: null,
        }));
      }
    } catch {
      // ignore
    }
  };

  const fetchProjectInfo = async () => {
    if (!projectId) {
      ElMessage.error("参数错误：缺少项目ID");
      return;
    }
    loading.value = true;
    try {
      const res = (await getProjectDetail(
        Number(projectId)
      )) as ApiResponse<ProjectDetail>;
      const data = res?.data ?? res;
      if (data) {
        await initFromProject(data as ProjectDetail);
      } else {
        ElMessage.error("未获取到项目详情");
      }
    } catch (error: unknown) {
      ElMessage.error(getErrorMessage(error, "获取项目详情失败"));
    } finally {
      loading.value = false;
    }
  };

  const submit = async (isDraft: boolean) => {
    console.log("submit 函数被调用，isDraft:", isDraft);
    console.log("formRef.value:", formRef.value);

    if (!isDraft) {
      if (!formRef.value) {
        console.error("formRef.value 为空！");
        ElMessage.error("表单未初始化，请刷新页面重试");
        return;
      }
      try {
        console.log("开始验证表单...");
        await formRef.value.validate();
        console.log("表单验证通过，开始提交...");
      } catch (error) {
        console.error("表单验证失败:", error);
        ElMessage.warning("请检查必填项");
        return;
      }
    }

    // 将 doSubmit 的逻辑内联到这里，确保 loading 状态管理正确
    loading.value = true;
    try {
      const payload = new FormData();

      if (formData.final_report)
        payload.append("final_report", formData.final_report);
      if (formData.achievement_file) {
        payload.append("achievement_file", formData.achievement_file);
      }
      payload.append("is_draft", String(isDraft));

      const achievementsData = achievements.value.map((item) => {
        const { file, attachment_url, attachment_name, ...rest } = item;
        void file;
        void attachment_url;
        void attachment_name;
        return rest;
      });
      payload.append("achievements_json", JSON.stringify(achievementsData));

      achievements.value.forEach((item, index) => {
        if (item.file) {
          payload.append(`achievement_${index}`, item.file);
        }
      });

      const isEditingDraft = projectInfo.status === "CLOSURE_DRAFT";
      const res = (await (isEditingDraft
        ? updateClosureApplication(Number(projectId), payload)
        : createClosureApplication(
            Number(projectId),
            payload
          ))) as ApiResponse<unknown>;

      if (res.code === 200 || res.status === 201 || res.code === 201) {
        ElMessage.success(isDraft ? "草稿已保存" : "申请已提交");
        router.push(isDraft ? "/closure/drafts" : "/closure/applied");
      } else {
        ElMessage.error(res.message || "操作失败");
      }
    } catch (error: unknown) {
      console.error("提交失败:", error);
      const errMsg = getErrorMessage(error, "提交失败");
      ElMessage.error(errMsg);
    } finally {
      loading.value = false;
    }
  };

  const submitForm = async () => {
    console.log("submitForm 被调用");
    await submit(false);
  };
  const saveAsDraft = async () => {
    console.log("saveAsDraft 被调用");
    await submit(true);
  };

  const canDeleteSubmission = computed(() => {
    const status = projectInfo.status;
    return [
      "CLOSURE_DRAFT",
      "CLOSURE_SUBMITTED",
      "CLOSURE_LEVEL2_REVIEWING",
      "CLOSURE_LEVEL2_REJECTED",
      "CLOSURE_LEVEL1_REVIEWING",
      "CLOSURE_LEVEL1_REJECTED",
      "CLOSURE_RETURNED",
    ].includes(status);
  });

  const handleDeleteSubmission = async () => {
    if (!project.value) return;
    try {
      await ElMessageBox.confirm(
        "确定删除该结题提交吗？删除后可在回收站恢复。",
        "提示",
        {
          type: "warning",
        }
      );
      const res = (await deleteClosureSubmission(
        project.value.id
      )) as ApiResponse<unknown>;
      if (res?.code === 200) {
        ElMessage.success("已移入回收站");
        fetchProjectInfo();
      } else {
        ElMessage.error(res?.message || "删除失败");
      }
    } catch {
      // cancel
    }
  };

  onMounted(() => {
    loadDictionaries([
      DICT_CODES.ACHIEVEMENT_TYPE,
      DICT_CODES.PROJECT_LEVEL,
      DICT_CODES.PROJECT_CATEGORY,
    ]);
    fetchProjectInfo();
  });

  return {
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
    removeAchievement,
  };
}
