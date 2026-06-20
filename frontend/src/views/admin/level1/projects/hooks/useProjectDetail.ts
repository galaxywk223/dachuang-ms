import { computed, onMounted, reactive, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  ElMessage,
  type FormInstance,
  type FormRules,
} from "element-plus";
import { useDictionary } from "@/composables/useDictionary";
import { DICT_CODES } from "@/api/dictionaries";
import {
  getAdminProjectDetail,
  getProjectTimeline,
  updateProjectInfo,
} from "@/api/projects/admin";
import { getProjectDetail, exportProjectDoc, downloadProjectFile } from "@/api/projects";
import { useUserStore } from "@/stores/user";
import { saveBlob } from "@/utils/common";

type OptionItem = {
  value: string;
  label: string;
  extra_data?: {
    budget?: number | string;
  };
};

interface AdvisorInfo {
  job_number: string;
  name: string;
  title: string;
  contact?: string;
  email?: string;
  order: number;
}

interface MemberInfo {
  student_id: string;
  name: string;
  role?: string;
}

type ProjectForm = {
  id: number | null;
  project_no: string;
  status: string;
  status_display: string;
  source: string;
  level: string;
  category: string;
  is_key_field: boolean;
  key_field_code: string;
  title: string;
  budget: number;
  approved_budget: number | null;
  recommendation_rank: number | null;
  recommended_level_display: string;
  recommended_budget: number | null;
  recommendation_comment: string;
  final_level_display: string;
  final_budget: number | null;
  publish_status: string;
  publish_status_display: string;
  published_at: string;
  published_by_name: string;
  college: string;
  major_code: string;
  leader_name: string;
  leader_student_id: string;
  leader_contact: string;
  leader_email: string;
  expected_results: string;
  description: string;
  proposal_file_url: string;
  proposal_file_name: string;
  attachment_file_url: string;
  attachment_file_name: string;
  advisors: AdvisorInfo[];
  members: MemberInfo[];
};

type ProjectDetailResponse = {
  data?: Record<string, unknown>;
};

type TimelineItem = {
  type?: string;
  title?: string;
  time?: string;
  description?: string;
  status?: string;
  reviewer?: string;
};

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null;

const getErrorMessage = (error: unknown, fallback: string) => {
  if (!isRecord(error)) return fallback;
  const response = error.response;
  if (
    isRecord(response) &&
    isRecord(response.data) &&
    typeof response.data.message === "string"
  ) {
    return response.data.message;
  }
  if (typeof error.message === "string") return error.message;
  return fallback;
};

export function useProjectDetail() {
  const router = useRouter();
  const route = useRoute();
  const { loadDictionaries, getOptions } = useDictionary();

  const pageLoading = ref(false);
  const saving = ref(false);
  const timeline = ref<TimelineItem[]>([]);

  const formRef = ref<FormInstance>();
  const form = reactive<ProjectForm>({
    id: null,
    project_no: "",
    status: "",
    status_display: "",
    source: "",
    level: "",
    category: "",
    is_key_field: false,
    key_field_code: "",
    title: "",
    budget: 0,
    approved_budget: null as number | null,
    recommendation_rank: null,
    recommended_level_display: "",
    recommended_budget: null,
    recommendation_comment: "",
    final_level_display: "",
    final_budget: null,
    publish_status: "",
    publish_status_display: "",
    published_at: "",
    published_by_name: "",
    college: "",
    major_code: "",
    leader_name: "",
    leader_student_id: "",
    leader_contact: "",
    leader_email: "",
    expected_results: "",
    description: "",
    proposal_file_url: "",
    proposal_file_name: "",
    attachment_file_url: "",
    attachment_file_name: "",
    advisors: [] as AdvisorInfo[],
    members: [] as MemberInfo[],
  });

  const isViewMode = computed(() => route.query.mode !== "edit");
  const pageTitle = computed(() =>
    isViewMode.value ? "项目详情" : "编辑项目信息"
  );

  const rules: FormRules = {
    title: [{ required: true, message: "请输入项目名称", trigger: "blur" }],
    level: [{ required: true, message: "请选择项目级别", trigger: "change" }],
    category: [
      { required: true, message: "请选择项目类别", trigger: "change" },
    ],
  };

  const levelOptions = computed(() => getOptions(DICT_CODES.PROJECT_LEVEL));
  const categoryOptions = computed(() =>
    getOptions(DICT_CODES.PROJECT_CATEGORY)
  );
  const sourceOptions = computed(() => getOptions(DICT_CODES.PROJECT_SOURCE));
  const collegeOptions = computed(() => getOptions(DICT_CODES.COLLEGE));
  const majorOptions = computed(() => getOptions(DICT_CODES.MAJOR_CATEGORY));
  const keyFieldOptions = computed(() => getOptions(DICT_CODES.KEY_FIELD_CODE));
  const advisorTitleOptions = computed(() =>
    getOptions(DICT_CODES.ADVISOR_TITLE)
  );

  const keyFieldCascaderOptions = computed(() => {
    const children = (keyFieldOptions.value as OptionItem[]).map((opt) => ({
      value: opt.value,
      label: opt.label,
    }));
    return [
      { value: "GENERAL", label: "一般项目" },
      {
        value: "KEY",
        label: "重点领域项目",
        children: children.length
          ? children
          : [{ value: "", label: "暂无数据 (请在后台添加)", disabled: true }],
      },
    ];
  });

  const keyFieldCascaderValue = computed({
    get: () => {
      if (!form.is_key_field) return ["GENERAL"];
      return form.key_field_code ? ["KEY", form.key_field_code] : ["KEY"];
    },
    set: (val: string[]) => {
      if (!val || val.length === 0) return;
      if (val[0] === "GENERAL") {
        form.is_key_field = false;
        form.key_field_code = "";
      } else if (val[0] === "KEY") {
        form.is_key_field = true;
        if (val.length > 1) {
          form.key_field_code = val[1];
        }
      }
    },
  });

  watch(
    () => form.level,
    (newVal) => {
      if (!newVal) {
        form.budget = 0;
        return;
      }
      const selected = (levelOptions.value as OptionItem[]).find(
        (opt) => opt.value === newVal
      );
      if (selected && selected.extra_data && selected.extra_data.budget) {
        form.budget = Number(selected.extra_data.budget);
      }
    }
  );

  const getLabel = (options: OptionItem[], value: string) => {
    const found = options.find((opt) => opt.value === value);
    return found ? found.label : value;
  };

  const formatDateTime = (value?: string) => {
    if (!value) return "-";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return value;
    const yyyy = date.getFullYear();
    const mm = String(date.getMonth() + 1).padStart(2, "0");
    const dd = String(date.getDate()).padStart(2, "0");
    const hh = String(date.getHours()).padStart(2, "0");
    const mi = String(date.getMinutes()).padStart(2, "0");
    return `${yyyy}-${mm}-${dd} ${hh}:${mi}`;
  };

  const loadProject = async () => {
    const id = Number(route.params.id);
    if (!id) {
      ElMessage.error("未找到项目");
      router.back();
      return;
    }
    pageLoading.value = true;
    try {
      // 根据用户角色选择不同的API
      const userStore = useUserStore();
      const userRole = userStore.role;

      let res: ProjectDetailResponse | Record<string, unknown>;

      // 教师使用通用项目详情API，管理员使用管理员专用API
      if (userRole === "teacher") {
        res = (await getProjectDetail(id)) as
          | ProjectDetailResponse
          | Record<string, unknown>;
      } else {
        res = (await getAdminProjectDetail(id)) as
          | ProjectDetailResponse
          | Record<string, unknown>;
      }

      const data = (isRecord(res) && "data" in res ? res.data : res) as
        | Record<string, unknown>
        | undefined;
      if (!data || !isRecord(data)) {
        throw new Error("数据为空");
      }
      form.id = typeof data.id === "number" ? data.id : Number(data.id || 0);
      form.project_no = String(data.project_no || "");
      form.status = String(data.status || "");
      form.status_display = String(data.status_display || "");
      form.source = String(data.source || "");
      form.level = String(data.level || "");
      form.category = String(data.category || "");
      form.is_key_field = !!data.is_key_field;
      form.key_field_code = String(
        data.key_domain_code || data.key_field_code || ""
      );
      form.title = String(data.title || "");
      form.budget = Number(data.budget || 0);
      form.approved_budget =
        data.approved_budget !== null && data.approved_budget !== undefined
          ? Number(data.approved_budget)
          : null;
      form.recommendation_rank =
        data.recommendation_rank !== null && data.recommendation_rank !== undefined
          ? Number(data.recommendation_rank)
          : null;
      form.recommended_level_display = String(data.recommended_level_display || "");
      form.recommended_budget =
        data.recommended_budget !== null && data.recommended_budget !== undefined
          ? Number(data.recommended_budget)
          : null;
      form.recommendation_comment = String(data.recommendation_comment || "");
      form.final_level_display = String(data.final_level_display || "");
      form.final_budget =
        data.final_budget !== null && data.final_budget !== undefined
          ? Number(data.final_budget)
          : null;
      form.publish_status = String(data.publish_status || "");
      form.publish_status_display = String(data.publish_status_display || "");
      form.published_at = String(data.published_at || "");
      form.published_by_name = String(data.published_by_name || "");
      form.college = String(data.college || "");
      form.major_code = String(data.major_code || "");
      form.leader_name = String(data.leader_name || "");
      form.leader_student_id = String(
        data.leader_student_id || data.student_id || ""
      );
      form.leader_contact = String(data.leader_contact || "");
      form.leader_email = String(data.leader_email || "");
      form.expected_results = String(data.expected_results || "");
      form.description = String(data.description || "");
      form.proposal_file_url = String(data.proposal_file_url || "");
      form.proposal_file_name = String(data.proposal_file_name || "");
      form.attachment_file_url = String(data.attachment_file_url || "");
      form.attachment_file_name = String(data.attachment_file_name || "");

      if (Array.isArray(data.advisors_info)) {
        form.advisors = (data.advisors_info as Record<string, unknown>[]).map(
          (item, index: number) => ({
            job_number: String(item.job_number || ""),
            name: String(item.name || ""),
            title: String(item.title || ""),
            contact: String(item.contact || ""),
            email: String(item.email || ""),
            order: Number(item.order || index + 1),
          })
        );
      } else {
        form.advisors = [];
      }

      if (Array.isArray(data.members_info)) {
        form.members = (data.members_info as Record<string, unknown>[]).map(
          (item) => ({
            student_id: String(item.student_id || ""),
            name: String(item.user_name || item.name || ""),
            role: String(item.role || "MEMBER"),
          })
        );
      } else {
        form.members = [];
      }

      if (userRole !== "teacher") {
        const timelineRes = (await getProjectTimeline(id)) as ProjectDetailResponse;
        const timelinePayload = timelineRes.data;
        timeline.value = Array.isArray(timelinePayload)
          ? (timelinePayload as TimelineItem[])
          : [];
      } else {
        timeline.value = [];
      }
    } catch (error) {
      ElMessage.error(getErrorMessage(error, "加载项目详情失败"));
    } finally {
      pageLoading.value = false;
    }
  };

  const handleSubmit = async () => {
    if (isViewMode.value) return;
    if (!formRef.value) return;
    if (form.is_key_field && !form.key_field_code) {
      ElMessage.error("请选择重点领域代码");
      return;
    }

    try {
      await formRef.value.validate();
    } catch {
      ElMessage.error("请完善必填信息");
      return;
    }

    saving.value = true;
    const basePayload = {
      title: form.title,
      source: form.source || null,
      level: form.level || null,
      category: form.category || null,
      is_key_field: !!form.is_key_field,
      key_domain_code: form.key_field_code || "",
      budget: Number(form.budget) || 0,
      approved_budget:
        form.approved_budget === null || form.approved_budget === undefined
          ? null
          : Number(form.approved_budget),
      expected_results: form.expected_results,
      description: form.description,
    };
    if (!form.id) {
      ElMessage.error("项目ID无效");
      saving.value = false;
      return;
    }
    try {
      await updateProjectInfo(form.id, basePayload);
      ElMessage.success("保存成功");
      router.replace({
        name: "level1-project-detail",
        params: { id: form.id },
        query: { mode: "view" },
      });
    } catch (error) {
      const resp = isRecord(error) ? error.response : undefined;
      const respData = isRecord(resp) ? resp.data : undefined;
      console.error("Update project failed", {
        payload: basePayload,
        status: isRecord(resp) ? resp.status : undefined,
        response: respData || error,
      });
      let msg = getErrorMessage(error, "保存失败");
      if (respData && isRecord(respData)) {
        if (typeof respData.message === "string") {
          msg = respData.message;
        } else {
          const details = Object.entries(respData)
            .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join("; ") : v}`)
            .join("；");
          if (details) msg = `${msg}：${details}`;
        }
      } else if (typeof respData === "string") {
        msg = `${msg}：${respData}`;
      }
      ElMessage.error(msg);
    } finally {
      saving.value = false;
    }
  };

  const switchToEdit = () => {
    router.replace({
      name: "level1-project-detail",
      params: { id: form.id || route.params.id },
      query: { mode: "edit" },
    });
  };

  const handleExportDoc = async () => {
    if (!form.id) return;
    try {
      const res = await exportProjectDoc(form.id);
      const blobPart =
        typeof res === "string"
          ? res
          : res instanceof ArrayBuffer
          ? res
          : ArrayBuffer.isView(res)
          ? (res.buffer as ArrayBuffer)
          : JSON.stringify(res ?? "");
      const blob =
        res instanceof Blob
          ? res
          : new Blob([blobPart], {
              type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            });
      saveBlob(blob, `${form.project_no || "project"}_申报书.docx`);
    } catch {
      ElMessage.error("导出失败");
    }
  };

  const downloadProjectMaterial = async (
    field: "proposal_file" | "attachment_file"
  ) => {
    if (!form.id) return;
    const filename =
      field === "proposal_file"
        ? form.proposal_file_name || "申报书"
        : form.attachment_file_name || "附件";
    try {
      const blob = (await downloadProjectFile(form.id, field)) as Blob;
      saveBlob(blob, filename);
    } catch {
      ElMessage.error("下载项目文件失败");
    }
  };

  onMounted(async () => {
    await loadDictionaries([
      DICT_CODES.PROJECT_LEVEL,
      DICT_CODES.PROJECT_CATEGORY,
      DICT_CODES.PROJECT_SOURCE,
      DICT_CODES.COLLEGE,
      DICT_CODES.MAJOR_CATEGORY,
      DICT_CODES.KEY_FIELD_CODE,
      DICT_CODES.ADVISOR_TITLE,
    ]);
    await loadProject();
  });

  return {
    router,
    route,
    pageLoading,
    saving,
    formRef,
    form,
    timeline,
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
    formatDateTime,
    handleSubmit,
    switchToEdit,
    handleExportDoc,
    downloadProjectMaterial,
  };
}
