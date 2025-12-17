import { computed, onMounted, reactive, ref, watch } from "vue";
import {
  ElMessage,
  ElMessageBox,
  type FormInstance,
  type FormRules,
  type UploadFile,
} from "element-plus";
import request from "@/utils/request";
import {
  DICT_CODES,
  createDictionaryItem,
  deleteDictionaryItem,
  updateDictionaryItem,
} from "@/api/dictionary";

interface DictionaryType {
  id: number;
  code: string;
  name: string;
  description: string;
}

interface DictionaryItem {
  id: number;
  dict_type: number;
  label: string;
  value: string;
  description?: string;
  sort_order: number;
  is_active: boolean;
  extra_data?: any;
  template_file?: string | null;
}

const CATEGORY_GROUPS: Record<string, string[]> = {
  project: [
    DICT_CODES.PROJECT_LEVEL,
    DICT_CODES.PROJECT_CATEGORY,
    DICT_CODES.PROJECT_SOURCE,
    DICT_CODES.KEY_FIELD_CODE,
    DICT_CODES.PROJECT_STATUS,
    DICT_CODES.CLOSURE_RATING,
  ],
  org: [
    DICT_CODES.COLLEGE,
    DICT_CODES.MAJOR_CATEGORY,
    DICT_CODES.TITLE,
    DICT_CODES.USER_ROLE,
    DICT_CODES.MEMBER_ROLE,
  ],
  achievement: [DICT_CODES.ACHIEVEMENT_TYPE],
  other: [
    DICT_CODES.REVIEW_TYPE,
    DICT_CODES.REVIEW_LEVEL,
    DICT_CODES.REVIEW_STATUS,
    DICT_CODES.NOTIFICATION_TYPE,
  ],
};

export function useSystemDictionaries(options: { category?: string } = {}) {
  const dictionaryTypes = ref<DictionaryType[]>([]);
  const currentType = ref<DictionaryType | null>(null);
  const items = ref<DictionaryItem[]>([]);
  const loading = ref(false);
  const dialogVisible = ref(false);
  const submitting = ref(false);
  const isEditMode = ref(false);
  const editingId = ref<number | null>(null);
  const formRef = ref<FormInstance>();

  const selectedFile = ref<File | null>(null);
  const fileList = ref<any[]>([]);

  const CODE_BASED_TYPES = ["major_category", "key_field_code", "project_level"];

  const showCode = computed(() => {
    if (!currentType.value) return false;
    return CODE_BASED_TYPES.includes(currentType.value.code);
  });

  const showBudget = computed(() => currentType.value?.code === "project_level");
  const showTemplate = computed(
    () => currentType.value?.code === DICT_CODES.PROJECT_CATEGORY
  );

  const form = reactive({
    label: "",
    value: "",
    description: "",
    sort_order: 0,
    budget: 0,
  });

  const rules = computed<FormRules>(() => {
    const baseRules: FormRules = {
      label: [{ required: true, message: "请输入名称", trigger: "blur" }],
    };

    if (showCode.value) {
      baseRules.value = [{ required: true, message: "请输入代码", trigger: "blur" }];
    }

    return baseRules;
  });

  const fetchTypes = async () => {
    try {
      const response = await request.get("/dictionaries/types/");
      const list =
        (response as any)?.data?.results ??
        (response as any)?.results ??
        (response as any)?.data ??
        response;

      const allTypes = Array.isArray(list) ? list : [];
      const category = options.category || "";

      if (category && CATEGORY_GROUPS[category]) {
        const allowedCodes = CATEGORY_GROUPS[category];
        dictionaryTypes.value = allTypes.filter((t: any) =>
          allowedCodes.includes(t.code)
        );
      } else {
        dictionaryTypes.value = allTypes;
      }

      currentType.value = dictionaryTypes.value.length
        ? dictionaryTypes.value[0]
        : null;
    } catch (error) {
      console.error("Failed to fetch dictionary types:", error);
      ElMessage.error("获取参数类型失败");
    }
  };

  const fetchItems = async (typeCode: string) => {
    loading.value = true;
    try {
      const response = await request.get("/dictionaries/items/", {
        params: { dict_type_code: typeCode },
      });
      const list =
        (response as any)?.data?.results ??
        (response as any)?.results ??
        (response as any)?.data ??
        response;
      items.value = Array.isArray(list) ? list : [];
    } catch (error) {
      console.error("Failed to fetch items:", error);
      ElMessage.error("获取参数数据失败");
    } finally {
      loading.value = false;
    }
  };

  const handleTypeSelect = (type: DictionaryType) => {
    currentType.value = type;
  };

  const resetFormState = () => {
    form.label = "";
    form.value = "";
    form.description = "";
    form.sort_order = 0;
    form.budget = 0;
    selectedFile.value = null;
    fileList.value = [];
  };

  const openAddDialog = () => {
    isEditMode.value = false;
    editingId.value = null;
    resetFormState();
    dialogVisible.value = true;
  };

  const editItem = (item: DictionaryItem) => {
    isEditMode.value = true;
    editingId.value = item.id;
    form.label = item.label;
    form.value = item.value;
    form.description = item.description || "";
    form.sort_order = item.sort_order;

    if (item.extra_data && typeof item.extra_data === "object") {
      form.budget = (item.extra_data as any).budget || 0;
    } else {
      form.budget = 0;
    }

    fileList.value = [];
    if (item.template_file) {
      const fileName = item.template_file.split("/").pop() || "template.pdf";
      fileList.value = [{ name: fileName, url: item.template_file }];
    }

    dialogVisible.value = true;
  };

  const resetForm = () => {
    resetFormState();
    formRef.value?.clearValidate();
  };

  const handleFileChange = (file: UploadFile) => {
    selectedFile.value = file.raw || null;
  };

  const handleRemoveFile = () => {
    selectedFile.value = null;
  };

  const submitForm = async () => {
    const type = currentType.value;
    if (!formRef.value || !type) return;

    await formRef.value.validate(async (valid) => {
      if (!valid) return;
      submitting.value = true;
      try {
        const finalValue = showCode.value ? form.value : form.label;

        const extraData: any = {};
        if (showBudget.value) {
          extraData.budget = Number(form.budget) || 0;
        }

        let payload: any;
        if (selectedFile.value) {
          payload = new FormData();
          payload.append("label", form.label);
          payload.append("value", finalValue);
          payload.append(
            "sort_order",
            String(
              isEditMode.value && editingId.value
                ? form.sort_order
                : items.value.length + 1
            )
          );
          payload.append("extra_data", JSON.stringify(extraData));
          payload.append("dict_type", String(type.id));
          payload.append("description", form.description || "");
          payload.append("is_active", "true");
          payload.append("template_file", selectedFile.value);
        } else {
          payload = {
            label: form.label,
            value: finalValue,
            sort_order:
              isEditMode.value && editingId.value
                ? form.sort_order
                : items.value.length + 1,
            extra_data: extraData,
            dict_type: type.id,
            description: form.description || "",
            is_active: true,
          };
        }

        if (isEditMode.value && editingId.value) {
          await updateDictionaryItem(editingId.value, payload);
          ElMessage.success("修改成功");
        } else {
          await createDictionaryItem(payload);
          ElMessage.success("添加成功");
        }

        dialogVisible.value = false;
        await fetchItems(type.code);
      } catch (error) {
        console.error(error);
        ElMessage.error(isEditMode.value ? "修改失败" : "添加失败");
      } finally {
        submitting.value = false;
      }
    });
  };

  const deleteItem = async (item: DictionaryItem) => {
    try {
      await ElMessageBox.confirm(
        `确认要删除 \"${item.label}\" 吗？此操作不可恢复。`,
        "警告",
        {
          confirmButtonText: "确定删除",
          cancelButtonText: "取消",
          type: "warning",
        }
      );

      await deleteDictionaryItem(item.id);
      ElMessage.success("删除成功");
      if (currentType.value) {
        await fetchItems(currentType.value.code);
      }
    } catch (error) {
      if (error !== "cancel") {
        ElMessage.error("删除失败，可能该条目正在被使用");
      }
    }
  };

  watch(currentType, async (newType) => {
    if (newType) {
      await fetchItems(newType.code);
    } else {
      items.value = [];
    }
  });

  onMounted(async () => {
    await fetchTypes();
  });

  return {
    dictionaryTypes,
    currentType,
    items,
    loading,
    dialogVisible,
    submitting,
    isEditMode,
    editingId,
    formRef,
    fileList,
    showCode,
    showBudget,
    showTemplate,
    form,
    rules,
    fetchItems,
    handleTypeSelect,
    openAddDialog,
    editItem,
    resetForm,
    handleFileChange,
    handleRemoveFile,
    submitForm,
    deleteItem,
  };
}

