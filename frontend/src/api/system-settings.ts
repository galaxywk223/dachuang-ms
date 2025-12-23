import request from "@/utils/request";

export function getEffectiveSettings() {
  return request({
    url: "/system-settings/settings/effective/",
    method: "get",
  });
}

export function updateSettingByCode(code: string, data: any) {
  return request({
    url: `/system-settings/settings/by-code/${code}/`,
    method: "put",
    data,
  });
}

export function getCertificateSettings() {
  return request({
    url: "/system-settings/certificates/",
    method: "get",
  });
}

export function createCertificateSetting(data: any) {
  return request({
    url: "/system-settings/certificates/",
    method: "post",
    data,
    headers: {
      "Content-Type": data instanceof FormData ? "multipart/form-data" : "application/json",
    },
  });
}

export function updateCertificateSetting(id: number, data: any) {
  return request({
    url: `/system-settings/certificates/${id}/`,
    method: "patch",
    data,
    headers: {
      "Content-Type": data instanceof FormData ? "multipart/form-data" : "application/json",
    },
  });
}

export function deleteCertificateSetting(id: number) {
  return request({
    url: `/system-settings/certificates/${id}/`,
    method: "delete",
  });
}
