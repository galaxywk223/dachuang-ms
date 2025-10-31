import request from "@/utils/request";
import type { ApiResponse, User, LoginResponse } from "@/types";

/**
 * 用户登录
 */
export function login(
  employeeId: string,
  password: string,
  role: string = "student"
): Promise<ApiResponse<LoginResponse>> {
  return request({
    url: "/auth/login/",
    method: "post",
    data: {
      employee_id: employeeId,
      password,
      role,
    },
  });
}

/**
 * 用户登出
 */
export function logout(): Promise<ApiResponse<void>> {
  return request({
    url: "/auth/logout/",
    method: "post",
  });
}

/**
 * 获取用户信息
 */
export function getProfile(): Promise<ApiResponse<User>> {
  return request({
    url: "/auth/profile/",
    method: "get",
  });
}

/**
 * 更新用户信息
 */
export function updateProfile(data: Partial<User>): Promise<ApiResponse<User>> {
  return request({
    url: "/auth/profile/",
    method: "put",
    data,
  });
}

/**
 * 修改密码
 */
export function changePassword(
  oldPassword: string,
  newPassword: string,
  confirmPassword: string
): Promise<ApiResponse<void>> {
  return request({
    url: "/auth/change-password/",
    method: "post",
    data: {
      old_password: oldPassword,
      new_password: newPassword,
      confirm_password: confirmPassword,
    },
  });
}
