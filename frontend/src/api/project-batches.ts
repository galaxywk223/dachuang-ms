import request from "@/utils/request";

export function listProjectBatches(params?: Record<string, any>) {
  return request({
    url: "/system-settings/batches/",
    method: "get",
    params,
  });
}

export function getCurrentBatch() {
  return request({
    url: "/system-settings/batches/current/",
    method: "get",
  });
}

export function createProjectBatch(data: any) {
  return request({
    url: "/system-settings/batches/",
    method: "post",
    data,
  });
}

export function updateProjectBatch(id: number, data: any) {
  return request({
    url: `/system-settings/batches/${id}/`,
    method: "patch",
    data,
  });
}

export function getProjectBatch(id: number) {
  return request({
    url: `/system-settings/batches/${id}/`,
    method: "get",
  });
}

export function setCurrentBatch(id: number) {
  return request({
    url: `/system-settings/batches/${id}/set-current/`,
    method: "post",
  });
}
export function restoreProjectBatch(id: number) {
  return request({
    url: `/system-settings/batches/${id}/restore/`,
    method: "post",
  });
}
