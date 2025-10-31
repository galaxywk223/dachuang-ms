import request from '@/utils/request'

/**
 * 用户登录
 */
export function login(employeeId, password) {
  return request({
    url: '/auth/login/',
    method: 'post',
    data: {
      employee_id: employeeId,
      password
    }
  })
}

/**
 * 用户登出
 */
export function logout() {
  return request({
    url: '/auth/logout/',
    method: 'post'
  })
}

/**
 * 获取用户信息
 */
export function getProfile() {
  return request({
    url: '/auth/profile/',
    method: 'get'
  })
}

/**
 * 更新用户信息
 */
export function updateProfile(data) {
  return request({
    url: '/auth/profile/',
    method: 'put',
    data
  })
}

/**
 * 修改密码
 */
export function changePassword(oldPassword, newPassword, confirmPassword) {
  return request({
    url: '/auth/change-password/',
    method: 'post',
    data: {
      old_password: oldPassword,
      new_password: newPassword,
      confirm_password: confirmPassword
    }
  })
}
