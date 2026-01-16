import request from "@/utils/request";

// 管理员 - 项目管理相关接口

/**
 * 获取所有项目列表
 */
export function getAllProjects(
  params: Record<string, unknown>
): Promise<unknown> {
  return request({
    url: "/projects/admin/manage/",
    method: "get",
    params,
  });
}

/**
 * 获取项目详情
 */
export function getAdminProjectDetail(id: number): Promise<unknown> {
  return request({
    url: `/projects/admin/manage/${id}/`,
    method: "get",
  });
}

/**
 * 更新项目信息
 */
export function updateProjectInfo(
  id: number,
  data: Record<string, unknown> | FormData
): Promise<unknown> {
  return request({
    url: `/projects/admin/manage/${id}/`,
    method: "patch",
    data,
  });
}

/**
 * 删除项目
 */
export function deleteProjectById(id: number): Promise<unknown> {
  return request({
    url: `/projects/admin/manage/${id}/`,
    method: "delete",
  });
}

/**
 * 获取项目统计数据
 */
export function getProjectStatistics(): Promise<unknown> {
  return request({
    url: "/projects/admin/manage/statistics/",
    method: "get",
  });
}

/**
 * 获取项目统计报表
 */
export function getProjectStatisticsReport(
  params?: Record<string, unknown>
): Promise<unknown> {
  return request({
    url: "/projects/admin/manage/statistics-report/",
    method: "get",
    params,
  });
}

// 成果管理相关接口

/**
 * 获取成果列表
 */
export function getAchievements(
  params: Record<string, unknown>
): Promise<unknown> {
  return request({
    url: "/projects/admin/achievements/",
    method: "get",
    params,
  });
}

/**
 * 导出成果数据
 */
export function exportAchievements(
  params: Record<string, unknown>
): Promise<unknown> {
  return request({
    url: "/projects/admin/achievements/export/",
    method: "get",
    params,
    responseType: "blob",
  });
}

/**
 * 批量导出项目数据
 */
export function exportProjects(
  params?: Record<string, unknown>
): Promise<unknown> {
  return request({
    url: "/projects/admin/manage/export/",
    method: "get",
    params,
    responseType: "blob",
  });
}

/**
 * 批量下载附件
 */
export function batchDownloadAttachments(
  params?: Record<string, unknown>
): Promise<unknown> {
  return request({
    url: "/projects/admin/manage/batch-download/",
    method: "get",
    params,
    responseType: "blob",
  });
}

export function batchUpdateProjectStatus(
  data: Record<string, unknown>
): Promise<unknown> {
  return request({
    url: "/projects/admin/manage/batch-status/",
    method: "post",
    data,
  });
}

export function batchExportDocs(
  params: Record<string, unknown>
): Promise<unknown> {
  return request({
    url: "/projects/admin/manage/batch-export-doc/",
    method: "get",
    params,
    responseType: "blob",
  });
}

export function getCertificatePreview(id: number): Promise<unknown> {
  return request({
    url: `/projects/admin/manage/${id}/certificate-preview/`,
    method: "get",
    responseType: "text",
  });
}

export function batchExportCertificates(
  params: Record<string, unknown>
): Promise<unknown> {
  return request({
    url: "/projects/admin/manage/batch-certificates/",
    method: "get",
    params,
    responseType: "blob",
  });
}

export function batchExportNotices(
  params: Record<string, unknown>
): Promise<unknown> {
  return request({
    url: "/projects/admin/manage/batch-establishment-notice/",
    method: "get",
    params,
    responseType: "blob",
  });
}

export function importHistoryProjects(
  data: Record<string, unknown> | FormData
): Promise<unknown> {
  return request({
    url: "/projects/admin/manage/import-history/",
    method: "post",
    data,
    headers: {
      "Content-Type":
        data instanceof FormData ? "multipart/form-data" : "application/json",
    },
  });
}

export function archiveClosedProjects(): Promise<unknown> {
  return request({
    url: "/projects/admin/manage/archive-closed/",
    method: "post",
  });
}

export function getArchives(): Promise<unknown> {
  return request({
    url: "/projects/admin/manage/archives/",
    method: "get",
  });
}

export function getDuplicateProjectNumbers(): Promise<unknown> {
  return request({
    url: "/projects/admin/manage/duplicate-project-nos/",
    method: "get",
  });
}

export function exportProjectNumbers(
  params?: Record<string, unknown>
): Promise<unknown> {
  return request({
    url: "/projects/admin/manage/export-project-nos/",
    method: "get",
    params,
    responseType: "blob",
  });
}

export function duplicateProjectNumbers(): Promise<unknown> {
  return request({
    url: "/projects/admin/manage/duplicate-project-nos/",
    method: "get",
  });
}
