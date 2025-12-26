import { computed, onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { useRouter } from "vue-router";
import { useDictionary } from "@/composables/useDictionary";
import { DICT_CODES } from "@/api/dictionaries";
import {
  batchUpdateProjectStatus,
  deleteProjectById,
} from "@/api/projects/admin";
import { pushProjectToExternal } from "@/api/projects";
import { batchSendNotifications } from "@/api/notifications";
import { useProjectExport } from "./useProjectExport";
import { useProjectSearch } from "./useProjectSearch";
import { useProjectTable } from "./useProjectTable";

export function useAllProjects() {
  const router = useRouter();
  const { loadDictionaries, getOptions } = useDictionary();

  const filters = reactive({
    search: "",
    level: "",
    category: "",
    status: "",
  });

  const {
    loading,
    projects,
    selectedRows,
    currentPage,
    pageSize,
    total,
    fetchProjects,
    handlePageChange,
    handleSizeChange,
    handleSelectionChange,
  } = useProjectTable(filters);

  const { handleSearch, handleReset } = useProjectSearch(
    filters,
    fetchProjects,
    currentPage
  );

  const {
    handleBatchExport,
    handleBatchDownload,
    handleBatchExportDocs,
    handleBatchExportNotices,
    handleBatchExportCertificates,
  } = useProjectExport(filters, selectedRows);

  const batchStatusDialogVisible = ref(false);
  const batchNotifyDialogVisible = ref(false);
  const batchStatusLoading = ref(false);
  const batchNotifyLoading = ref(false);
  const batchStatusForm = reactive({ status: "" });
  const batchNotifyForm = reactive({
    title: "",
    content: "",
  });

  const levelOptions = computed(() => getOptions(DICT_CODES.PROJECT_LEVEL));
  const categoryOptions = computed(() => getOptions(DICT_CODES.PROJECT_CATEGORY));
  const statusOptions = computed(() => getOptions(DICT_CODES.PROJECT_STATUS));

  const handleView = (row: any) => {
    router.push({
      name: "level1-project-detail",
      params: { id: row.id },
      query: { mode: "view" },
    });
  };

  const handleEdit = (row: any) => {
    router.push({
      name: "level1-project-detail",
      params: { id: row.id },
      query: { mode: "edit" },
    });
  };

  const handleDelete = async (row: any) => {
    try {
      await ElMessageBox.confirm(
        `确定要删除项目"${row.title}"吗？此操作不可恢复！`,
        "警告",
        {
          confirmButtonText: "确定删除",
          cancelButtonText: "取消",
          type: "warning",
        }
      );
      await deleteProjectById(row.id);
      ElMessage.success("删除成功");
      fetchProjects();
    } catch (error) {
      if (error !== "cancel") ElMessage.error("删除失败");
    }
  };

  const ensureSelection = () => {
    if (selectedRows.value.length === 0) {
      ElMessage.warning("请先勾选项目");
      return false;
    }
    return true;
  };

  const handlePushToExternal = async () => {
    if (!ensureSelection()) return;
    try {
      await ElMessageBox.confirm(
        "确定要将选中的项目推送至省平台吗？",
        "提示",
        {
          confirmButtonText: "确定推送",
          cancelButtonText: "取消",
          type: "info",
        }
      );

      loading.value = true;
      const ids = selectedRows.value.map((row) => row.id);
      const res: any = await pushProjectToExternal({
        project_ids: ids,
        target: "PROVINCIAL_PLATFORM",
      });

      if (res.code === 200) {
        ElMessage.success(res.message || "推送完成");
      } else {
        ElMessage.warning(res.message || "推送部分失败");
      }
    } catch (error) {
      if (error !== "cancel") ElMessage.error("推送失败");
    } finally {
      loading.value = false;
    }
  };

  const openBatchStatusDialog = () => {
    if (!ensureSelection()) return;
    batchStatusForm.status = "";
    batchStatusDialogVisible.value = true;
  };

  const submitBatchStatus = async () => {
    if (!batchStatusForm.status) {
      ElMessage.warning("请选择目标状态");
      return;
    }
    batchStatusLoading.value = true;
    try {
      const payload = {
        project_ids: selectedRows.value.map((row) => row.id),
        status: batchStatusForm.status,
      };
      const res: any = await batchUpdateProjectStatus(payload);
      if (res.code === 200) {
        ElMessage.success("状态更新成功");
        batchStatusDialogVisible.value = false;
        fetchProjects();
      }
    } catch {
      ElMessage.error("状态更新失败");
    } finally {
      batchStatusLoading.value = false;
    }
  };

  const openBatchNotifyDialog = () => {
    if (!ensureSelection()) return;
    batchNotifyForm.title = "";
    batchNotifyForm.content = "";
    batchNotifyDialogVisible.value = true;
  };

  const submitBatchNotify = async () => {
    if (!batchNotifyForm.title || !batchNotifyForm.content) {
      ElMessage.warning("请填写通知标题和内容");
      return;
    }
    batchNotifyLoading.value = true;
    try {
      const recipients = Array.from(
        new Set(selectedRows.value.map((row) => row.leader).filter(Boolean))
      );
      const res: any = await batchSendNotifications({
        title: batchNotifyForm.title,
        content: batchNotifyForm.content,
        recipients,
      });
      if (res.code === 200) {
        ElMessage.success("通知已发送");
        batchNotifyDialogVisible.value = false;
      }
    } catch (error: any) {
      ElMessage.error(error.response?.data?.message || "发送失败");
    } finally {
      batchNotifyLoading.value = false;
    }
  };

  const getLevelType = (level: string) => {
    if (level === "NATIONAL") return "danger";
    if (level === "PROVINCIAL") return "warning";
    return "info";
  };

  const getLabel = (options: any[], value: string) => {
    const found = options.find((opt) => opt.value === value);
    return found ? found.label : value;
  };

  onMounted(() => {
    loadDictionaries([
      DICT_CODES.PROJECT_LEVEL,
      DICT_CODES.PROJECT_CATEGORY,
      DICT_CODES.PROJECT_STATUS,
    ]);
    fetchProjects();
  });

  return {
    loading,
    projects,
    selectedRows,
    currentPage,
    pageSize,
    total,
    filters,
    levelOptions,
    categoryOptions,
    statusOptions,
    handleSearch,
    handleReset,
    handlePageChange,
    handleSizeChange,
    handleView,
    handleEdit,
    handleDelete,
    handleSelectionChange,
    handleBatchExport,
    handleBatchDownload,
    handleBatchExportDocs,
    handleBatchExportNotices,
    handleBatchExportCertificates,
    handlePushToExternal,
    openBatchStatusDialog,
    submitBatchStatus,
    openBatchNotifyDialog,
    submitBatchNotify,
    batchStatusDialogVisible,
    batchNotifyDialogVisible,
    batchStatusLoading,
    batchNotifyLoading,
    batchStatusForm,
    batchNotifyForm,
    getLevelType,
    getLabel,
  };
}
