import axios, {
  AxiosInstance,
  InternalAxiosRequestConfig,
  AxiosResponse,
  AxiosError,
  AxiosRequestConfig,
} from "axios";
import { ElMessage } from "element-plus";
import type { ApiResponse } from "@/types";
import { CONFIG } from "@/config";

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null;

const flattenMessages = (value: unknown): string[] => {
  if (Array.isArray(value)) {
    return value.flat().map((item) => String(item));
  }
  if (value === null || value === undefined) return [];
  return [String(value)];
};

const normalizeMessage = (message: string, isDictionaryRequest: boolean): string => {
  if (!isDictionaryRequest) return message;
  if (message.includes("The fields dict_type, value must make a unique set.")) {
    return "字典类型与代码已存在，不能重复";
  }
  return message
    .replace(/\bdict_type\b/g, "字典类型")
    .replace(/\bvalue\b/g, "代码");
};

const getFieldLabel = (key: string, isDictionaryRequest: boolean): string => {
  const dictionaryOverrides: Record<string, string> = {
    value: "代码",
    label: "显示名称",
  };

  const baseLabels: Record<string, string> = {
    non_field_errors: "",
    dict_type: "字典类型",
    value: "值",
    label: "名称",
    employee_id: "学号/工号",
    real_name: "姓名",
    password: "密码",
    college: "学院",
    major: "专业",
    title: "职称",
    email: "邮箱",
    phone: "手机号",
    role: "角色",
  };

  if (isDictionaryRequest && key in dictionaryOverrides) {
    return dictionaryOverrides[key];
  }
  return baseLabels[key] ?? key;
};

const formatFieldErrors = (
  data: Record<string, unknown>,
  isDictionaryRequest: boolean
): string => {
  const parts: string[] = [];
  for (const [key, value] of Object.entries(data)) {
    const messages = flattenMessages(value).map((msg) =>
      normalizeMessage(msg, isDictionaryRequest)
    );
    if (messages.length === 0) continue;
    if (key === "non_field_errors") {
      parts.push(...messages);
      continue;
    }
    const label = getFieldLabel(key, isDictionaryRequest);
    const prefix = label ? `${label}：` : "";
    parts.push(`${prefix}${messages.join("; ")}`);
  }
  return parts.join("; ");
};

const getResponseHeader = (headers: unknown, key: string): string => {
  if (!isRecord(headers)) return "";
  const get = headers.get;
  if (typeof get === "function") {
    const value = get.call(headers, key);
    return typeof value === "string" ? value : "";
  }
  const value = headers[key] ?? headers[key.toLowerCase()];
  return typeof value === "string" ? value : "";
};

const parseBlobErrorData = async (
  data: unknown,
  headers: unknown
): Promise<unknown> => {
  if (!(data instanceof Blob)) return data;
  const contentType = getResponseHeader(headers, "Content-Type");
  if (
    !data.type.includes("application/json") &&
    !contentType.includes("application/json")
  ) {
    return data;
  }
  try {
    return JSON.parse(await data.text()) as unknown;
  } catch {
    return data;
  }
};

const buildErrorMessage = (
  data: unknown,
  isDictionaryRequest: boolean,
  fallback: string
): string => {
  let msg =
    (isRecord(data) && typeof data.message === "string" && data.message) ||
    fallback;

  // Handle custom error format with 'errors' field
  if (isRecord(data) && data.errors) {
    const errors = data.errors;
    const details = Array.isArray(errors)
      ? errors.flat().join("; ")
      : isRecord(errors)
        ? formatFieldErrors(errors, isDictionaryRequest)
        : "";
    if (details) msg = `${msg}: ${details}`;
  }
  // Handle standard DRF error format (dict of lists)
  else if (isRecord(data) && !("message" in data)) {
    if (typeof data.detail === "string") {
      msg = data.detail;
    }
    const values = Object.values(data);
    const hasArrayErrors = values.some((v) => Array.isArray(v));
    if (hasArrayErrors) {
      const details = formatFieldErrors(data, isDictionaryRequest);
      if (details) msg = details;
    }
  }

  return msg;
};

const request: AxiosInstance = axios.create({
  baseURL: `${CONFIG.api.BASE_URL}/api/${CONFIG.api.API_VERSION}`,
  timeout: CONFIG.api.TIMEOUT,
});

let refreshPromise: Promise<string | null> | null = null;

const clearAuthStorage = () => {
  localStorage.removeItem(CONFIG.app.STORAGE_KEYS.TOKEN);
  localStorage.removeItem(CONFIG.app.STORAGE_KEYS.REFRESH_TOKEN);
  localStorage.removeItem(CONFIG.app.STORAGE_KEYS.ROLE_INFO);
  localStorage.removeItem(CONFIG.app.STORAGE_KEYS.USER_ROLE);
};

const isAuthEndpoint = (url?: string) =>
  typeof url === "string" &&
  (url.includes("/auth/login/") ||
    url.includes("/auth/logout/") ||
    url.includes("/auth/refresh/"));

const refreshAccessToken = async (): Promise<string | null> => {
  const refreshToken = localStorage.getItem(CONFIG.app.STORAGE_KEYS.REFRESH_TOKEN);
  if (!refreshToken) return null;

  if (!refreshPromise) {
    refreshPromise = axios
      .post<ApiResponse<{ access_token: string; refresh_token?: string }>>(
        `${CONFIG.api.BASE_URL}/api/${CONFIG.api.API_VERSION}/auth/refresh/`,
        { refresh_token: refreshToken },
        { timeout: CONFIG.api.TIMEOUT }
      )
      .then((response) => {
        const data = response.data.data;
        if (!data?.access_token) return null;
        localStorage.setItem(CONFIG.app.STORAGE_KEYS.TOKEN, data.access_token);
        if (data.refresh_token) {
          localStorage.setItem(
            CONFIG.app.STORAGE_KEYS.REFRESH_TOKEN,
            data.refresh_token
          );
        }
        return data.access_token;
      })
      .catch(() => null)
      .finally(() => {
        refreshPromise = null;
      });
  }

  return refreshPromise;
};

// 请求拦截器
request.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem(CONFIG.app.STORAGE_KEYS.TOKEN);
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => {
    if (CONFIG.env.DEBUG) {
      console.error("Request error:", error);
    }
    return Promise.reject(error);
  }
);

// 响应拦截器：把 AxiosResponse 统一转换为后端的业务响应结构 { code, message, data }
request.interceptors.response.use(
  ((response: AxiosResponse<ApiResponse<unknown>>) => response.data) as unknown as (
    value: AxiosResponse<ApiResponse<unknown>>
  ) => AxiosResponse<ApiResponse<unknown>>,
  async (error: AxiosError<unknown>) => {
    if (error.response) {
      const configUrl = error.config?.url || "";
      const isDictionaryRequest =
        typeof configUrl === "string" && configUrl.includes("/dictionaries/");
      const responseData = await parseBlobErrorData(
        error.response.data,
        error.response.headers
      );
      error.response.data = responseData;
      switch (error.response.status) {
        case 401: {
          const originalConfig = error.config as
            | (AxiosRequestConfig & { _retry?: boolean })
            | undefined;
          if (
            originalConfig &&
            !originalConfig._retry &&
            !isAuthEndpoint(configUrl)
          ) {
            originalConfig._retry = true;
            const newAccessToken = await refreshAccessToken();
            if (newAccessToken) {
              originalConfig.headers = {
                ...(originalConfig.headers || {}),
                Authorization: `Bearer ${newAccessToken}`,
              };
              return request(originalConfig);
            }
          }

          ElMessage.error("登录已过期，请重新登录");
          clearAuthStorage();

          // 避免引入 router 造成循环依赖：直接跳转到登录页
          if (window.location.pathname !== "/login") {
            window.location.replace("/login");
          }
          break;
        }
        case 403:
          ElMessage.error(
            buildErrorMessage(responseData, isDictionaryRequest, "没有权限访问")
          );
          break;
        case 404:
          ElMessage.error(
            buildErrorMessage(
              responseData,
              isDictionaryRequest,
              "请求的资源不存在"
            )
          );
          break;
        case 500:
          ElMessage.error(
            buildErrorMessage(responseData, isDictionaryRequest, "服务器错误")
          );
          break;
        default: {
          const msg = buildErrorMessage(
            responseData,
            isDictionaryRequest,
            "请求失败"
          );
          ElMessage.error(msg);
        }
      }
    } else {
      ElMessage.error("网络错误，请检查网络连接");
    }
    return Promise.reject(error);
  }
);

export default request;

// 业务泛型封装：让调用端获得严格的 ApiResponse<T> 类型
export function apiRequest<T = unknown>(
  config: AxiosRequestConfig
): Promise<ApiResponse<T>> {
  // 响应拦截器已经把返回值从 AxiosResponse 转成 ApiResponse
  return request(config) as unknown as Promise<ApiResponse<T>>;
}
