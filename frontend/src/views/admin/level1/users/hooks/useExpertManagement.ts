import { computed, onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from "element-plus";

import {
  createUser,
  deleteUser,
  getUsers,
  toggleUserStatus,
  updateUser,
} from "@/api/users/admin";
import { DICT_CODES } from "@/api/dictionaries";
import { useDictionary } from "@/composables/useDictionary";

export function useExpertManagement() {
  const loading = ref(false);
  const tableData = ref<any[]>([]);
  const total = ref(0);
  const currentPage = ref(1);
  const pageSize = ref(10);
  const addDialogVisible = ref(false);
  const submitLoading = ref(false);
  const isEditMode = ref(false);
  const currentId = ref<number | null>(null);

  const formRef = ref<FormInstance>();
  const { loadDictionaries, getOptions, getLabel } = useDictionary();

  const formData = reactive({
    employee_id: "",
    real_name: "",
    password: "123456",
    phone: "",
    email: "",
    college: "",
    title: "",
    expert_scope: "COLLEGE",
  });

  const collegeOptions = computed(() => getOptions(DICT_CODES.COLLEGE));
  const titleOptions = computed(() => getOptions(DICT_CODES.ADVISOR_TITLE));
  const expertScopeOptions = [
    { value: "SCHOOL", label: "校级专家" },
    { value: "COLLEGE", label: "院级专家" },
  ];

  const getScopeLabel = (value: string) => {
    const match = expertScopeOptions.find((item) => item.value === value);
    return match?.label || "未设置";
  };

  const formRules: FormRules = {
    employee_id: [
      { required: true, message: "请输入工号", trigger: "blur" },
      { min: 4, max: 20, message: "长度应在 4-20 个字符内", trigger: "blur" },
    ],
    real_name: [{ required: true, message: "请输入姓名", trigger: "blur" }],
    password: [
      { required: true, message: "请输入密码", trigger: "blur" },
      { min: 6, message: "密码至少 6 位", trigger: "blur" },
    ],
    phone: [
      {
        validator: (_rule, value, callback) => {
          if (!value) return callback();
          if (!/^\d{11}$/.test(value)) {
            return callback(new Error("手机号需为 11 位数字"));
          }
          return callback();
        },
        trigger: "blur",
      },
    ],
    email: [{ type: "email", message: "邮箱格式不正确", trigger: "blur" }],
    college: [
      {
        validator: (_rule, value, callback) => {
          if (formData.expert_scope === "COLLEGE" && !value) {
            return callback(new Error("请选择学院"));
          }
          return callback();
        },
        trigger: "change",
      },
    ],
    title: [{ required: true, message: "请选择职称", trigger: "change" }],
    expert_scope: [{ required: true, message: "请选择级别", trigger: "change" }],
  };

  const filters = reactive({
    search: "",
    college: "",
    expert_scope: "",
    role: "EXPERT",
  });

  const loadData = async () => {
    loading.value = true;
    try {
      const params = {
        page: currentPage.value,
        page_size: pageSize.value,
        ...filters,
      };
      if (!params.search) delete (params as any).search;
      if (!params.college) delete (params as any).college;
      if (!params.expert_scope) delete (params as any).expert_scope;

      const res = await getUsers(params);
      if (res.code === 200 && res.data) {
        tableData.value = res.data.results || [];
        const resultCount = res.data.count ?? res.data.total ?? tableData.value.length;
        total.value = Number.isFinite(resultCount) ? resultCount : 0;
      } else {
        tableData.value = [];
        total.value = 0;
      }
    } catch (error) {
      console.error(error);
      ElMessage.error("获取数据失败");
    } finally {
      loading.value = false;
    }
  };

  const handleSearch = () => {
    currentPage.value = 1;
    loadData();
  };

  const resetFilters = () => {
    filters.search = "";
    filters.college = "";
    filters.expert_scope = "";
    handleSearch();
  };

  const handleSizeChange = (val: number) => {
    pageSize.value = val;
    loadData();
  };

  const handleCurrentChange = (val: number) => {
    currentPage.value = val;
    loadData();
  };

  const handleEdit = (row: any) => {
    isEditMode.value = true;
    currentId.value = row.id;
    Object.assign(formData, {
      employee_id: row.employee_id,
      real_name: row.real_name,
      phone: row.phone,
      email: row.email,
      college: row.college,
      title: row.title,
      expert_scope: row.expert_scope || "COLLEGE",
      password: "",
    });
    addDialogVisible.value = true;
  };

  const handleToggleStatus = async (row: any) => {
    try {
      const action = row.is_active ? "禁用" : "激活";
      await ElMessageBox.confirm(`确定要${action}该专家吗？`, "提示", {
        type: "warning",
      });
      const res = await toggleUserStatus(row.id);
      if (res.code === 200) {
        ElMessage.success(`${action}成功`);
        loadData();
      }
    } catch {
      // cancel
    }
  };

  const handleDelete = async (row: any) => {
    try {
      await ElMessageBox.confirm(
        `确定要删除专家 \"${row.real_name}\" 吗？此操作不可恢复。`,
        "警告",
        {
          confirmButtonText: "确定删除",
          cancelButtonText: "取消",
          type: "warning",
        }
      );

      const res = await deleteUser(row.id);
      if (res.code === 200 || res.code === 204) {
        ElMessage.success("删除成功");
        loadData();
      } else {
        ElMessage.success("删除成功");
        loadData();
      }
    } catch (error) {
      if (error !== "cancel") {
        console.error(error);
        ElMessage.error("删除失败");
      }
    }
  };

  const resetFormState = () => {
    addDialogVisible.value = false;
    isEditMode.value = false;
    currentId.value = null;
    Object.assign(formData, {
      employee_id: "",
      real_name: "",
      password: "123456",
      phone: "",
      email: "",
      college: "",
      title: "",
      expert_scope: "COLLEGE",
    });
    formRef.value?.clearValidate();
  };

  const openCreateDialog = () => {
    resetFormState();
    addDialogVisible.value = true;
  };

  const handleSubmit = async () => {
    if (!formRef.value) return;
    const valid = await formRef.value.validate().catch(() => false);
    if (!valid) return;

    submitLoading.value = true;
    try {
      const sanitizedId = formData.employee_id.replace(/[^a-zA-Z0-9]/g, "");
      const payload = {
        ...formData,
        employee_id: sanitizedId,
        role: "EXPERT",
        college: formData.expert_scope === "SCHOOL" ? "" : formData.college,
      };

      let res;
      if (isEditMode.value && currentId.value) {
        res = await updateUser(currentId.value, payload);
      } else {
        res = await createUser(payload);
      }

      if (res.code === 200) {
        ElMessage.success(isEditMode.value ? "修改成功" : "添加成功");
        addDialogVisible.value = false;
        loadData();
      }
    } catch (error) {
      console.error(error);
    } finally {
      submitLoading.value = false;
    }
  };

  const importDialogVisible = ref(false);
  const importFile = ref<File | null>(null);
  const importLoading = ref(false);
  const importForm = reactive({
    expert_scope: "COLLEGE",
  });

  const handleImportClick = () => {
    importDialogVisible.value = true;
    importFile.value = null;
    importForm.expert_scope = "COLLEGE";
  };

  const handleFileChange = (file: any) => {
    importFile.value = file.raw;
  };

  const handleImportSubmit = async () => {
    if (!importFile.value) {
      ElMessage.warning("请选择文件");
      return;
    }

    importLoading.value = true;
    try {
      const formData = new FormData();
      formData.append("file", importFile.value);
      formData.append("role", "EXPERT");
      formData.append("expert_scope", importForm.expert_scope);

      const { importUsers } = await import("@/api/users/admin");
      const res = await importUsers(formData);

      if (res.code === 200) {
        ElMessage.success(res.message);
        importDialogVisible.value = false;
        loadData();
      }
    } catch (error: any) {
      console.error(error);
      ElMessage.error(error.response?.data?.message || "导入失败");
    } finally {
      importLoading.value = false;
    }
  };

  onMounted(() => {
    loadDictionaries([DICT_CODES.COLLEGE, DICT_CODES.ADVISOR_TITLE]);
    loadData();
  });

  return {
    addDialogVisible,
    collegeOptions,
    currentPage,
    DICT_CODES,
    expertScopeOptions,
    filters,
    formData,
    formRef,
    formRules,
    getLabel,
    getScopeLabel,
    handleCurrentChange,
    handleDelete,
    handleEdit,
    handleFileChange,
    handleImportClick,
    handleImportSubmit,
    handleSearch,
    handleSizeChange,
    handleSubmit,
    handleToggleStatus,
    importDialogVisible,
    importForm,
    importLoading,
    isEditMode,
    loading,
    openCreateDialog,
    pageSize,
    resetFormState,
    resetFilters,
    submitLoading,
    tableData,
    titleOptions,
    total,
  };
}
