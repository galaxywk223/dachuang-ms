import request from '@/utils/request'

/**
 * 获取项目列表
 */
export function getProjects(params) {
  return request({
    url: '/projects/',
    method: 'get',
    params
  })
}

/**
 * 获取项目详情
 */
export function getProjectDetail(id) {
  return request({
    url: `/projects/${id}/`,
    method: 'get'
  })
}

/**
 * 创建项目
 */
export function createProject(data) {
  return request({
    url: '/projects/',
    method: 'post',
    data
  })
}

/**
 * 更新项目
 */
export function updateProject(id, data) {
  return request({
    url: `/projects/${id}/`,
    method: 'put',
    data
  })
}

/**
 * 删除项目
 */
export function deleteProject(id) {
  return request({
    url: `/projects/${id}/`,
    method: 'delete'
  })
}

/**
 * 提交项目
 */
export function submitProject(id) {
  return request({
    url: `/projects/${id}/submit/`,
    method: 'post'
  })
}

/**
 * 添加项目成员
 */
export function addProjectMember(id, userId) {
  return request({
    url: `/projects/${id}/add_member/`,
    method: 'post',
    data: { user_id: userId }
  })
}

/**
 * 移除项目成员
 */
export function removeProjectMember(id, memberId) {
  return request({
    url: `/projects/${id}/remove-member/${memberId}/`,
    method: 'delete'
  })
}

/**
 * 获取项目进度
 */
export function getProjectProgress(id) {
  return request({
    url: `/projects/${id}/progress/`,
    method: 'get'
  })
}

/**
 * 添加项目进度
 */
export function addProjectProgress(id, data) {
  return request({
    url: `/projects/${id}/add-progress/`,
    method: 'post',
    data
  })
}
