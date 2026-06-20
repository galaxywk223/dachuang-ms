// ====================================
// 应用配置文件（精简版）
// ====================================

// 环境配置
interface EnvConfig {
  API_BASE_URL: string;
  DEBUG: boolean;
}

const ENV_CONFIGS: Record<string, EnvConfig> = {
  development: {
    API_BASE_URL: "http://localhost:8000",
    DEBUG: true,
  },
  production: {
    API_BASE_URL: "",
    DEBUG: false,
  },
};

// 获取当前环境配置
export const getCurrentConfig = (): EnvConfig => {
  const env = import.meta.env.MODE || "development";
  return ENV_CONFIGS[env] || ENV_CONFIGS.development;
};

const normalizeApiBaseUrl = (rawValue: string | undefined, envConfig: EnvConfig) => {
  const value = (rawValue || envConfig.API_BASE_URL).trim().replace(/\/+$/, "");

  if (!envConfig.DEBUG && value) {
    if (/^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/i.test(value)) {
      throw new Error("VITE_API_BASE_URL must not point to a local backend in production.");
    }
    if (value === "https://api.dachuang.com") {
      throw new Error("VITE_API_BASE_URL must be changed from the placeholder production host.");
    }
  }

  return value;
};

const CURRENT_ENV_CONFIG = getCurrentConfig();

// API 配置
export const API_CONFIG = {
  BASE_URL: normalizeApiBaseUrl(
    import.meta.env.VITE_API_BASE_URL,
    CURRENT_ENV_CONFIG
  ),
  API_VERSION: "v1",
  TIMEOUT: 10000,
};

// 应用配置（只保留实际使用的）
export const APP_CONFIG = {
  APP_NAME: "大创项目管理平台",
  STORAGE_KEYS: {
    TOKEN: "token",
    REFRESH_TOKEN: "refresh_token",
    ROLE_INFO: "role_info",
    USER_ROLE: "user_role",
  },
};

// 统一配置对象
export const CONFIG = {
  api: API_CONFIG,
  app: APP_CONFIG,
  env: CURRENT_ENV_CONFIG,
};
