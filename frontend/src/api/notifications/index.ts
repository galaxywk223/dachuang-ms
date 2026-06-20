import request from "@/utils/request";

/**
 * 批量发送通知（管理员）
 */
export function batchSendNotifications(data: {
  title: string;
  content: string;
  recipients?: number[];
  role?: string;
  college?: string;
}): Promise<unknown> {
  return request({
    url: "/notifications/batch-send/",
    method: "post",
    data,
  });
}

export function getNotifications(params?: Record<string, unknown>): Promise<unknown> {
  return request({
    url: "/notifications/",
    method: "get",
    params,
  });
}

export function markNotificationRead(id: number): Promise<unknown> {
  return request({
    url: `/notifications/${id}/mark_read/`,
    method: "post",
  });
}

export function markAllNotificationsRead(): Promise<unknown> {
  return request({
    url: "/notifications/mark-all-read/",
    method: "post",
  });
}

export function getUnreadCount(): Promise<unknown> {
  return request({
    url: "/notifications/unread_count/",
    method: "get",
  });
}

export function getPlatformNotices(
  params?: Record<string, unknown>
): Promise<unknown> {
  return request({
    url: "/notifications/notices/",
    method: "get",
    params,
  });
}

export function savePlatformNotice(
  data: Record<string, unknown>,
  id?: number
): Promise<unknown> {
  return request({
    url: id ? `/notifications/notices/${id}/` : "/notifications/notices/",
    method: id ? "patch" : "post",
    data,
  });
}

export function getPlatformMaterials(
  params?: Record<string, unknown>
): Promise<unknown> {
  return request({
    url: "/notifications/materials/",
    method: "get",
    params,
  });
}

export function savePlatformMaterial(
  data: Record<string, unknown> | FormData,
  id?: number
): Promise<unknown> {
  return request({
    url: id ? `/notifications/materials/${id}/` : "/notifications/materials/",
    method: id ? "patch" : "post",
    data,
    headers: data instanceof FormData ? { "Content-Type": "multipart/form-data" } : {},
  });
}

export function recordMaterialDownload(id: number | string): Promise<unknown> {
  return request({
    url: `/notifications/materials/${id}/record_download/`,
    method: "post",
  });
}

export function downloadPlatformMaterial(id: number | string): Promise<unknown> {
  return request({
    url: `/notifications/materials/${id}/download/`,
    method: "get",
    responseType: "blob",
  });
}
