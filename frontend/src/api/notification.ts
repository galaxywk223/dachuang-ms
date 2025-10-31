import request from "@/utils/request";
import type { ApiResponse, Notification, PaginatedResponse } from "@/types";

/**
 * 获取通知列表
 */
export function getNotifications(
  params?: Record<string, any>
): Promise<ApiResponse<PaginatedResponse<Notification>>> {
  return request({
    url: "/notifications/",
    method: "get",
    params,
  });
}

/**
 * 标记为已读
 */
export function markNotificationRead(id: number): Promise<ApiResponse<void>> {
  return request({
    url: `/notifications/${id}/mark_read/`,
    method: "post",
  });
}

/**
 * 标记所有为已读
 */
export function markAllNotificationsRead(): Promise<ApiResponse<void>> {
  return request({
    url: "/notifications/mark-all-read/",
    method: "post",
  });
}

/**
 * 获取未读通知数量
 */
export function getUnreadCount(): Promise<ApiResponse<{ count: number }>> {
  return request({
    url: "/notifications/unread_count/",
    method: "get",
  });
}
