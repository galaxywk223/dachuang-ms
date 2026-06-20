import request from "@/utils/request";

export function lookupUsers(params: Record<string, unknown>): Promise<unknown> {
  return request({
    url: "/auth/users/",
    method: "get",
    params,
  });
}
