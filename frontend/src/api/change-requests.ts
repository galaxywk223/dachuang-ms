import request from "@/utils/request";

export function getChangeRequests(params?: any) {
  return request({
    url: "/projects/change-requests/",
    method: "get",
    params,
  });
}

export function createChangeRequest(data: any) {
  return request({
    url: "/projects/change-requests/",
    method: "post",
    data,
    headers: {
      "Content-Type": data instanceof FormData ? "multipart/form-data" : "application/json",
    },
  });
}

export function updateChangeRequest(id: number, data: any) {
  return request({
    url: `/projects/change-requests/${id}/`,
    method: "patch",
    data,
    headers: {
      "Content-Type": data instanceof FormData ? "multipart/form-data" : "application/json",
    },
  });
}

export function submitChangeRequest(id: number) {
  return request({
    url: `/projects/change-requests/${id}/submit/`,
    method: "post",
  });
}

export function reviewChangeRequest(id: number, data: any) {
  return request({
    url: `/projects/change-requests/${id}/review/`,
    method: "post",
    data,
  });
}
