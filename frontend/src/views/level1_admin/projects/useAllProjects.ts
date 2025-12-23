import { computed, onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { useRouter } from "vue-router";
import { useDictionary } from "@/composables/useDictionary";
import { DICT_CODES } from "@/api/dictionary";
import {
  batchDownloadAttachments,
  batchExportCertificates,
  batchExportDocs,
  batchExportNotices,
  batchUpdateProjectStatus,
  deleteProjectById,
  exportProjects,
  getAllProjects,
} from "@/api/admin";
import { batchSendNotifications } from "@/api/notifications";

export function useAllProjects() {
  const router = useRouter();
  const { loadDictionaries, getOptions } = useDictionary();

  const loading = ref(false);
  const projects = ref<any[]>([]);
  const selectedRows = ref<any[]>([]);
  const batchStatusDialogVisible = ref(false);
  const batchNotifyDialogVisible = ref(false);
  const batchStatusLoading = ref(false);
  const batchNotifyLoading = ref(false);
  const batchStatusForm = reactive({ status: "" });
  const batchNotifyForm = reactive({
    title: "",
    content: "",
  });
  const currentPage = ref(1);
  const pageSize = ref(10);
  const total = ref(0);

  const filters = reactive({
    search: "",
    level: "",
    category: "",
    status: "",
  });

  const levelOptions = computed(() => getOptions(DICT_CODES.PROJECT_LEVEL));
  const categoryOptions = computed(() => getOptions(DICT_CODES.PROJECT_CATEGORY));
  const statusOptions = computed(() => getOptions(DICT_CODES.PROJECT_STATUS));

  const fetchProjects = async () => {
    loading.value = true;
    try {
      const params = {
        page: currentPage.value,
        page_size: pageSize.value,
        search: filters.search,
        level: filters.level,
        category: filters.category,
        status: filters.status,
      };

      const res: any = await getAllProjects(params);
      if (res.results) {
        projects.value = res.results;
        total.value = res.count;
      } else if (res.data && res.data.results) {
        projects.value = res.data.results;
        total.value = res.data.count;
      } else {
        projects.value = Array.isArray(res) ? res : [];
        total.value = projects.value.length;
      }
    } catch {
      ElMessage.error("获取项目列表失败");
    } finally {
      loading.value = false;
    }
  };

  const handleSearch = () => {
    currentPage.value = 1;
    fetchProjects();
  };

  const handleReset = () => {
    filters.search = "";
    filters.level = "";
    filters.category = "";
    filters.status = "";
    currentPage.value = 1;
    fetchProjects();
  };

  const handlePageChange = () => fetchProjects();
  const handleSizeChange = () => {
    currentPage.value = 1;
    fetchProjects();
  };

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
        `确定要删除项目\"${row.title}\"吗？此操作不可恢复！`,
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

  const handleSelectionChange = (val: any[]) => {
    selectedRows.value = val;
  };

  const ensureSelection = () => {
    if (selectedRows.value.length === 0) {
      ElMessage.warning("请先勾选项目");
      return false;
    }
    return true;
  };

  const downloadFile = (blob: Blob, filename: string) => {
    const url = window.URL.createObjectURL(new Blob([blob]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleBatchExport = async () => {
    try {
      ElMessage.info("正在生成导出文件，请稍候...");
      const params: any = {};

      if (selectedRows.value.length > 0) {
        params.ids = selectedRows.value.map((row) => row.id).join(",");
      } else {
        params.search = filters.search;
        params.level = filters.level;
        params.category = filters.category;
        params.status = filters.status;
      }

      const res: any = await exportProjects(params);
      downloadFile(res, "项目数据.xlsx");
      ElMessage.success("导出成功");
    } catch {
      ElMessage.error("导出失败");
    }
  };

  const handleBatchDownload = async () => {
    try {
      ElMessage.info("正在打包附件，请稍候...");
      const params: any = {};

      if (selectedRows.value.length > 0) {
        params.ids = selectedRows.value.map((row) => row.id).join(",");
      } else {
        params.search = filters.search;
        params.level = filters.level;
        params.category = filters.category;
        params.status = filters.status;
      }

      const res: any = await batchDownloadAttachments(params);
      if (res.type === "application/json") {
        const text = await res.text();
        const json = JSON.parse(text);
        ElMessage.error(json.message || "下载失败");
        return;
      }
      downloadFile(res, "项目附件.zip");
      ElMessage.success("下载成功");
    } catch {
      ElMessage.error("下载失败，可能没有可下载的附件");
    }
  };

  const handleBatchExportDocs = async () => {
    if (!ensureSelection()) return;
    try {
      ElMessage.info("正在生成申报书，请稍候...");
      const ids = selectedRows.value.map((row) => row.id).join(",");
      const res: any = await batchExportDocs({ ids });
      downloadFile(res, "项目申报书.zip");
      ElMessage.success("导出成功");
    } catch {
      ElMessage.error("导出失败");
    }
  };

  const handleBatchExportNotices = async () => {
    if (!ensureSelection()) return;
    try {
      ElMessage.info("正在生成立项通知书，请稍候...");
      const ids = selectedRows.value.map((row) => row.id).join(",");
      const res: any = await batchExportNotices({ ids });
      downloadFile(res, "立项通知书.zip");
      ElMessage.success("生成成功");
    } catch {
      ElMessage.error("生成失败");
    }
  };

  const handleBatchExportCertificates = async () => {
    if (!ensureSelection()) return;
    try {
      ElMessage.info("正在生成结题证书，请稍候...");
      const ids = selectedRows.value.map((row) => row.id).join(",");
      const res: any = await batchExportCertificates({ ids });
      downloadFile(res, "结题证书.zip");
      ElMessage.success("生成成功");
    } catch {
      ElMessage.error("生成失败");
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

  const getStatusClass = (status: string) => {
    if (status.includes("APPROVED")) return "dot-success";
    if (status.includes("REJECTED")) return "dot-danger";
    if (status.includes("REVIEWING") || status.includes("AUDITING") || status === "SUBMITTED")
      return "dot-warning";
    return "dot-info";
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
    getStatusClass,
  };
}
