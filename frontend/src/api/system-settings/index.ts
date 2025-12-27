import request from "@/utils/request";

export function getEffectiveSettings(batchId?: number | null) {
  return request({
    url: "/system-settings/settings/effective/",
    method: "get",
    params: batchId ? { batch_id: batchId } : undefined,
  });
}

export function updateSettingByCode(code: string, data: any, batchId?: number | null) {
  return request({
    url: `/system-settings/settings/by-code/${code}/`,
    method: "put",
    data,
    params: batchId ? { batch_id: batchId } : undefined,
  });
}

export function getCertificateSettings() {
  return request({
    url: "/system-settings/certificates/",
    method: "get",
  });
}

export function createCertificateSetting(data: any) {
  return request({
    url: "/system-settings/certificates/",
    method: "post",
    data,
    headers: {
      "Content-Type": data instanceof FormData ? "multipart/form-data" : "application/json",
    },
  });
}

export function updateCertificateSetting(id: number, data: any) {
  return request({
    url: `/system-settings/certificates/${id}/`,
    method: "patch",
    data,
    headers: {
      "Content-Type": data instanceof FormData ? "multipart/form-data" : "application/json",
    },
  });
}

export function deleteCertificateSetting(id: number) {
  return request({
    url: `/system-settings/certificates/${id}/`,
    method: "delete",
  });
}

export function getWorkflows(params?: any) {
  return request({
    url: "/system-settings/workflows/",
    method: "get",
    params,
  });
}

export function createWorkflow(data: any) {
  return request({
    url: "/system-settings/workflows/",
    method: "post",
    data,
  });
}

export function updateWorkflow(id: number, data: any) {
  return request({
    url: `/system-settings/workflows/${id}/`,
    method: "patch",
    data,
  });
}

export function deleteWorkflow(id: number) {
  return request({
    url: `/system-settings/workflows/${id}/`,
    method: "delete",
  });
}

export function getWorkflowNodes(params?: any) {
  return request({
    url: "/system-settings/workflow-nodes/",
    method: "get",
    params,
  });
}

export function createWorkflowNode(data: any) {
  return request({
    url: "/system-settings/workflow-nodes/",
    method: "post",
    data,
  });
}

export function updateWorkflowNode(id: number, data: any) {
  return request({
    url: `/system-settings/workflow-nodes/${id}/`,
    method: "patch",
    data,
  });
}

export function deleteWorkflowNode(id: number) {
  return request({
    url: `/system-settings/workflow-nodes/${id}/`,
    method: "delete",
  });
}

export function reorderWorkflowNodes(items: Array<{ id: number; sort_order: number }>) {
  return request({
    url: "/system-settings/workflow-nodes/reorder/",
    method: "post",
    data: { items },
  });
}

export function getReviewTemplates(params?: any) {
  return request({
    url: "/system-settings/review-templates/",
    method: "get",
    params,
  });
}

export function createReviewTemplate(data: any) {
  return request({
    url: "/system-settings/review-templates/",
    method: "post",
    data,
  });
}

export function updateReviewTemplate(id: number, data: any) {
  return request({
    url: `/system-settings/review-templates/${id}/`,
    method: "patch",
    data,
  });
}

export function deleteReviewTemplate(id: number) {
  return request({
    url: `/system-settings/review-templates/${id}/`,
    method: "delete",
  });
}

export function getReviewTemplateItems(params?: any) {
  return request({
    url: "/system-settings/review-template-items/",
    method: "get",
    params,
  });
}

export function createReviewTemplateItem(data: any) {
  return request({
    url: "/system-settings/review-template-items/",
    method: "post",
    data,
  });
}

export function updateReviewTemplateItem(id: number, data: any) {
  return request({
    url: `/system-settings/review-template-items/${id}/`,
    method: "patch",
    data,
  });
}

export function deleteReviewTemplateItem(id: number) {
  return request({
    url: `/system-settings/review-template-items/${id}/`,
    method: "delete",
  });
}

export function reorderReviewTemplateItems(items: Array<{ id: number; sort_order: number }>) {
  return request({
    url: "/system-settings/review-template-items/reorder/",
    method: "post",
    data: { items },
  });
}
