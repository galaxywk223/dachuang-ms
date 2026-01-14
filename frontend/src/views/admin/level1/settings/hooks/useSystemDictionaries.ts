import { computed, onMounted, reactive, ref, watch } from "vue";
import {
  ElMessage,
  ElMessageBox,
  type FormInstance,
  type FormRules,
  type UploadFile,
  type UploadUserFile,
} from "element-plus";
import request from "@/utils/request";
import {
  DICT_CODES,
  createDictionaryItem,
  deleteDictionaryItem,
  bulkCreateDictionaryItems,
  clearDictionaryItems,
  updateDictionaryItem,
} from "@/api/dictionaries";

interface DictionaryType {
  id: number;
  code: string;
  name: string;
  description: string;
  isLocal?: boolean;
}

interface DictionaryItem {
  id: number;
  dict_type: number;
  label: string;
  value: string;
  description?: string;
  sort_order: number;
  is_active: boolean;
  extra_data?: Record<string, unknown>;
  template_file?: string | null;
}

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null;

const resolveList = <T>(response: unknown): T[] => {
  if (Array.isArray(response)) return response as T[];
  if (!isRecord(response)) return [];
  if (Array.isArray(response.results)) return response.results as T[];
  if (isRecord(response.data) && Array.isArray(response.data.results)) {
    return response.data.results as T[];
  }
  if (Array.isArray(response.data)) return response.data as T[];
  return [];
};

const CATEGORY_GROUPS: Record<string, string[]> = {
  project: [
    DICT_CODES.PROJECT_LEVEL,
    DICT_CODES.PROJECT_CATEGORY,
    DICT_CODES.PROJECT_SOURCE,
    DICT_CODES.KEY_FIELD_CODE,
  ],
  org: [DICT_CODES.COLLEGE, DICT_CODES.MAJOR_CATEGORY, DICT_CODES.TITLE],
  achievement: [DICT_CODES.ACHIEVEMENT_TYPE],
};

export function useSystemDictionaries(
  options: {
    category?: string;
    dictTypeCode?: string;
    extraTypes?: DictionaryType[];
  } = {}
) {
  const dictionaryTypes = ref<DictionaryType[]>([]);
  const currentType = ref<DictionaryType | null>(null);
  const items = ref<DictionaryItem[]>([]);
  const loading = ref(false);
  const dialogVisible = ref(false);
  const submitting = ref(false);
  const isEditMode = ref(false);
  const editingId = ref<number | null>(null);
  const formRef = ref<FormInstance>();
  const importDialogVisible = ref(false);
  const importLoading = ref(false);
  const importFile = ref<File | null>(null);
  const importText = ref("");

  const selectedFile = ref<File | null>(null);
  const fileList = ref<UploadUserFile[]>([]);

  const CODE_BASED_TYPES = [
    "major_category",
    "key_field_code",
    "project_level",
  ];

  const showCode = computed(() => {
    if (!currentType.value) return false;
    return CODE_BASED_TYPES.includes(currentType.value.code);
  });

  const showBudget = computed(
    () => currentType.value?.code === "project_level"
  );
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
      baseRules.value = [
        { required: true, message: "请输入代码", trigger: "blur" },
      ];
    }

    return baseRules;
  });

  const fetchTypes = async () => {
    try {
      const response = await request.get("/dictionaries/types/");
      const allTypes = resolveList<DictionaryType>(response).map((type) => ({
        ...type,
        name: type.code === DICT_CODES.COLLEGE ? "部门" : type.name,
      }));
      const category = options.category || "";

      let filteredTypes: DictionaryType[] = [];

      if (category && CATEGORY_GROUPS[category]) {
        const allowedCodes = CATEGORY_GROUPS[category];
        filteredTypes = allTypes.filter((t: DictionaryType) =>
          allowedCodes.includes(t.code)
        );
      } else {
        filteredTypes = allTypes;
      }

      // Merge extra types
      if (options.extraTypes) {
        filteredTypes = [...filteredTypes, ...options.extraTypes];
      }

      dictionaryTypes.value = filteredTypes;

      // 如果提供了dictTypeCode，直接选中该类型
      if (options.dictTypeCode) {
        const targetType = dictionaryTypes.value.find(
          (t: DictionaryType) => t.code === options.dictTypeCode
        );
        currentType.value = targetType || null;
      } else {
        currentType.value = dictionaryTypes.value.length
          ? dictionaryTypes.value[0]
          : null;
      }

      // 立即加载第一个类型的数据
      if (currentType.value) {
        await fetchItems(currentType.value.code);
      }
    } catch (error) {
      console.error("Failed to fetch dictionary types:", error);
      ElMessage.error("获取参数类型失败");
    }
  };

  const fetchItems = async (typeCode: string) => {
    // Check if current type is local
    if (currentType.value?.isLocal) {
      items.value = [];
      return;
    }

    loading.value = true;
    try {
      const response = await request.get("/dictionaries/items/", {
        params: { dict_type_code: typeCode },
      });
      items.value = resolveList<DictionaryItem>(response);
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

  const openImportDialog = () => {
    importDialogVisible.value = true;
    importFile.value = null;
    importText.value = "";
  };

  const resetImport = () => {
    importFile.value = null;
    importText.value = "";
  };

  const handleImportFileChange = (file: UploadFile) => {
    importFile.value = file.raw || null;
  };

  const readImportContent = async (): Promise<{
    text: string;
    rows: string[][] | null;
  }> => {
    if (!importFile.value) {
      return { text: importText.value || "", rows: null };
    }

    const fileName = importFile.value.name.toLowerCase();
    if (fileName.endsWith(".xlsx") || fileName.endsWith(".xls")) {
      const { read, utils } = await import("xlsx");
      const arrayBuffer = await importFile.value.arrayBuffer();
      const workbook = read(arrayBuffer, { type: "array" });
      const sheetName = workbook.SheetNames[0];
      const sheet = workbook.Sheets[sheetName];
      const rows = utils.sheet_to_json(sheet, { header: 1 }) as unknown[];
      const normalized = rows
        .map((row) =>
          (row as unknown[])
            .map((cell) => String(cell ?? "").trim())
            .filter((cell) => cell !== "")
        )
        .filter((row) => row.length > 0);
      return { text: "", rows: normalized };
    }

    return { text: await importFile.value.text(), rows: null };
  };

  const parseImportItems = (payload: {
    text: string;
    rows: string[][] | null;
  }) => {
    const typeCode = currentType.value?.code || "";
    const isCollege = typeCode === DICT_CODES.COLLEGE;
    const isMajorCategory = typeCode === DICT_CODES.MAJOR_CATEGORY;

    const isHeader = (parts: string[]) => {
      if (parts.length < 2) return false;
      const header = parts.map((part) => part.toLowerCase());
      if (isCollege) {
        return header[0] === "cno" && header[1] === "cname";
      }
      if (isMajorCategory) {
        return header[0] === "subno" && header[1] === "sub";
      }
      return false;
    };

    let rows: string[][] = [];
    if (payload.rows && payload.rows.length > 0) {
      rows = payload.rows;
    } else {
      const lines = payload.text
        .split(/\r?\n/)
        .map((line) => line.trim())
        .filter(Boolean);
      rows = lines
        .map((line) => line.split(/,|\t/).map((part) => part.trim()))
        .filter((parts) => parts.length > 0);
    }

    if (rows.length > 0 && isHeader(rows[0])) {
      rows.shift();
    }

    return rows
      .map((parts) => {
        let label = parts[0] || "";
        let value = showCode.value ? parts[1] || label : label;
        if (isCollege || isMajorCategory) {
          value = parts[0] || "";
          label = parts[1] || "";
        }
        return { label, value };
      })
      .filter((item) => item.label && item.value);
  };

  const submitImport = async () => {
    const type = currentType.value;
    if (!type) return;
    importLoading.value = true;
    try {
      const content = await readImportContent();
      if (
        !content.text.trim() &&
        (!content.rows || content.rows.length === 0)
      ) {
        ElMessage.warning("请上传文件或填写导入内容");
        return;
      }
      const itemsToImport = parseImportItems(content);
      if (itemsToImport.length === 0) {
        ElMessage.warning("没有可导入的数据");
        return;
      }
      const res = (await bulkCreateDictionaryItems({
        dict_type: type.id,
        items: itemsToImport,
      })) as { created?: number; skipped?: number };
      const created = res?.created ?? 0;
      const skipped = res?.skipped ?? 0;
      ElMessage.success(`导入完成：新增 ${created} 条，跳过 ${skipped} 条`);
      importDialogVisible.value = false;
      await fetchItems(type.code);
    } catch (error) {
      console.error(error);
      ElMessage.error("导入失败");
    } finally {
      importLoading.value = false;
    }
  };

  const clearItems = async () => {
    const type = currentType.value;
    if (!type) return;
    try {
      await ElMessageBox.confirm(
        `确认清空 ${type.name} 吗？此操作不可恢复。`,
        "警告",
        {
          confirmButtonText: "确定清空",
          cancelButtonText: "取消",
          type: "warning",
        }
      );
      await clearDictionaryItems({ dict_type: type.id });
      ElMessage.success("清空成功");
      await fetchItems(type.code);
    } catch (error) {
      if (error !== "cancel") {
        ElMessage.error("清空失败，可能存在被引用的条目");
      }
    }
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
      form.budget = Number(item.extra_data?.budget || 0);
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

    try {
      await formRef.value.validate();
    } catch {
      return;
    }

    if (type.code === DICT_CODES.MAJOR_CATEGORY) {
      const normalizedLabel = form.label.trim();
      const duplicateLabel = items.value.some(
        (item) =>
          item.id !== editingId.value && item.label.trim() === normalizedLabel
      );
      if (duplicateLabel) {
        ElMessage.error("专业大类显示名称不能重复");
        return;
      }
    }

    submitting.value = true;
    try {
      const finalValue = showCode.value ? form.value : form.label;

      const extraData: Record<string, unknown> = {};
      if (showBudget.value) {
        extraData.budget = Number(form.budget) || 0;
      }

      let payload: FormData | Record<string, unknown>;
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
  };

  const deleteItem = async (item: DictionaryItem) => {
    try {
      await ElMessageBox.confirm(
        `确认要删除 "${item.label}" 吗？此操作不可恢复。`,
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

  watch(currentType, async (newType, oldType) => {
    // 只有当类型真正改变时才重新加载（避免初始化时重复加载）
    if (newType && newType.code !== oldType?.code) {
      await fetchItems(newType.code);
    } else if (!newType) {
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
    importDialogVisible,
    importLoading,
    importText,
    form,
    rules,
    fetchItems,
    handleTypeSelect,
    openImportDialog,
    handleImportFileChange,
    submitImport,
    clearItems,
    resetImport,
    openAddDialog,
    editItem,
    resetForm,
    handleFileChange,
    handleRemoveFile,
    submitForm,
    deleteItem,
  };
}
