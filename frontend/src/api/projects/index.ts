import request from "@/utils/request";

// 项目申请相关接口

/**
 * 创建项目申请
 */
export function createProjectApplication(data: Record<string, unknown> | FormData): Promise<unknown> {
  return request({
    url: "/projects/application/create/",
    method: "post",
    data,
  });
}

/**
 * 获取项目列表
 */
export function getProjects(params?: Record<string, unknown>): Promise<unknown> {
  return request({
    url: "/projects/",
    method: "get",
    params,
  });
}

/**
 * 更新项目申请
 */
export function updateProjectApplication(id: number, data: Record<string, unknown> | FormData): Promise<unknown> {
  return request({
    url: `/projects/application/${id}/update/`,
    method: "put",
    data,
  });
}

/**
 * 撤回项目申报
 */
export function withdrawProjectApplication(id: number): Promise<unknown> {
  return request({
    url: `/projects/application/${id}/withdraw/`,
    method: "post",
  });
}

/**
 * 删除已提交立项申请（进入回收站）
 */
export function deleteProjectApplication(id: number): Promise<unknown> {
  return request({
    url: `/projects/${id}/delete-application/`,
    method: "post",
  });
}

/**
 * 获取我的项目列表
 */
export function getMyProjects(params?: Record<string, unknown>): Promise<unknown> {
  return request({
    url: "/projects/my-projects/",
    method: "get",
    params,
  });
}

/**
 * 获取我的草稿箱
 */
export function getMyDrafts(params?: Record<string, unknown>): Promise<unknown> {
  return request({
    url: "/projects/my-drafts/",
    method: "get",
    params,
  });
}

/**
 * 获取项目详情
 */
export function getProjectDetail(id: number): Promise<unknown> {
  return request({
    url: `/projects/${id}/`,
    method: "get",
  });
}

/**
 * 获取项目成果列表（项目过程）
 */
export function getProjectAchievementList(id: number): Promise<unknown> {
  return request({
    url: `/projects/${id}/achievements/`,
    method: "get",
  });
}

/**
 * 添加项目成果
 */
export function addProjectAchievement(id: number, data: Record<string, unknown> | FormData): Promise<unknown> {
  return request({
    url: `/projects/${id}/add-achievement/`,
    method: "post",
    data,
    headers: {
      "Content-Type": data instanceof FormData ? "multipart/form-data" : "application/json",
    },
  });
}

/**
 * 删除项目成果
 */
export function removeProjectAchievement(projectId: number, achievementId: number): Promise<unknown> {
  return request({
    url: `/projects/${projectId}/remove-achievement/${achievementId}/`,
    method: "delete",
  });
}

/**
 * 删除项目
 */
export function deleteProject(id: number): Promise<unknown> {
  return request({
    url: `/projects/${id}/`,
    method: "delete",
  });
}

// 结题管理相关接口

/**
 * 获取待结题项目列表
 */
export function getPendingClosureProjects(params?: Record<string, unknown>): Promise<unknown> {
  return request({
    url: "/projects/closure/pending/",
    method: "get",
    params,
  });
}

/**
 * 获取已申请结题项目列表
 */
export function getAppliedClosureProjects(params?: Record<string, unknown>): Promise<unknown> {
  return request({
    url: "/projects/closure/applied/",
    method: "get",
    params,
  });
}

/**
 * 获取结题草稿箱
 */
export function getClosureDrafts(params?: Record<string, unknown>): Promise<unknown> {
  return request({
    url: "/projects/closure/drafts/",
    method: "get",
    params,
  });
}

/**
 * 创建结题申请
 */
export function createClosureApplication(id: number, data: Record<string, unknown> | FormData): Promise<unknown> {
  return request({
    url: `/projects/closure/${id}/create/`,
    method: "post",
    data,
  });
}

/**
 * 更新结题申请
 */
export function updateClosureApplication(id: number, data: Record<string, unknown> | FormData): Promise<unknown> {
  return request({
    url: `/projects/closure/${id}/update/`,
    method: "put",
    data,
  });
}

/**
 * 撤销结题申请
 */
export function revokeClosureApplication(id: number): Promise<unknown> {
  return request({
    url: `/projects/${id}/revoke-closure/`,
    method: "post",
  });
}

/**
 * 删除结题草稿
 */
export function deleteClosureDraft(id: number): Promise<unknown> {
  return request({
    url: `/projects/closure/${id}/delete/`,
    method: "delete",
  });
}

/**
 * 删除中期提交（进入回收站）
 */
export function deleteMidTermSubmission(id: number): Promise<unknown> {
  return request({
    url: `/projects/${id}/delete-mid-term/`,
    method: "post",
  });
}

/**
 * 删除结题提交（进入回收站）
 */
export function deleteClosureSubmission(id: number): Promise<unknown> {
  return request({
    url: `/projects/${id}/delete-closure/`,
    method: "post",
  });
}

/**
 * 获取项目成果列表
 */
export function getProjectAchievements(id: number): Promise<unknown> {
  return request({
    url: `/projects/closure/${id}/achievements/`,
    method: "get",
  });
}

/**
 * 获取结题证书（HTML）
 */
export function getProjectCertificate(id: number): Promise<unknown> {
  return request({
    url: `/projects/${id}/certificate/`,
    method: "get",
    responseType: "blob",
  });
}

/**
 * 导出项目申报书 (Word)
 */
export function exportProjectDoc(id: number): Promise<unknown> {
  return request({
    url: `/projects/${id}/export-doc/`,
    method: "get",
    responseType: "blob",
  });
}

/**
 * 获取回收站记录
 */
export function getRecycleBin(params?: Record<string, unknown>): Promise<unknown> {
  return request({
    url: "/projects/recycle-bin/",
    method: "get",
    params,
  });
}

/**
 * 恢复回收站记录
 */
export function restoreRecycleBin(id: number): Promise<unknown> {
  return request({
    url: `/projects/recycle-bin/${id}/restore/`,
    method: "post",
  });
}

/**
 * 获取项目进度
 */
export function getProjectProgress(id: number): Promise<unknown> {
  return request({
    url: `/projects/${id}/progress/`,
    method: "get",
  });
}

/**
 * 添加项目进度
 */
export function addProjectProgress(id: number, data: Record<string, unknown> | FormData): Promise<unknown> {
  return request({
    url: `/projects/${id}/add-progress/`,
    method: "post",
    data,
    headers: {
      "Content-Type": data instanceof FormData ? "multipart/form-data" : "application/json",
    },
  });
}

/**
 * 删除项目进度（进入回收站）
 */
export function removeProjectProgress(projectId: number, progressId: number): Promise<unknown> {
  return request({
    url: `/projects/${projectId}/remove-progress/${progressId}/`,
    method: "delete",
  });
}

/**
 * 删除经费记录（进入回收站）
 */
export function removeProjectExpenditure(id: number): Promise<unknown> {
  return request({
    url: `/projects/expenditures/${id}/`,
    method: "delete",
  });
}

/**
 * 推送项目数据到外部平台
 */
export function pushProjectToExternal(data: { project_ids: number[]; target: string }): Promise<unknown> {
  return request({
    url: `/projects/push-external/`,
    method: "post",
    data,
  });
}
