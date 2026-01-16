import request from "@/utils/request";

/**
 * 获取角色简化列表（用于下拉选择等场景）
 */
export function getRoleSimpleList(): Promise<unknown> {
  return request({
    url: "/auth/roles/simple/",
    method: "get",
  });
}

/**
 * 获取所有角色（包含用户数等统计信息）
 */
export function getRoles(params?: Record<string, unknown>): Promise<unknown> {
  return request({
    url: "/auth/roles/",
    method: "get",
    params,
  });
}

/**
 * 获取角色详情
 */
export function getRoleDetail(id: number): Promise<unknown> {
  return request({
    url: `/auth/roles/${id}/`,
    method: "get",
  });
}

/**
 * 创建角色
 */
export function createRole(data: Record<string, unknown>): Promise<unknown> {
  return request({
    url: "/auth/roles/",
    method: "post",
    data,
  });
}

/**
 * 更新角色
 */
export function updateRole(
  id: number,
  data: Record<string, unknown>
): Promise<unknown> {
  return request({
    url: `/auth/roles/${id}/`,
    method: "put",
    data,
  });
}

/**
 * 删除角色
 */
export function deleteRole(id: number): Promise<unknown> {
  return request({
    url: `/auth/roles/${id}/`,
    method: "delete",
  });
}

/**
 * 切换角色状态
 */
export function toggleRoleStatus(id: number): Promise<unknown> {
  return request({
    url: `/auth/roles/${id}/toggle-status/`,
    method: "post",
  });
}
