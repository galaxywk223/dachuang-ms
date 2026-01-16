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
