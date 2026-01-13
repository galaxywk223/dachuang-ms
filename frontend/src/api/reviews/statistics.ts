import request from "@/utils/request";

/**
 * 获取各类审核的待审核数量
 */
export function getPendingCounts() {
  return request({
    url: "/reviews/statistics/pending-counts/",
    method: "get",
  });
}
