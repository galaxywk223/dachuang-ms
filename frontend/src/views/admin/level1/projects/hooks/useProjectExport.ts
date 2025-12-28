import { ElMessage } from "element-plus";
import {
  batchDownloadAttachments,
  batchExportCertificates,
  batchExportDocs,
  batchExportNotices,
  exportProjects,
} from "@/api/projects/admin";

type ProjectRow = {
  id: number;
};

export function useProjectExport(
  filters: {
    search: string;
    level: string;
    category: string;
    status: string;
  },
  selectedRows: { value: ProjectRow[] }
) {
  const ensureSelection = () => {
    if (selectedRows.value.length === 0) {
      ElMessage.warning("请先勾选项目");
      return false;
    }
    return true;
  };

  const toBlob = (value: unknown, type: string) => {
    if (value instanceof Blob) return value;
    if (typeof value === "string") return new Blob([value], { type });
    if (value instanceof ArrayBuffer) return new Blob([value], { type });
    if (ArrayBuffer.isView(value)) {
      return new Blob([value.buffer as ArrayBuffer], { type });
    }
    return new Blob([JSON.stringify(value ?? "")], { type });
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
      downloadFile(toBlob(res, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"), "项目数据.xlsx");
      ElMessage.success("导出成功");
    } catch {
      ElMessage.error("导出失败");
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
      downloadFile(toBlob(res, "application/zip"), "项目附件.zip");
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
      const res = await batchExportDocs({ ids });
      downloadFile(toBlob(res, "application/zip"), "项目申报书.zip");
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
      downloadFile(toBlob(res, "application/zip"), "立项通知书.zip");
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
      downloadFile(toBlob(res, "application/zip"), "结题证书.zip");
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
