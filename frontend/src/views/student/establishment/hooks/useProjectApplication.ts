import { computed, onMounted, reactive, ref, watch } from "vue";
import { ElMessage, type FormInstance, type UploadUserFile } from "element-plus";
import { useRouter, useRoute } from "vue-router";
import { getUsers } from "@/api/users/admin";
import { useDictionary } from "@/composables/useDictionary";
import { DICT_CODES } from "@/api/dictionaries";
import { useUserStore } from "@/stores/user";
import {
  createProjectApplication,
  updateProjectApplication,
  getProjectDetail,
} from "@/api/projects";

interface AdvisorInfo {
  user_id?: number | null;
  job_number: string;
  name: string;
  title: string;
  contact: string;
  email: string;
  order: number;
  college?: string;
}

interface MemberInfo {
  student_id: string;
  name: string;
}

interface CascaderOption {
  value: string;
  label: string;
  disabled?: boolean;
  children?: CascaderOption[];
}

interface FormDataState {
  id: number | null;
  source: string;
  level: string;
  category: string;
  discipline: string;
  is_key_field: boolean | string;
  key_domain_code: string;
  college: string;
  budget: number;
  major_code: string;
  leader_contact: string;
  leader_email: string;
  title: string;
  expected_results: string;
  expected_results_data: { achievement_type: string; expected_count: number }[];
  description: string;
  advisors: AdvisorInfo[];
  members: MemberInfo[];
  attachment_file: File | null;
}

export function useProjectApplication() {
  const userStore = useUserStore();
  const router = useRouter();
  const route = useRoute();
  const { loadDictionaries, getOptions } = useDictionary();

  const formRef = ref<FormInstance>();
  const loading = ref(false);
  const fileList = ref<UploadUserFile[]>([]);

  const currentUser = computed(() => ({
    name: userStore.user?.real_name || userStore.user?.username || "学生用户",
    student_id: userStore.user?.employee_id || userStore.user?.username || "Unknown",
  }));

  const formData = reactive<FormDataState>({
    id: null,
    source: "",
    level: "",
    category: "",
    discipline: "",
    is_key_field: false,
    key_domain_code: "",
    college: "",
    budget: 0,
    major_code: "",
    leader_contact: "",
    leader_email: "",
    title: "",
    expected_results: "",
    expected_results_data: [],
    description: "",
    advisors: [],
    members: [],
    attachment_file: null,
  });

  // Watcher for Budget Automation
  watch(
    () => formData.level,
    (newVal) => {
      if (!newVal) {
        formData.budget = 0;
        return;
      }
      const selectedOption = levelOptions.value.find(
        (opt: any) => opt.value === newVal
      );
      if (selectedOption && selectedOption.extra_data && selectedOption.extra_data.budget) {
        formData.budget = Number(selectedOption.extra_data.budget);
      } else {
        // Fallback or keep 0 if no config found
        formData.budget = 0;
      }
    }
  );

  // Temp inputs
  const newAdvisor = reactive({
    user_id: null as number | null,
    job_number: "",
    name: "",
    title: "",
    contact: "",
    email: "",
    order: 1,
  });
  const newMember = reactive({ student_id: "", name: "" });

  const currentTemplateUrl = computed(() => {
    if (!formData.category) return null;
    const option = categoryOptions.value.find((opt: any) => opt.value === formData.category);
    return option?.template_file || null;
  });

  const handleDownloadTemplate = () => {
    if (!formData.category) {
      ElMessage.warning("请先选择项目类别");
      return;
    }
    if (currentTemplateUrl.value) {
      window.open(currentTemplateUrl.value, "_blank");
    } else {
      ElMessage.info("该类别暂无申请书模板");
    }
  };

  const rules = {
    source: [{ required: true, message: "必选项", trigger: "change" }],
    level: [{ required: true, message: "必选项", trigger: "change" }],
    category: [{ required: true, message: "必选项", trigger: "change" }],
    discipline: [{ required: false, message: "必选项", trigger: "change" }],
    title: [{ required: true, message: "必填项", trigger: "blur" }],
    leader_contact: [{ required: true, message: "必填项", trigger: "blur" }],
    leader_email: [{ required: true, message: "必填项", trigger: "blur" }],
    college: [{ required: true, message: "必选项", trigger: "change" }],
    major_code: [{ required: true, message: "必选项", trigger: "change" }],
    expected_results: [{ required: true, message: "必填项", trigger: "blur" }],
    description: [{ required: true, message: "必填项", trigger: "blur" }],
    attachment_file: [
      {
        validator: (_rule: any, _value: any, callback: any) => {
          if (fileList.value.length > 0) {
            callback();
          } else {
            callback(new Error("请上传申请书"));
          }
        },
        trigger: "change",
      },
    ],
  };

  // Dicts
  const sourceOptions = computed(() => getOptions(DICT_CODES.PROJECT_SOURCE));
  const collegeOptions = computed(() => getOptions(DICT_CODES.COLLEGE));
  const majorOptions = computed(() => getOptions(DICT_CODES.MAJOR_CATEGORY));
  const advisorTitleOptions = computed(() => getOptions(DICT_CODES.ADVISOR_TITLE));
  const levelOptions = computed(() => getOptions(DICT_CODES.PROJECT_LEVEL));
  const keyFieldOptions = computed(() => getOptions(DICT_CODES.KEY_FIELD_CODE));
  const categoryOptions = computed(() => getOptions(DICT_CODES.PROJECT_CATEGORY));
  const disciplineOptions = computed(() => getOptions(DICT_CODES.DISCIPLINE));
  const achievementTypeOptions = computed(() => getOptions(DICT_CODES.ACHIEVEMENT_TYPE));

  const getDefaultLevel = () => levelOptions.value[0]?.value || "";
  const getDefaultCategory = () => categoryOptions.value[0]?.value || "";

  const keyFieldCascaderOptions = computed(() => {
    let keyChildren: CascaderOption[] = keyFieldOptions.value.map((opt) => ({
      value: opt.value,
      label: opt.label,
    }));

    if (keyChildren.length === 0) {
      keyChildren = [
        {
          value: "",
          label: "暂无数据 (请在后台添加)",
          disabled: true,
        },
      ];
    }

    return [
      {
        value: "GENERAL",
        label: "一般项目",
      },
      {
        value: "KEY",
        label: "重点领域项目",
        children: keyChildren,
      },
    ] as CascaderOption[];
  });

  const keyFieldCascaderValue = computed({
    get: () => {
      if (!formData.is_key_field) return ["GENERAL"];
      return formData.key_domain_code ? ["KEY", formData.key_domain_code] : ["KEY"];
    },
    set: (val: string[]) => {
      if (!val || val.length === 0) return;
      if (val[0] === "GENERAL") {
        formData.is_key_field = false;
        formData.key_domain_code = "";
      } else if (val[0] === "KEY") {
        formData.is_key_field = true;
        if (val.length > 1) {
          formData.key_domain_code = val[1];
        }
      }
    },
  });

  const expectedForm = reactive({
    achievement_type: "",
    expected_count: 1,
  });

  const addExpectedResult = () => {
    if (!expectedForm.achievement_type) {
      ElMessage.warning("请选择成果类型");
      return;
    }
    formData.expected_results_data.push({
      achievement_type: expectedForm.achievement_type,
      expected_count: expectedForm.expected_count || 1,
    });
    expectedForm.achievement_type = "";
    expectedForm.expected_count = 1;
  };

  const removeExpectedResult = (index: number) => {
    formData.expected_results_data.splice(index, 1);
  };

  const getLabel = (options: any[], value: string) => {
    const found = options.find((opt) => opt.value === value);
    return found ? found.label : value;
  };

  // Dynamic Actions
  const handleSearchNewAdvisor = async () => {
    if (!newAdvisor.job_number) {
      ElMessage.warning("请输入工号");
      return;
    }

    try {
      const res = await getUsers({
        employee_id: newAdvisor.job_number,
        role: "TEACHER",
        page_size: 1,
      });
      const users = res.data?.results || [];
      if (users.length > 0) {
        const user = users[0];
        newAdvisor.user_id = user.id;
        newAdvisor.name = user.real_name;
        newAdvisor.title = user.title || "";
        newAdvisor.contact = user.phone;
        newAdvisor.email = user.email;

        ElMessage.success(`已找到教师: ${user.real_name}`);
      } else {
        ElMessage.error("未找到该工号的教师，请核对或联系管理员添加");
        newAdvisor.user_id = null;
        newAdvisor.name = "";
        newAdvisor.title = "";
        newAdvisor.contact = "";
        newAdvisor.email = "";
      }
    } catch (error) {
      console.error("Search failed", error);
      ElMessage.error("查询失败");
    }
  };

  const handleAddNewAdvisor = () => {
    if (newAdvisor.order === 2) {
      const hasFirst = formData.advisors.some((a) => a.order === 1);
      if (!hasFirst) {
        ElMessage.warning("请先添加第一指导教师");
        return;
      }
    }
    // Check if user is selected
    if (!newAdvisor.user_id) {
      ElMessage.warning("请先查询并确认教师信息");
      return;
    }

    // Check duplicate
    if (formData.advisors.some((a) => a.job_number === newAdvisor.job_number)) {
      ElMessage.warning("该教师已添加");
      return;
    }

    // Check if order already exists (optional, but good for UX)
    if (formData.advisors.some((a) => a.order === newAdvisor.order)) {
      ElMessage.warning(newAdvisor.order === 1 ? "第一指导教师已存在" : "第二指导教师已存在");
      return;
    }

    formData.advisors.push({ ...newAdvisor });
    // Reset
    newAdvisor.user_id = null;
    newAdvisor.job_number = "";
    newAdvisor.name = "";
    newAdvisor.title = "";
    newAdvisor.contact = "";
    newAdvisor.email = "";
  };

  const handleSearchNewMember = async () => {
    if (!newMember.student_id) {
      ElMessage.warning("请输入学号");
      return;
    }

    try {
      const res = await getUsers({
        employee_id: newMember.student_id,
        role: "STUDENT",
        page_size: 1,
      });
      const users = res.data?.results || [];
      if (users.length > 0) {
        const user = users[0];
        newMember.name = user.real_name;
        ElMessage.success(`已找到学生: ${user.real_name}`);
      } else {
        ElMessage.error("未找到该学号的学生");
        newMember.name = "";
      }
    } catch (error) {
      console.error("Search failed", error);
      ElMessage.error("查询失败");
    }
  };

  const handleAddNewMember = () => {
    if (!newMember.student_id) {
      ElMessage.warning("请填写学号");
      return;
    }
    if (!newMember.name) {
      ElMessage.warning("请先查询并确认学生信息");
      return;
    }

    // Check duplicate
    if (formData.members.some((m) => m.student_id === newMember.student_id)) {
      ElMessage.warning("该成员已添加");
      return;
    }

    formData.members.push({ ...newMember });
    // Reset
    newMember.student_id = "";
    newMember.name = "";
  };

  const removeAdvisor = (i: number) => formData.advisors.splice(i, 1);
  const removeMember = (i: number) => formData.members.splice(i, 1);

  const handleFileChange = (file: any) => {
    const isPDF = file.raw.type === "application/pdf";
    const isLt2M = file.raw.size / 1024 / 1024 < 2;

    if (!isPDF) {
      ElMessage.error("只能上传 PDF 文件!");
      fileList.value = [];
      formData.attachment_file = null;
      return;
    }
    if (!isLt2M) {
      ElMessage.error("文件大小不能超过 2MB!");
      fileList.value = [];
      formData.attachment_file = null;
      return;
    }

    formData.attachment_file = file.raw;
    formRef.value?.validateField("attachment_file");
  };

  const handleFileRemove = () => {
    formData.attachment_file = null;
  };

  // Submit Logic
  const handleSaveOrSubmit = async (isDraft: boolean) => {
    if (!formRef.value) return;

    // Advisor Validation (only for submit, draft can be partial)
    if (!isDraft) {
      if (formData.advisors.length === 0) {
        ElMessage.warning("请至少添加一名指导老师");
        return;
      }
      // Ensure First Advisor exists
      const hasFirst = formData.advisors.some((a) => a.order === 1);
      if (!hasFirst) {
        ElMessage.warning("请添加第一指导老师");
        return;
      }
    }

    if (!isDraft) {
      if (formData.advisors.length === 0) {
        console.warn("No advisors added, user might have forgotten to click add");
      }
      if (formData.expected_results_data.length === 0) {
        ElMessage.warning("请补充预期成果清单");
        return;
      }
      await formRef.value.validate(async (valid) => {
        if (!valid) {
          ElMessage.error("请完善必填信息");
          return;
        }
        await processRequest(false);
      });
    } else {
      await processRequest(true);
    }
  };

  const processRequest = async (isDraft: boolean) => {
    if (!formData.title && isDraft) {
      ElMessage.warning("请填写项目名称（草稿必填）");
      return;
    }

    loading.value = true;
    try {
      const payload = new FormData();

      // 1. Basic Fields Mapping
      const basicFields = { ...formData };

      // Handle Logic before appending
      const validLevels = levelOptions.value.map((opt: any) => opt.value);
      if (!validLevels.includes(basicFields.level)) {
        basicFields.level = getDefaultLevel();
      }

      const validCategories = categoryOptions.value.map((opt: any) => opt.value);
      if (!validCategories.includes(basicFields.category)) {
        basicFields.category = getDefaultCategory();
      }

      const keyFieldVal = basicFields.is_key_field;
      basicFields.is_key_field =
        keyFieldVal === true ||
        keyFieldVal === "TRUE" ||
        keyFieldVal === "YES" ||
        keyFieldVal === "KEY"
          ? "KEY"
          : "NORMAL";

      if (!basicFields.leader_email || !/^\S+@\S+\.\S+$/.test(basicFields.leader_email)) {
        basicFields.leader_email = "";
      }

      basicFields.budget = Number(basicFields.budget) || 0;

      payload.append("is_draft", String(isDraft));

      // Append fields loop
      Object.keys(basicFields).forEach((key) => {
        if (key === "attachment_file") {
          if (basicFields.attachment_file) {
            payload.append("proposal_file", basicFields.attachment_file);
          }
        } else if (key === "advisors" || key === "members") {
          payload.append(key, JSON.stringify(basicFields[key]));
        } else if (key === "expected_results_data") {
          payload.append(key, JSON.stringify(basicFields[key] || []));
        } else if (key === "id") {
          // Skip ID in body
        } else {
          const val = (basicFields as any)[key];
          if (val !== null && val !== undefined) {
            payload.append(key, String(val));
          }
        }
      });

      let response: any;
      if (formData.id) {
        response = await updateProjectApplication(formData.id, payload);
      } else {
        response = await createProjectApplication(payload);
      }

      if (response.code === 200 || response.status === 201) {
        ElMessage.success(isDraft ? "草稿已保存" : "申请已提交");
        if (!isDraft) {
          router.push("/establishment/my-projects");
        } else {
          if (response.data && response.data.id) {
            formData.id = response.data.id;
            router.replace({
              path: route.path,
              query: { ...route.query, id: String(response.data.id) },
            });
          }
        }
      } else {
        let errorMsg = response.message || "操作失败";
        if (response.errors) {
          const details = Object.entries(response.errors)
            .map(([k, v]) => `${k}: ${v}`)
            .join("; ");
          errorMsg += ` (${details})`;
        }
        ElMessage.error(errorMsg);
      }
    } catch (e: any) {
      ElMessage.error(e.message || "请求失败");
      console.error(e);
    } finally {
      loading.value = false;
    }
  };

  const submitForm = () => handleSaveOrSubmit(false);
  const saveAsDraft = () => handleSaveOrSubmit(true);
  const handleReset = () => formRef.value?.resetFields();

  const loadData = async (id: number) => {
    loading.value = true;
    try {
      const res: any = await getProjectDetail(id);
      const projectData = res.data || res;

      if (projectData && (projectData.id || res.code === 200)) {
        const data = projectData.id ? projectData : projectData.data;
        if (!data) throw new Error("No data found");

        formData.id = data.id;
        formData.title = data.title || "";
        formData.source = data.source || "";
        formData.level = data.level || getDefaultLevel();
        formData.category = data.category || getDefaultCategory();
        formData.college = data.college || "";
        formData.major_code = data.major_code || "";
        formData.budget = Number(data.budget || 0);
        formData.leader_contact = data.leader_contact || "";
        formData.leader_email = data.leader_email || "";
        formData.description = data.description || "";
        formData.expected_results = data.expected_results || "";
        formData.expected_results_data = Array.isArray(data.expected_results_data)
          ? data.expected_results_data
          : [];

        // Handle Boolean Key Field
        formData.is_key_field = !!data.is_key_field;
        formData.key_domain_code = data.key_domain_code || data.key_field_code || "";

        const proposalUrl = data.proposal_file_url || data.attachment_file_url || "";
        const proposalName = data.proposal_file_name || data.attachment_file_name || "申请书.pdf";
        fileList.value = proposalUrl
          ? [{ name: proposalName, url: proposalUrl, status: "success", uid: Date.now() }]
          : [];

        if (Array.isArray(data.advisors_info) && data.advisors_info.length > 0) {
          formData.advisors = data.advisors_info.map((adh: any, index: number) => ({
            job_number: adh.job_number || "",
            name: adh.name || "",
            title: adh.title || "",
            contact: adh.contact || "",
            email: adh.email || "",
            order: adh.order || index + 1,
          }));
        }

        if (Array.isArray(data.members_info) && data.members_info.length > 0) {
          const otherMembers = data.members_info.filter((m: any) => m.role === "MEMBER");
          if (otherMembers.length > 0) {
            formData.members = otherMembers.map((m: any) => ({
              student_id: m.student_id || "",
              name: m.user_name || m.name || "",
            }));
          }
        }
        ElMessage.success("数据加载成功");
      }
    } catch (e: any) {
      ElMessage.error("加载详情失败");
    } finally {
      loading.value = false;
    }
  };

  onMounted(async () => {
    await loadDictionaries([
      DICT_CODES.PROJECT_LEVEL,
      DICT_CODES.PROJECT_CATEGORY,
      DICT_CODES.PROJECT_SOURCE,
      DICT_CODES.COLLEGE,
      DICT_CODES.PROJECT_TYPE,
      DICT_CODES.MAJOR_CATEGORY,
      DICT_CODES.TITLE,
      DICT_CODES.KEY_FIELD_CODE,
      DICT_CODES.ACHIEVEMENT_TYPE,
    ]);
    const id = route.query.id;
    if (id) {
      loadData(Number(id));
    } else {
      // Pre-fill contact info if creating new application
      if (userStore.user) {
        if (!formData.leader_contact) formData.leader_contact = userStore.user.phone || "";
        if (!formData.leader_email) formData.leader_email = userStore.user.email || "";
      }
    }
  });

  // Watch for user data loading if not available on mount
  watch(
    () => userStore.user,
    (newUser) => {
      if (newUser && !route.query.id) {
        if (!formData.leader_contact) formData.leader_contact = newUser.phone || "";
        if (!formData.leader_email) formData.leader_email = newUser.email || "";
      }
    }
  );

  return {
    formRef,
    formData,
    rules,
    sourceOptions,
    levelOptions,
    categoryOptions,
    disciplineOptions,
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
  };
}
