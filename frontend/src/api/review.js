import request from '@/utils/request'

/**
 * 获取审核列表
 */
export function getReviews(params) {
  return request({
    url: '/reviews/',
    method: 'get',
    params
  })
}

/**
 * 获取待审核列表
 */
export function getPendingReviews(params) {
  return request({
    url: '/reviews/pending/',
    method: 'get',
    params
  })
}

/**
 * 审核项目
 */
export function reviewProject(id, action, comments, score) {
  return request({
    url: `/reviews/${id}/review/`,
    method: 'post',
    data: {
      action,
      comments,
      score
    }
  })
}

/**
 * 提交到一级审核
 */
export function submitToLevel1(projectId) {
  return request({
    url: '/reviews/submit-to-level1/',
    method: 'post',
    data: {
      project_id: projectId
    }
  })
}
