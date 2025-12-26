import { ElMessage } from "element-plus";
import {
  batchDownloadAttachments,
  batchExportCertificates,
  batchExportDocs,
  batchExportNotices,
  exportProjects,
} from "@/api/admin";

export function useProjectExport(
  filters: {
    search: string;
    level: string;
    category: string;
    status: string;
  },
  selectedRows: { value: any[] }
) {
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

  return {
    handleBatchExport,
    handleBatchDownload,
    handleBatchExportDocs,
    handleBatchExportNotices,
    handleBatchExportCertificates,
  };
}
