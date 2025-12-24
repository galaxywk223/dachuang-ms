import request from "@/utils/request";

export function listProjectBatches() {
  return request({
    url: "/system-settings/batches/",
    method: "get",
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

export function setCurrentBatch(id: number) {
  return request({
    url: `/system-settings/batches/${id}/set-current/`,
    method: "post",
  });
}
