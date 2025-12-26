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
