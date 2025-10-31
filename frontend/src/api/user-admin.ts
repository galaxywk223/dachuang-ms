import request from "@/utils/request";

// 管理员 - 用户管理相关接口

/**
 * 获取用户列表
 */
export function getUsers(params: any) {
  return request({
    url: "/auth/admin/users/",
    method: "get",
    params,
  });
}

/**
 * 创建用户
 */
export function createUser(data: any) {
  return request({
    url: "/auth/admin/users/",
    method: "post",
    data,
  });
}

/**
 * 获取用户详情
 */
export function getUserDetail(id: number) {
  return request({
    url: `/auth/admin/users/${id}/`,
    method: "get",
  });
}

/**
 * 更新用户信息
 */
export function updateUser(id: number, data: any) {
  return request({
    url: `/auth/admin/users/${id}/`,
    method: "put",
    data,
  });
}

/**
 * 删除用户
 */
export function deleteUser(id: number) {
  return request({
    url: `/auth/admin/users/${id}/`,
    method: "delete",
  });
}

/**
 * 启用/禁用用户
 */
export function toggleUserStatus(id: number) {
  return request({
    url: `/auth/admin/users/${id}/toggle-status/`,
    method: "post",
  });
}

/**
 * 重置用户密码
 */
export function resetUserPassword(id: number) {
  return request({
    url: `/auth/admin/users/${id}/reset-password/`,
    method: "post",
  });
}

/**
 * 获取用户统计数据
 */
export function getUserStatistics() {
  return request({
    url: "/auth/admin/users/statistics/",
    method: "get",
  });
}
