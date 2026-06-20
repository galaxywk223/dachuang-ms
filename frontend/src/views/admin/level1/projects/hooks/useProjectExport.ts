import { ElMessage } from "element-plus";
import {
  batchDownloadAttachments,
  batchExportCertificates,
  batchExportDocs,
  batchExportNotices,
  exportProjects,
} from "@/api/projects/admin";
import { getDownloadErrorMessage, saveDownload } from "@/utils/common";

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
      await saveDownload(res, {
        filename: "项目数据.xlsx",
        fallbackType:
          "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      });
      ElMessage.success("导出成功");
    } catch (error) {
      ElMessage.error(await getDownloadErrorMessage(error, "导出失败"));
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
      await saveDownload(res, {
        filename: "项目附件.zip",
        fallbackType: "application/zip",
      });
      ElMessage.success("下载成功");
    } catch (error) {
      ElMessage.error(
        await getDownloadErrorMessage(error, "下载失败，可能没有可下载的附件")
      );
    }
  };

  const handleBatchExportDocs = async () => {
    if (!ensureSelection()) return;
    try {
      ElMessage.info("正在生成申报书，请稍候...");
      const ids = selectedRows.value.map((row) => row.id).join(",");
      const res = await batchExportDocs({ ids });
      await saveDownload(res, {
        filename: "项目申报书.zip",
        fallbackType: "application/zip",
      });
      ElMessage.success("导出成功");
    } catch (error) {
      ElMessage.error(await getDownloadErrorMessage(error, "导出失败"));
    }
  };

  const handleBatchExportNotices = async () => {
    if (!ensureSelection()) return;
    try {
      ElMessage.info("正在生成立项通知书，请稍候...");
      const ids = selectedRows.value.map((row) => row.id).join(",");
      const res = await batchExportNotices({ ids });
      await saveDownload(res, {
        filename: "立项通知书.zip",
        fallbackType: "application/zip",
      });
      ElMessage.success("生成成功");
    } catch (error) {
      ElMessage.error(await getDownloadErrorMessage(error, "生成失败"));
    }
  };

  const handleBatchExportCertificates = async () => {
    if (!ensureSelection()) return;
    try {
      ElMessage.info("正在生成结题证书，请稍候...");
      const ids = selectedRows.value.map((row) => row.id).join(",");
      const res = await batchExportCertificates({ ids });
      await saveDownload(res, {
        filename: "结题证书.zip",
        fallbackType: "application/zip",
      });
      ElMessage.success("生成成功");
    } catch (error) {
      ElMessage.error(await getDownloadErrorMessage(error, "生成失败"));
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
