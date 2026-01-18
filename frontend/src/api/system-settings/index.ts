import request from "@/utils/request";

export function getEffectiveSettings(
  batchId?: number | null
): Promise<unknown> {
  return request({
    url: "/system-settings/settings/effective/",
    method: "get",
    params: batchId ? { batch_id: batchId } : undefined,
  });
}

export function updateSettingByCode(
  code: string,
  data: Record<string, unknown>,
  batchId?: number | null
): Promise<unknown> {
  return request({
    url: `/system-settings/settings/by-code/${code}/`,
    method: "put",
    data,
    params: batchId ? { batch_id: batchId } : undefined,
  });
}

export function getCertificateSettings(): Promise<unknown> {
  return request({
    url: "/system-settings/certificates/",
    method: "get",
  });
}

export function createCertificateSetting(
  data: Record<string, unknown> | FormData
): Promise<unknown> {
  return request({
    url: "/system-settings/certificates/",
    method: "post",
    data,
    headers: {
      "Content-Type":
        data instanceof FormData ? "multipart/form-data" : "application/json",
    },
  });
}

export function updateCertificateSetting(
  id: number,
  data: Record<string, unknown> | FormData
): Promise<unknown> {
  return request({
    url: `/system-settings/certificates/${id}/`,
    method: "patch",
    data,
    headers: {
      "Content-Type":
        data instanceof FormData ? "multipart/form-data" : "application/json",
    },
  });
}

export function deleteCertificateSetting(id: number): Promise<unknown> {
  return request({
    url: `/system-settings/certificates/${id}/`,
    method: "delete",
  });
}
