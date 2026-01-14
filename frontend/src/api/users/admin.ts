import request from "@/utils/request";

// 管理员 - 用户管理相关接口

/**
 * 获取用户列表
 */
export function getUsers(params: Record<string, unknown>): Promise<unknown> {
  return request({
    url: "/auth/admin/users/",
    method: "get",
    params,
  });
}

/**
 * 创建用户
 */
export function createUser(data: Record<string, unknown> | FormData): Promise<unknown> {
  return request({
    url: "/auth/admin/users/",
    method: "post",
    data,
  });
}

/**
 * 获取用户详情
 */
export function getUserDetail(id: number): Promise<unknown> {
  return request({
    url: `/auth/admin/users/${id}/`,
    method: "get",
  });
}

/**
 * 更新用户信息
 */
export function updateUser(id: number, data: Record<string, unknown> | FormData): Promise<unknown> {
  return request({
    url: `/auth/admin/users/${id}/`,
    method: "put",
    data,
  });
}

/**
 * 删除用户
 */
export function deleteUser(id: number): Promise<unknown> {
  return request({
    url: `/auth/admin/users/${id}/`,
    method: "delete",
  });
}

/**
 * 启用/禁用用户
 */
export function toggleUserStatus(id: number): Promise<unknown> {
  return request({
    url: `/auth/admin/users/${id}/toggle-status/`,
    method: "post",
  });
}

/**
 * 勾选/取消专家资格
 */
export function toggleExpertStatus(id: number, is_expert: boolean): Promise<unknown> {
  return request({
    url: `/auth/admin/users/${id}/toggle-expert/`,
    method: "post",
    data: { is_expert },
  });
}

/**
 * 重置用户密码
 */
export function resetUserPassword(id: number): Promise<unknown> {
  return request({
    url: `/auth/admin/users/${id}/reset-password/`,
    method: "post",
  });
}

/**
 * 获取用户统计数据
 */
export function getUserStatistics(): Promise<unknown> {
  return request({
    url: "/auth/admin/users/statistics/",
    method: "get",
  });
}

/**
 * 批量导入用户
 */
export function importUsers(data: FormData): Promise<unknown> {
  return request({
    url: "/auth/admin/users/import_data/",
    method: "post",
    data,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  });
}
