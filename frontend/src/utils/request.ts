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

const request: AxiosInstance = axios.create({
  baseURL: `${CONFIG.api.BASE_URL}/api/${CONFIG.api.API_VERSION}`,
  timeout: CONFIG.api.TIMEOUT,
});

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
  (response: AxiosResponse<ApiResponse>) => {
    // 用类型断言把业务数据封装成 Promise 以符合 axios 对返回值的兼容 (可以是 response 或 promise)
    return response.data as unknown as AxiosResponse<ApiResponse>;
  },
  async (error: AxiosError<ApiResponse>) => {
    if (error.response) {
      switch (error.response.status) {
        case 401: {
          ElMessage.error("登录已过期，请重新登录");
          localStorage.removeItem("token");
          localStorage.removeItem("refresh_token");
          // 动态导入 router 以避免循环依赖
          const { default: router } = await import("@/router");
          router.push("/login");
          break;
        }
        case 403:
          ElMessage.error("没有权限访问");
          break;
        case 404:
          ElMessage.error("请求的资源不存在");
          break;
        case 500:
          ElMessage.error("服务器错误");
          break;
        default: {
          const data = error.response.data as any;
          let msg = data?.message || "请求失败";

          // Handle custom error format with 'errors' field
          if (data?.errors) {
            const details = Object.values(data.errors).flat().join('; ');
            if (details) msg = `${msg}: ${details}`;
          }
          // Handle standard DRF error format (dict of lists)
          else if (data && typeof data === 'object' && !data.code && !data.message) {
            const details = Object.values(data).flat().join('; ');
            if (details) msg = details;
          }

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
export function apiRequest<T = any>(
  config: AxiosRequestConfig
): Promise<ApiResponse<T>> {
  // 由于响应拦截器已经把返回值从 AxiosResponse 转成 ApiResponse，这里做类型断言
  return request(config) as unknown as Promise<ApiResponse<T>>;
}
