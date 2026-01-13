/**
 * 评审相关API
 */
import request from "@/utils/request";

/**
 * 评审操作参数接口
 */
export interface ReviewActionParams {
  action: "approve" | "reject";
  comments: string;
  score?: number | null;
  score_details?: { item_id: number; score: number | null }[];
  closure_rating?: string;
  reject_to?: string; // 旧参数，向后兼容
  target_node_id?: number | null; // 新参数，退回到指定节点ID
}

/**
 * 批量评审参数接口
 */
export interface BatchReviewParams {
  review_ids: number[];
  action: "approve" | "reject";
  comments: string;
  score?: number;
  closure_rating?: string;
  target_node_id?: number | null;
}

/**
 * 工作流节点接口
 */
export interface WorkflowNode {
  id: number;
  code: string;
  name: string;
  node_type: "SUBMIT" | "REVIEW" | "EXPERT_REVIEW" | "APPROVAL";
  role: string;
}

/**
 * 执行评审操作
 */
export function reviewAction(
  reviewId: number,
  data: ReviewActionParams
): Promise<unknown> {
  return request({
    url: `/reviews/${reviewId}/review/`,
    method: "post",
    data,
  });
}

/**
 * 修订评审记录
 */
export function reviseReview(
  reviewId: number,
  data: ReviewActionParams
): Promise<unknown> {
  return request({
    url: `/reviews/${reviewId}/revise/`,
    method: "post",
    data,
  });
}

/**
 * 获取可退回的目标节点列表
 */
export function getRejectTargets(
  reviewId: number
): Promise<{ code: number; message: string; data: WorkflowNode[] }> {
  return request({
    url: `/reviews/${reviewId}/reject-targets/`,
    method: "get",
  });
}

/**
 * 根据项目ID获取可退回的目标节点列表（用于管理员审核）
 */
export function getRejectTargetsByProject(
  projectId: number
): Promise<{ code: number; message: string; data: WorkflowNode[] }> {
  return request({
    url: `/projects/admin/review/${projectId}/reject-targets/`,
    method: "get",
  });
}

/**
 * 批量评审
 */
export function batchReview(data: BatchReviewParams): Promise<unknown> {
  return request({
    url: "/reviews/batch-review/",
    method: "post",
    data,
  });
}

/**
 * 获取待审核数量统计
 */
export function getPendingCounts(): Promise<unknown> {
  return request({
    url: "/reviews/statistics/pending-counts/",
    method: "get",
  });
}
