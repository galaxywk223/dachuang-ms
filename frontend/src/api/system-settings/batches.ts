import request from "@/utils/request";

export function listProjectBatches(params?: Record<string, unknown>): Promise<unknown> {
  return request({
    url: "/system-settings/batches/",
    method: "get",
    params,
  });
}

export function getCurrentBatch(): Promise<unknown> {
  return request({
    url: "/system-settings/batches/current/",
    method: "get",
  });
}

export function createProjectBatch(data: Record<string, unknown>): Promise<unknown> {
  return request({
    url: "/system-settings/batches/",
    method: "post",
    data,
  });
}

export function updateProjectBatch(id: number, data: Record<string, unknown>): Promise<unknown> {
  return request({
    url: `/system-settings/batches/${id}/`,
    method: "patch",
    data,
  });
}

export function deleteProjectBatch(id: number): Promise<unknown> {
  return request({
    url: `/system-settings/batches/${id}/`,
    method: "delete",
  });
}

export function getProjectBatch(id: number): Promise<unknown> {
  return request({
    url: `/system-settings/batches/${id}/`,
    method: "get",
  });
}

export function setCurrentBatch(id: number): Promise<unknown> {
  return request({
    url: `/system-settings/batches/${id}/set-current/`,
    method: "post",
  });
}
export function restoreProjectBatch(id: number): Promise<unknown> {
  return request({
    url: `/system-settings/batches/${id}/restore/`,
    method: "post",
  });
}
