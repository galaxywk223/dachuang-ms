import request from "@/utils/request";

export function getRoles(params?: Record<string, unknown>): Promise<unknown> {
  return request({
    url: "/auth/roles/",
    method: "get",
    params,
  });
}

export function getRoleDetail(id: number): Promise<unknown> {
  return request({
    url: `/auth/roles/${id}/`,
    method: "get",
  });
}

export function createRole(data: Record<string, unknown>): Promise<unknown> {
  return request({
    url: "/auth/roles/",
    method: "post",
    data,
  });
}

export function updateRole(id: number, data: Record<string, unknown>): Promise<unknown> {
  return request({
    url: `/auth/roles/${id}/`,
    method: "put",
    data,
  });
}

export function deleteRole(id: number): Promise<unknown> {
  return request({
    url: `/auth/roles/${id}/`,
    method: "delete",
  });
}

export function toggleRoleStatus(id: number): Promise<unknown> {
  return request({
    url: `/auth/roles/${id}/toggle_status/`,
    method: "post",
  });
}

export function getRoleSimpleList(): Promise<unknown> {
  return request({
    url: "/auth/roles/simple_list/",
    method: "get",
  });
}

export function getPermissions(params?: Record<string, unknown>): Promise<unknown> {
  return request({
    url: "/auth/permissions/",
    method: "get",
    params,
  });
}
