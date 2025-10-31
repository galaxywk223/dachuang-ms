import request from "@/utils/request";

// 管理员 - 项目审核相关接口

/**
 * 获取待审核项目列表
 */
export function getReviewProjects(params: any) {
  return request({
    url: "/projects/admin/review/pending/",
    method: "get",
    params,
  });
}

/**
 * 审核通过项目
 */
export function approveProject(id: number, data: any) {
  return request({
    url: `/projects/admin/review/${id}/approve/`,
    method: "post",
    data,
  });
}

/**
 * 驳回项目
 */
export function rejectProject(id: number, data: any) {
  return request({
    url: `/projects/admin/review/${id}/reject/`,
    method: "post",
    data,
  });
}

// 管理员 - 项目管理相关接口

/**
 * 获取所有项目列表
 */
export function getAllProjects(params: any) {
  return request({
    url: "/projects/admin/manage/",
    method: "get",
    params,
  });
}

/**
 * 获取项目详情
 */
export function getProjectDetail(id: number) {
  return request({
    url: `/projects/admin/manage/${id}/`,
    method: "get",
  });
}

/**
 * 更新项目信息
 */
export function updateProjectInfo(id: number, data: any) {
  return request({
    url: `/projects/admin/manage/${id}/`,
    method: "put",
    data,
  });
}

/**
 * 删除项目
 */
export function deleteProjectById(id: number) {
  return request({
    url: `/projects/admin/manage/${id}/`,
    method: "delete",
  });
}

/**
 * 获取项目统计数据
 */
export function getProjectStatistics() {
  return request({
    url: "/projects/admin/manage/statistics/",
    method: "get",
  });
}
