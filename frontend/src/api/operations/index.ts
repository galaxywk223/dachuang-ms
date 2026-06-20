import request from "@/utils/request";

export function getTaskList(params?: Record<string, unknown>): Promise<unknown> {
  return request({
    url: "/operations/tasks/",
    method: "get",
    params,
  });
}

export function getOperationLogs(params?: Record<string, unknown>): Promise<unknown> {
  return request({
    url: "/operations/logs/",
    method: "get",
    params,
  });
}

export function downloadTaskResult(id: number): Promise<unknown> {
  return request({
    url: `/operations/tasks/${id}/download/`,
    method: "get",
    responseType: "blob",
  });
}

export function getImportKinds(): Promise<unknown> {
  return request({
    url: "/operations/tasks/data-center/kinds/",
    method: "get",
  });
}

export function downloadImportTemplate(kind: string): Promise<unknown> {
  return request({
    url: "/operations/tasks/data-center/template/",
    method: "get",
    params: { kind },
    responseType: "blob",
  });
}

export function previewImport(data: FormData): Promise<unknown> {
  return request({
    url: "/operations/tasks/data-center/preview/",
    method: "post",
    data,
    headers: { "Content-Type": "multipart/form-data" },
  });
}

export function executeImport(data: FormData): Promise<unknown> {
  return request({
    url: "/operations/tasks/data-center/import/",
    method: "post",
    data,
    headers: { "Content-Type": "multipart/form-data" },
  });
}
