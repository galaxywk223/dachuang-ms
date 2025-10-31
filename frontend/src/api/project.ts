import request from "@/utils/request";
import type {
  ApiResponse,
  Project,
  PaginatedResponse,
  ProjectForm,
} from "@/types";

/**
 * 获取项目列表
 */
export function getProjects(
  params?: Record<string, any>
): Promise<ApiResponse<PaginatedResponse<Project>>> {
  return request({
    url: "/projects/",
    method: "get",
    params,
  });
}

/**
 * 获取项目详情
 */
export function getProjectDetail(id: number): Promise<ApiResponse<Project>> {
  return request({
    url: `/projects/${id}/`,
    method: "get",
  });
}

/**
 * 创建项目
 */
export function createProject(
  data: ProjectForm
): Promise<ApiResponse<Project>> {
  return request({
    url: "/projects/",
    method: "post",
    data,
  });
}

/**
 * 更新项目
 */
export function updateProject(
  id: number,
  data: Partial<ProjectForm>
): Promise<ApiResponse<Project>> {
  return request({
    url: `/projects/${id}/`,
    method: "put",
    data,
  });
}

/**
 * 删除项目
 */
export function deleteProject(id: number): Promise<ApiResponse<void>> {
  return request({
    url: `/projects/${id}/`,
    method: "delete",
  });
}

/**
 * 提交项目
 */
export function submitProject(id: number): Promise<ApiResponse<Project>> {
  return request({
    url: `/projects/${id}/submit/`,
    method: "post",
  });
}

/**
 * 添加项目成员
 */
export function addProjectMember(
  id: number,
  userId: number
): Promise<ApiResponse<void>> {
  return request({
    url: `/projects/${id}/add_member/`,
    method: "post",
    data: { user_id: userId },
  });
}

/**
 * 移除项目成员
 */
export function removeProjectMember(
  id: number,
  memberId: number
): Promise<ApiResponse<void>> {
  return request({
    url: `/projects/${id}/remove-member/${memberId}/`,
    method: "delete",
  });
}
