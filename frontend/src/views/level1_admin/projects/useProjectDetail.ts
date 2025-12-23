import { computed, onMounted, reactive, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { useDictionary } from "@/composables/useDictionary";
import { DICT_CODES } from "@/api/dictionary";
import { getProjectDetail, updateProjectInfo } from "@/api/admin";
import { exportProjectDoc } from "@/api/project";

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

export function useProjectDetail() {
  const router = useRouter();
  const route = useRoute();
  const { loadDictionaries, getOptions } = useDictionary();

  const pageLoading = ref(false);
  const saving = ref(false);

  const formRef = ref();
  const form = reactive<any>({
    id: null,
    project_no: "",
    status_display: "",
    source: "",
    level: "",
    category: "",
    is_key_field: false,
    key_field_code: "",
    title: "",
    budget: 0,
    approved_budget: null as number | null,
    college: "",
    major_code: "",
    leader_name: "",
    leader_student_id: "",
    leader_contact: "",
    leader_email: "",
    expected_results: "",
    description: "",
    advisors: [] as AdvisorInfo[],
    members: [] as MemberInfo[],
  });

  const isViewMode = computed(() => route.query.mode !== "edit");
  const pageTitle = computed(() =>
    isViewMode.value ? "项目详情" : "编辑项目信息"
  );

  const rules = {
    title: [{ required: true, message: "请输入项目名称", trigger: "blur" }],
    level: [{ required: true, message: "请选择项目级别", trigger: "change" }],
    category: [{ required: true, message: "请选择项目类别", trigger: "change" }],
  };

  const levelOptions = computed(() => getOptions(DICT_CODES.PROJECT_LEVEL));
  const categoryOptions = computed(() => getOptions(DICT_CODES.PROJECT_CATEGORY));
  const sourceOptions = computed(() => getOptions(DICT_CODES.PROJECT_SOURCE));
  const collegeOptions = computed(() => getOptions(DICT_CODES.COLLEGE));
  const majorOptions = computed(() => getOptions(DICT_CODES.MAJOR_CATEGORY));
  const keyFieldOptions = computed(() => getOptions(DICT_CODES.KEY_FIELD_CODE));
  const advisorTitleOptions = computed(() => getOptions(DICT_CODES.ADVISOR_TITLE));

  const keyFieldCascaderOptions = computed(() => {
    const children = keyFieldOptions.value.map((opt: any) => ({
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
      const selected = levelOptions.value.find((opt: any) => opt.value === newVal);
      if (selected && selected.extra_data && selected.extra_data.budget) {
        form.budget = Number(selected.extra_data.budget);
      }
    }
  );

  const getLabel = (options: any[], value: string) => {
    const found = options.find((opt) => opt.value === value);
    return found ? found.label : value;
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
      const res: any = await getProjectDetail(id);
      const data = res.data || res;
      if (!data) {
        throw new Error("数据为空");
      }
      form.id = data.id;
      form.project_no = data.project_no || "";
      form.status_display = data.status_display || "";
      form.source = data.source || "";
      form.level = data.level || "";
      form.category = data.category || "";
      form.is_key_field = !!data.is_key_field;
      form.key_field_code = data.key_domain_code || data.key_field_code || "";
      form.title = data.title || "";
      form.budget = Number(data.budget || 0);
      form.approved_budget =
        data.approved_budget !== null && data.approved_budget !== undefined
          ? Number(data.approved_budget)
          : null;
      form.college = data.college || "";
      form.major_code = data.major_code || "";
      form.leader_name = data.leader_name || "";
      form.leader_student_id = data.leader_student_id || data.student_id || "";
      form.leader_contact = data.leader_contact || "";
      form.leader_email = data.leader_email || "";
      form.expected_results = data.expected_results || "";
      form.description = data.description || "";

      if (Array.isArray(data.advisors_info)) {
        form.advisors = data.advisors_info.map((item: any, index: number) => ({
          job_number: item.job_number || "",
          name: item.name || "",
          title: item.title || "",
          contact: item.contact || "",
          email: item.email || "",
          order: item.order || index + 1,
        }));
      } else {
        form.advisors = [];
      }

      if (Array.isArray(data.members_info)) {
        form.members = data.members_info.map((item: any) => ({
          student_id: item.student_id || "",
          name: item.user_name || item.name || "",
          role: item.role || "MEMBER",
        }));
      } else {
        form.members = [];
      }
    } catch (error: any) {
      ElMessage.error(error.message || "加载项目详情失败");
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

    await formRef.value.validate(async (valid: boolean) => {
      if (!valid) {
        ElMessage.error("请完善必填信息");
        return;
      }
      saving.value = true;
      const payload = {
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
      try {
        await updateProjectInfo(form.id, payload);
        ElMessage.success("保存成功");
        router.replace({
          name: "level1-project-detail",
          params: { id: form.id },
          query: { mode: "view" },
        });
      } catch (error: any) {
        const resp = error?.response;
        const respData: any = resp?.data;
        console.error("Update project failed", {
          payload,
          status: resp?.status,
          response: respData || error,
        });
        let msg = error?.message || "保存失败";
        if (respData) {
          if (respData.message) {
            msg = respData.message;
          } else if (typeof respData === "object") {
            const details = Object.entries(respData)
              .map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join("; ") : v}`)
              .join("；");
            if (details) msg = `${msg}：${details}`;
          } else if (typeof respData === "string") {
            msg = `${msg}：${respData}`;
          }
        }
        ElMessage.error(msg);
      } finally {
        saving.value = false;
      }
    });
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
      const res: any = await exportProjectDoc(form.id);
      const blob = new Blob([res], {
        type: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `${form.project_no || "project"}_申报书.docx`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      ElMessage.error("导出失败");
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
  };
}
