import request from "@/utils/request";

export function getEffectiveSettings(batchId?: number | null): Promise<unknown> {
  return request({
    url: "/system-settings/settings/effective/",
    method: "get",
    params: batchId ? { batch_id: batchId } : undefined,
  });
}

export function updateSettingByCode(
  code: string,
  data: Record<string, unknown>,
  batchId?: number | null
): Promise<unknown> {
  return request({
    url: `/system-settings/settings/by-code/${code}/`,
    method: "put",
    data,
    params: batchId ? { batch_id: batchId } : undefined,
  });
}

export function getCertificateSettings(): Promise<unknown> {
  return request({
    url: "/system-settings/certificates/",
    method: "get",
  });
}

export function createCertificateSetting(data: Record<string, unknown> | FormData): Promise<unknown> {
  return request({
    url: "/system-settings/certificates/",
    method: "post",
    data,
    headers: {
      "Content-Type": data instanceof FormData ? "multipart/form-data" : "application/json",
    },
  });
}

export function updateCertificateSetting(id: number, data: Record<string, unknown> | FormData): Promise<unknown> {
  return request({
    url: `/system-settings/certificates/${id}/`,
    method: "patch",
    data,
    headers: {
      "Content-Type": data instanceof FormData ? "multipart/form-data" : "application/json",
    },
  });
}

export function deleteCertificateSetting(id: number): Promise<unknown> {
  return request({
    url: `/system-settings/certificates/${id}/`,
    method: "delete",
  });
}

export function getWorkflows(params?: Record<string, unknown>): Promise<unknown> {
  return request({
    url: "/system-settings/workflows/",
    method: "get",
    params,
  });
}

export function createWorkflow(data: Record<string, unknown>): Promise<unknown> {
  return request({
    url: "/system-settings/workflows/",
    method: "post",
    data,
  });
}

export function updateWorkflow(id: number, data: Record<string, unknown>): Promise<unknown> {
  return request({
    url: `/system-settings/workflows/${id}/`,
    method: "patch",
    data,
  });
}

export function deleteWorkflow(id: number): Promise<unknown> {
  return request({
    url: `/system-settings/workflows/${id}/`,
    method: "delete",
  });
}

export function getWorkflowNodes(params?: Record<string, unknown>): Promise<unknown> {
  return request({
    url: "/system-settings/workflow-nodes/",
    method: "get",
    params,
  });
}

export function createWorkflowNode(data: Record<string, unknown>): Promise<unknown> {
  return request({
    url: "/system-settings/workflow-nodes/",
    method: "post",
    data,
  });
}

export function updateWorkflowNode(id: number, data: Record<string, unknown>): Promise<unknown> {
  return request({
    url: `/system-settings/workflow-nodes/${id}/`,
    method: "patch",
    data,
  });
}

export function deleteWorkflowNode(id: number): Promise<unknown> {
  return request({
    url: `/system-settings/workflow-nodes/${id}/`,
    method: "delete",
  });
}

export function reorderWorkflowNodes(items: Array<{ id: number; sort_order: number }>): Promise<unknown> {
  return request({
    url: "/system-settings/workflow-nodes/reorder/",
    method: "post",
    data: { items },
  });
}

export function getReviewTemplates(params?: Record<string, unknown>): Promise<unknown> {
  return request({
    url: "/system-settings/review-templates/",
    method: "get",
    params,
  });
}

export function createReviewTemplate(data: Record<string, unknown>): Promise<unknown> {
  return request({
    url: "/system-settings/review-templates/",
    method: "post",
    data,
  });
}

export function updateReviewTemplate(id: number, data: Record<string, unknown>): Promise<unknown> {
  return request({
    url: `/system-settings/review-templates/${id}/`,
    method: "patch",
    data,
  });
}

export function deleteReviewTemplate(id: number): Promise<unknown> {
  return request({
    url: `/system-settings/review-templates/${id}/`,
    method: "delete",
  });
}

export function getReviewTemplateItems(params?: Record<string, unknown>): Promise<unknown> {
  return request({
    url: "/system-settings/review-template-items/",
    method: "get",
    params,
  });
}

export function createReviewTemplateItem(data: Record<string, unknown>): Promise<unknown> {
  return request({
    url: "/system-settings/review-template-items/",
    method: "post",
    data,
  });
}

export function updateReviewTemplateItem(id: number, data: Record<string, unknown>): Promise<unknown> {
  return request({
    url: `/system-settings/review-template-items/${id}/`,
    method: "patch",
    data,
  });
}

export function deleteReviewTemplateItem(id: number): Promise<unknown> {
  return request({
    url: `/system-settings/review-template-items/${id}/`,
    method: "delete",
  });
}

export function reorderReviewTemplateItems(items: Array<{ id: number; sort_order: number }>): Promise<unknown> {
  return request({
    url: "/system-settings/review-template-items/reorder/",
    method: "post",
    data: { items },
  });
}
