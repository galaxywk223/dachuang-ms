import request from "@/utils/request";

export function getProjectExpertSummary(
  projectId: number,
  params?: { review_type?: string; scope?: string; node_id?: number }
) {
  return request({
    url: `/projects/${projectId}/expert-summary`,
    method: "get",
    params,
  });
}

export function finalizeMidterm(
  projectId: number,
  data: { action: "pass" | "return"; reason?: string }
) {
  return request({
    url: `/projects/${projectId}/workflow/finalize-midterm/`,
    method: "post",
    data,
  });
}
