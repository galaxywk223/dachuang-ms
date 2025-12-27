import { computed, onMounted, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage, ElMessageBox, type FormInstance, type UploadFile } from "element-plus";

import {
  createClosureApplication,
  deleteClosureSubmission,
  getProjectAchievements,
  getProjectDetail,
  updateClosureApplication,
} from "@/api/projects";
import { DICT_CODES } from "@/api/dictionaries";
import { useDictionary } from "@/composables/useDictionary";

export function useClosureApply() {
  const route = useRoute();
  const router = useRouter();
  const formRef = ref<FormInstance>();
  const loading = ref(false);
  const project = ref<any | null>(null);
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
    achievement_summary: "",
  });

  const reportFileList = ref<any[]>([]);
  const achievementFileList = ref<any[]>([]);

  const achievements = ref<any[]>([]);
  const dialogVisible = ref(false);
  const dialogIndex = ref(-1);
  const dialogFileList = ref<any[]>([]);

  const achievementForm = reactive({
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
    extra_data: {} as Record<string, string>,
    file: null as File | null,
  });

  const achievementTypeOptions = computed(() => getOptions(DICT_CODES.ACHIEVEMENT_TYPE));

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
        validator: (_rule: any, _value: any, callback: any) => {
          if (formData.final_report || project.value?.final_report_url) {
            callback();
            return;
          }
          callback(new Error("请上传结题报告"));
        },
        trigger: "change",
      },
    ],
    achievement_summary: [
      { required: true, message: "请填写成果简介", trigger: "blur" },
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

  const openAchievementDialog = (row?: any, index = -1) => {
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
      achievementForm.company_name = extraData.company_name || row.company_name || "";
      achievementForm.company_role = extraData.company_role || row.company_role || "";
      achievementForm.company_date = extraData.company_date || row.company_date || "";
      achievementForm.conference_name =
        extraData.conference_name || row.conference_name || "";
      achievementForm.conference_level =
        extraData.conference_level || row.conference_level || "";
      achievementForm.conference_date =
        extraData.conference_date || row.conference_date || "";
      achievementForm.report_title = extraData.report_title || row.report_title || "";
      achievementForm.report_type = extraData.report_type || row.report_type || "";
      achievementForm.media_title = extraData.media_title || row.media_title || "";
      achievementForm.media_format = extraData.media_format || row.media_format || "";
      achievementForm.media_link = extraData.media_link || row.media_link || "";
      if (row.file) {
        dialogFileList.value = [{ name: row.file.name, status: "ready" }];
      } else if (row.attachment_url || row.attachment) {
        const url = row.attachment_url || row.attachment;
        const name =
          row.attachment_name || (typeof url === "string" ? url.split("/").pop() : "附件");
        dialogFileList.value = [{ name, url, status: "success" }];
      }
    } else {
      Object.keys(achievementForm).forEach((key) => {
        (achievementForm as any)[key] = "";
      });
      achievementForm.extra_data = {};
      achievementForm.file = null;
      achievementForm.id = null;
    }
  };

  const confirmAchievement = () => {
    if (!achievementForm.achievement_type || !achievementForm.title) {
      ElMessage.warning("请填写类型和标题");
      return;
    }

    const extraData: Record<string, string> = {};
    if (isCompanyType.value) {
      extraData.company_name = achievementForm.company_name;
      if (achievementForm.company_role) extraData.company_role = achievementForm.company_role;
      if (achievementForm.company_date) extraData.company_date = achievementForm.company_date;
    }
    if (isConferenceType.value) {
      extraData.conference_name = achievementForm.conference_name;
      if (achievementForm.conference_level) {
        extraData.conference_level = achievementForm.conference_level;
      }
      if (achievementForm.conference_date) {
        extraData.conference_date = achievementForm.conference_date;
      }
    }
    if (isReportType.value) {
      extraData.report_title = achievementForm.report_title;
      if (achievementForm.report_type) extraData.report_type = achievementForm.report_type;
    }
    if (isMediaType.value) {
      extraData.media_title = achievementForm.media_title;
      if (achievementForm.media_format) {
        extraData.media_format = achievementForm.media_format;
      }
      if (achievementForm.media_link) extraData.media_link = achievementForm.media_link;
    }
    const prev = dialogIndex.value > -1 ? achievements.value[dialogIndex.value] : null;
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

  const initFromProject = async (data: any) => {
    project.value = data;
    projectInfo.title = data.title || "";
    projectInfo.project_no = data.project_no || "";
    projectInfo.leader_name = data.leader_name || data.leader_info?.real_name || "";
    projectInfo.level_display =
      data.level_display || getLabel(DICT_CODES.PROJECT_LEVEL, data.level);
    projectInfo.category_display =
      data.category_display || getLabel(DICT_CODES.PROJECT_CATEGORY, data.category);
    projectInfo.budget = data.budget ?? 0;
    projectInfo.status = data.status || "";

    formData.achievement_summary = data.achievement_summary || "";

    reportFileList.value = [];
    achievementFileList.value = [];
    if (data.final_report_url) {
      reportFileList.value = [
        {
          name: data.final_report_name || "结题报告.pdf",
          url: data.final_report_url,
          status: "success",
        },
      ];
    }
    if (data.achievement_file_url) {
      achievementFileList.value = [
        {
          name: data.achievement_file_name || "附件",
          url: data.achievement_file_url,
          status: "success",
        },
      ];
    }

    achievements.value = [];
    try {
      const achRes: any = await getProjectAchievements(Number(projectId));
      if (achRes?.code === 200) {
        achievements.value = (achRes.data || []).map((item: any) => ({
          id: item.id,
          achievement_type: item.achievement_type_value || item.achievement_type,
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
      const res: any = await getProjectDetail(Number(projectId));
      const data = res?.data ?? res;
      if (data) {
        await initFromProject(data);
      } else {
        ElMessage.error("未获取到项目详情");
      }
    } catch {
      ElMessage.error("获取项目详情失败");
    } finally {
      loading.value = false;
    }
  };

  const submit = async (isDraft: boolean) => {
    if (!isDraft) {
      if (!formRef.value) return;
      await formRef.value.validate(async (valid) => {
        if (!valid) return;
        await doSubmit(false);
      });
    } else {
      await doSubmit(true);
    }
  };

  const doSubmit = async (isDraft: boolean) => {
    loading.value = true;
    try {
      const payload = new FormData();

      if (formData.final_report) payload.append("final_report", formData.final_report);
      if (formData.achievement_file) {
        payload.append("achievement_file", formData.achievement_file);
      }
      payload.append("achievement_summary", formData.achievement_summary);
      payload.append("is_draft", String(isDraft));

      const achievementsData = achievements.value.map((item: any) => {
        const { file, attachment_url, attachment_name, ...rest } = item;
        return rest;
      });
      payload.append("achievements_json", JSON.stringify(achievementsData));

      achievements.value.forEach((item, index) => {
        if (item.file) {
          payload.append(`achievement_${index}`, item.file);
        }
      });

      const isEditingDraft = projectInfo.status === "CLOSURE_DRAFT";
      const res: any = await (isEditingDraft
        ? updateClosureApplication(Number(projectId), payload)
        : createClosureApplication(Number(projectId), payload));
      if (res.code === 200 || res.status === 201) {
        ElMessage.success(isDraft ? "草稿已保存" : "申请已提交");
        router.push(isDraft ? "/closure/drafts" : "/closure/applied");
      } else {
        ElMessage.error(res.message || "操作失败");
      }
    } catch (e: any) {
      ElMessage.error(e.message || "提交失败");
    } finally {
      loading.value = false;
    }
  };

  const submitForm = () => submit(false);
  const saveAsDraft = () => submit(true);

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
      await ElMessageBox.confirm("确定删除该结题提交吗？删除后可在回收站恢复。", "提示", {
        type: "warning",
      });
      const res: any = await deleteClosureSubmission(project.value.id);
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
