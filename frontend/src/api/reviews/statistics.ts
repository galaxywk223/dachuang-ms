import { apiRequest } from "@/utils/request";

export interface ReviewCounts {
  establishment: number;
  midterm: number;
  closure: number;
  change: number;
}

/**
 * 获取各类审核的待审核数量
 */
export function getPendingCounts() {
  return apiRequest<ReviewCounts>({
    url: "/reviews/statistics/pending-counts/",
    method: "get",
  });
}
