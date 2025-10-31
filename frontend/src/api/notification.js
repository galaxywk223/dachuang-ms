import request from '@/utils/request'

/**
 * 获取通知列表
 */
export function getNotifications(params) {
  return request({
    url: '/notifications/',
    method: 'get',
    params
  })
}

/**
 * 标记为已读
 */
export function markNotificationRead(id) {
  return request({
    url: `/notifications/${id}/mark_read/`,
    method: 'post'
  })
}

/**
 * 标记所有为已读
 */
export function markAllNotificationsRead() {
  return request({
    url: '/notifications/mark-all-read/',
    method: 'post'
  })
}

/**
 * 获取未读通知数量
 */
export function getUnreadCount() {
  return request({
    url: '/notifications/unread_count/',
    method: 'get'
  })
}
