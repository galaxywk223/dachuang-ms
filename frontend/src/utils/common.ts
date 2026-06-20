// 通用工具函数
export const formatDate = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleDateString("zh-CN");
};

export const formatTime = (dateString: string): string => {
  const date = new Date(dateString);
  return date.toLocaleString("zh-CN");
};

export const getStatusType = (status: string): string => {
  const statusMap: Record<string, string> = {
    DRAFT: "info",
    PENDING_LEVEL1: "warning",
    PENDING_LEVEL2: "warning",
    APPROVED: "success",
    REJECTED: "danger",
  };
  return statusMap[status] || "info";
};

export const getStatusText = (status: string): string => {
  const statusMap: Record<string, string> = {
    DRAFT: "草稿",
    PENDING_LEVEL1: "待一级审核",
    PENDING_LEVEL2: "待二级审核",
    APPROVED: "已通过",
    REJECTED: "已拒绝",
  };
  return statusMap[status] || "未知状态";
};

export const saveBlob = (blob: Blob, filename: string): void => {
  const objectUrl = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = objectUrl;
  link.download = filename || "文件";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(objectUrl);
};

type DownloadBlobOptions = {
  filename: string;
  fallbackType: string;
};

class DownloadResponseError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "DownloadResponseError";
  }
}

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null;

const getResponseMessage = (value: unknown): string | null => {
  if (!isRecord(value)) return null;
  if (typeof value.message === "string" && value.message) {
    return value.message;
  }
  if (typeof value.detail === "string" && value.detail) {
    return value.detail;
  }
  return null;
};

const parseJsonBlobMessage = async (value: Blob): Promise<string | null> => {
  if (!value.type.includes("application/json")) return null;
  try {
    return getResponseMessage(JSON.parse(await value.text()));
  } catch {
    return null;
  }
};

export const toDownloadBlob = async (
  value: unknown,
  options: DownloadBlobOptions
): Promise<Blob> => {
  if (value instanceof Blob) {
    const message = await parseJsonBlobMessage(value);
    if (message) {
      throw new DownloadResponseError(message);
    }
    if (value.type.includes("application/json")) {
      throw new DownloadResponseError("下载失败");
    }
    return value;
  }

  const message = getResponseMessage(value);
  if (message) {
    throw new DownloadResponseError(message);
  }

  if (value instanceof ArrayBuffer) {
    return new Blob([value], { type: options.fallbackType });
  }
  if (ArrayBuffer.isView(value)) {
    return new Blob([value.buffer as ArrayBuffer], {
      type: options.fallbackType,
    });
  }
  if (typeof value === "string") {
    return new Blob([value], { type: options.fallbackType });
  }
  return new Blob([JSON.stringify(value ?? "")], {
    type: options.fallbackType,
  });
};

export const saveDownload = async (
  value: unknown,
  options: DownloadBlobOptions
): Promise<void> => {
  const blob = await toDownloadBlob(value, options);
  saveBlob(blob, options.filename);
};

export const getDownloadErrorMessage = async (
  error: unknown,
  fallback: string
): Promise<string> => {
  if (error instanceof DownloadResponseError) return error.message;
  if (!isRecord(error)) return fallback;

  const response = error.response;
  if (!isRecord(response)) return fallback;

  const data = response.data;
  if (data instanceof Blob) {
    return (await parseJsonBlobMessage(data)) || fallback;
  }
  return getResponseMessage(data) || fallback;
};
