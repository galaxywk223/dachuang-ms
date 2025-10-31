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
