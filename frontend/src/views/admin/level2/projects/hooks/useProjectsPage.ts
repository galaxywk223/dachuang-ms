import { computed, onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";

import { useDictionary } from "@/composables/useDictionary";
import { DICT_CODES } from "@/api/dictionaries";
import { getProjects, deleteProject } from "@/api/projects";
import {
  exportProjects,
  batchDownloadAttachments,
  batchExportDocs,
  batchExportNotices,
  batchExportCertificates,
  batchUpdateProjectStatus,
} from "@/api/projects/admin";
import { batchSendNotifications } from "@/api/notifications";

type ProjectRow = {
  id: number;
  title?: string;
  leader?: number | string;
};

type ProjectListResponse = {
  results?: ProjectRow[];
  count?: number;
  data?: {
    results?: ProjectRow[];
    count?: number;
  };
};

type OptionItem = {
  value: string;
  label: string;
};

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null;

const getErrorMessage = (error: unknown, fallback: string) => {
  if (!isRecord(error)) return fallback;
  const response = error.response;
  if (isRecord(response) && isRecord(response.data) && typeof response.data.message === "string") {
    return response.data.message;
  }
  if (typeof error.message === "string") return error.message;
  return fallback;
};

const toBlob = (value: unknown, fallbackType: string) => {
  if (value instanceof Blob) return value;
  if (value instanceof ArrayBuffer) return new Blob([value], { type: fallbackType });
  if (typeof value === "string") return new Blob([value], { type: fallbackType });
  return new Blob([JSON.stringify(value ?? "")], { type: fallbackType });
};

export function useProjectsPage() {
  const { loadDictionaries, getOptions } = useDictionary();

  const loading = ref(false);
  const projects = ref<ProjectRow[]>([]);
  const selectedRows = ref<ProjectRow[]>([]);
  const currentPage = ref(1);
  const pageSize = ref(10);
  const total = ref(0);
  const batchStatusDialogVisible = ref(false);
  const batchNotifyDialogVisible = ref(false);
  const batchStatusLoading = ref(false);
  const batchNotifyLoading = ref(false);
  const batchStatusForm = reactive({ status: "" });
  const batchNotifyForm = reactive({
    title: "",
    content: "",
  });

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

      const res = (await getProjects(params)) as ProjectListResponse | ProjectRow[];
      if (isRecord(res) && Array.isArray(res.results)) {
        projects.value = res.results ?? [];
        total.value = res.count ?? projects.value.length;
      } else if (isRecord(res) && isRecord(res.data) && Array.isArray(res.data?.results)) {
        projects.value = res.data?.results ?? [];
        total.value = res.data?.count ?? projects.value.length;
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

  const handleCreate = () => {
    ElMessage.info("申报功能请在学生端进行或开发管理员代申请功能");
  };

  const handleView = (row: ProjectRow) => ElMessage.success(`正在查看项目: ${row.title}`);
  const handleEdit = (row: ProjectRow) => ElMessage.warning(`编辑项目: ${row.title}`);
  const handleDelete = async (row: ProjectRow) => {
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
      await deleteProject(row.id);
      ElMessage.success("删除成功");
      fetchProjects();
    } catch (error) {
      if (error !== "cancel") ElMessage.error("删除失败");
    }
  };

  const handleSelectionChange = (val: ProjectRow[]) => {
    selectedRows.value = val;
  };

  const ensureSelection = () => {
    if (selectedRows.value.length === 0) {
      ElMessage.warning("请先勾选项目");
      return false;
    }
    return true;
  };

  const handleBatchExport = async () => {
    try {
      ElMessage.info("正在生成导出文件，请稍候...");
      const params: Record<string, string> = {};

      if (selectedRows.value.length > 0) {
        params.ids = selectedRows.value.map((row) => row.id).join(",");
      } else {
        params.search = filters.search;
        params.level = filters.level;
        params.category = filters.category;
        params.status = filters.status;
      }

      const res = await exportProjects(params);
      const blob = toBlob(res, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
      downloadFile(blob, "项目数据.xlsx");
      ElMessage.success("导出成功");
    } catch {
      ElMessage.error("导出失败");
    }
  };

  const handleBatchExportDocs = async () => {
    if (!ensureSelection()) return;
    try {
      ElMessage.info("正在生成申报书，请稍候...");
      const ids = selectedRows.value.map((row) => row.id).join(",");
      const res = await batchExportDocs({ ids });
      const blob = toBlob(res, "application/zip");
      downloadFile(blob, "项目申报书.zip");
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
      const res = await batchExportNotices({ ids });
      const blob = toBlob(res, "application/zip");
      downloadFile(blob, "立项通知书.zip");
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
      const res = await batchExportCertificates({ ids });
      const blob = toBlob(res, "application/zip");
      downloadFile(blob, "结题证书.zip");
      ElMessage.success("生成成功");
    } catch {
      ElMessage.error("生成失败");
    }
  };

  const handleBatchDownload = async () => {
    try {
      ElMessage.info("正在打包附件，请稍候...");
      const params: Record<string, string> = {};

      if (selectedRows.value.length > 0) {
        params.ids = selectedRows.value.map((row) => row.id).join(",");
      } else {
        params.search = filters.search;
        params.level = filters.level;
        params.category = filters.category;
        params.status = filters.status;
      }

      const res = await batchDownloadAttachments(params);
      if (res instanceof Blob && res.type === "application/json") {
        const text = await res.text();
        const json = JSON.parse(text);
        ElMessage.error(json.message || "下载失败");
        return;
      }
      const blob = toBlob(res, "application/zip");
      downloadFile(blob, "项目附件.zip");
      ElMessage.success("下载成功");
    } catch {
      ElMessage.error("下载失败，可能没有可下载的附件");
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
      const res = await batchUpdateProjectStatus(payload);
      if (isRecord(res) && res.code === 200) {
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
        new Set(
          selectedRows.value
            .map((row) => row.leader)
            .filter((value): value is number => typeof value === "number")
        )
      );
      const res = await batchSendNotifications({
        title: batchNotifyForm.title,
        content: batchNotifyForm.content,
        recipients,
      });
      if (isRecord(res) && res.code === 200) {
        ElMessage.success("通知已发送");
        batchNotifyDialogVisible.value = false;
      }
    } catch (error) {
      ElMessage.error(getErrorMessage(error, "发送失败"));
    } finally {
      batchNotifyLoading.value = false;
    }
  };

  const handleBatchCommand = (command: string) => {
    if (command === "status") openBatchStatusDialog();
    if (command === "docs") handleBatchExportDocs();
    if (command === "notices") handleBatchExportNotices();
    if (command === "certs") handleBatchExportCertificates();
    if (command === "notify") openBatchNotifyDialog();
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

  const getLevelType = (level: string) => {
    if (level === "NATIONAL") return "danger";
    if (level === "PROVINCIAL") return "warning";
    return "info";
  };

  const getLabel = (options: OptionItem[], value: string) => {
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
    batchNotifyDialogVisible,
    batchNotifyForm,
    batchNotifyLoading,
    batchStatusDialogVisible,
    batchStatusForm,
    batchStatusLoading,
    categoryOptions,
    currentPage,
    filters,
    getLabel,
    getLevelType,
    handleBatchCommand,
    handleBatchDownload,
    handleBatchExport,
    handleCreate,
    handleDelete,
    handleEdit,
    handlePageChange,
    handleReset,
    handleSearch,
    handleSelectionChange,
    handleSizeChange,
    handleView,
    levelOptions,
    loading,
    openBatchNotifyDialog,
    openBatchStatusDialog,
    pageSize,
    projects,
    selectedRows,
    statusOptions,
    submitBatchNotify,
    submitBatchStatus,
    total,
  };
}
