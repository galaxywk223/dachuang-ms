import request from "@/utils/request";
import type {
  ApiResponse,
  Review,
  PaginatedResponse,
  ReviewForm,
} from "@/types";

/**
 * 获取审核列表
 */
export function getReviews(
  params?: Record<string, any>
): Promise<ApiResponse<PaginatedResponse<Review>>> {
  return request({
    url: "/reviews/",
    method: "get",
    params,
  });
}

/**
 * 获取待审核列表
 */
export function getPendingReviews(
  params?: Record<string, any>
): Promise<ApiResponse<PaginatedResponse<Review>>> {
  return request({
    url: "/reviews/pending/",
    method: "get",
    params,
  });
}

/**
 * 审核项目
 */
export function reviewProject(
  id: number,
  data: ReviewForm
): Promise<ApiResponse<Review>> {
  return request({
    url: `/reviews/${id}/review/`,
    method: "post",
    data,
  });
}

/**
 * 提交到一级审核
 */
export function submitToLevel1(projectId: number): Promise<ApiResponse<void>> {
  return request({
    url: "/reviews/submit-to-level1/",
    method: "post",
    data: {
      project_id: projectId,
    },
  });
}

/**
 * 获取审核详情
 */
export function getReviewDetail(id: number): Promise<ApiResponse<Review>> {
  return request({
    url: `/reviews/${id}/`,
    method: "get",
  });
}

/**
 * 批量导出审核数据
 */
export function exportReviewsExcel(
  params?: Record<string, any>
): Promise<Blob> {
  return request({
    url: "/reviews/export-excel/",
    method: "get",
    params,
    responseType: "blob",
  });
}
