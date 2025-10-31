import request from "@/utils/request";

// 项目申请相关接口

/**
 * 创建项目申请
 */
export function createProjectApplication(data: any) {
  return request({
    url: "/projects/application/create/",
    method: "post",
    data,
  });
}

/**
 * 更新项目申请
 */
export function updateProjectApplication(id: number, data: any) {
  return request({
    url: `/projects/application/${id}/update/`,
    method: "put",
    data,
  });
}

/**
 * 获取我的项目列表
 */
export function getMyProjects(params?: any) {
  return request({
    url: "/projects/my-projects/",
    method: "get",
    params,
  });
}

/**
 * 获取我的草稿箱
 */
export function getMyDrafts(params?: any) {
  return request({
    url: "/projects/my-drafts/",
    method: "get",
    params,
  });
}

/**
 * 获取项目详情
 */
export function getProjectDetail(id: number) {
  return request({
    url: `/projects/${id}/`,
    method: "get",
  });
}

/**
 * 删除项目
 */
export function deleteProject(id: number) {
  return request({
    url: `/projects/${id}/`,
    method: "delete",
  });
}

// 结题管理相关接口

/**
 * 获取待结题项目列表
 */
export function getPendingClosureProjects(params?: any) {
  return request({
    url: "/projects/closure/pending/",
    method: "get",
    params,
  });
}

/**
 * 获取已申请结题项目列表
 */
export function getAppliedClosureProjects(params?: any) {
  return request({
    url: "/projects/closure/applied/",
    method: "get",
    params,
  });
}

/**
 * 获取结题草稿箱
 */
export function getClosureDrafts(params?: any) {
  return request({
    url: "/projects/closure/drafts/",
    method: "get",
    params,
  });
}

/**
 * 创建结题申请
 */
export function createClosureApplication(id: number, data: any) {
  return request({
    url: `/projects/closure/${id}/create/`,
    method: "post",
    data,
  });
}

/**
 * 更新结题申请
 */
export function updateClosureApplication(id: number, data: any) {
  return request({
    url: `/projects/closure/${id}/update/`,
    method: "put",
    data,
  });
}

/**
 * 删除结题草稿
 */
export function deleteClosureDraft(id: number) {
  return request({
    url: `/projects/closure/${id}/delete/`,
    method: "delete",
  });
}

/**
 * 获取项目成果列表
 */
export function getProjectAchievements(id: number) {
  return request({
    url: `/projects/closure/${id}/achievements/`,
    method: "get",
  });
}
