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
}) {
  return request({
    url: "/notifications/batch-send/",
    method: "post",
    data,
  });
}

export function getNotifications(params?: any) {
  return request({
    url: "/notifications/",
    method: "get",
    params,
  });
}

export function markNotificationRead(id: number) {
  return request({
    url: `/notifications/${id}/mark_read/`,
    method: "post",
  });
}

export function markAllNotificationsRead() {
  return request({
    url: "/notifications/mark-all-read/",
    method: "post",
  });
}

export function getUnreadCount() {
  return request({
    url: "/notifications/unread_count/",
    method: "get",
  });
}
