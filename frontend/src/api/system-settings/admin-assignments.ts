import request from "@/utils/request";

export interface PhaseScopeConfig {
  id: number;
  batch: number;
  phase: string;
  scope_type: string;
}

export interface AdminAssignment {
  id: number;
  batch: number;
  phase: string;
  workflow_node: number;
  workflow_name?: string;
  scope_value: string;
  admin_user: number;
  admin_user_name?: string;
}

export function getPhaseScopes(params?: Record<string, unknown>) {
  return request<PhaseScopeConfig[]>({
    url: "/system-settings/phase-scopes/",
    method: "get",
    params,
  });
}

export function createPhaseScope(data: Record<string, unknown>) {
  return request<PhaseScopeConfig>({
    url: "/system-settings/phase-scopes/",
    method: "post",
    data,
  });
}

export function updatePhaseScope(id: number, data: Record<string, unknown>) {
  return request<PhaseScopeConfig>({
    url: `/system-settings/phase-scopes/${id}/`,
    method: "patch",
    data,
  });
}

export function getAdminAssignments(params?: Record<string, unknown>) {
  return request<AdminAssignment[]>({
    url: "/system-settings/admin-assignments/",
    method: "get",
    params,
  });
}

export function createAdminAssignment(data: Record<string, unknown>) {
  return request<AdminAssignment>({
    url: "/system-settings/admin-assignments/",
    method: "post",
    data,
  });
}

export function updateAdminAssignment(id: number, data: Record<string, unknown>) {
  return request<AdminAssignment>({
    url: `/system-settings/admin-assignments/${id}/`,
    method: "patch",
    data,
  });
}

export function deleteAdminAssignment(id: number) {
  return request({
    url: `/system-settings/admin-assignments/${id}/`,
    method: "delete",
  });
}
