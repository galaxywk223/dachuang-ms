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
    API_BASE_URL: "https://api.dachuang.com",
    DEBUG: false,
  },
};

// 获取当前环境配置
export const getCurrentConfig = (): EnvConfig => {
  const env = import.meta.env.MODE || "development";
  return ENV_CONFIGS[env] || ENV_CONFIGS.development;
};

// API 配置
export const API_CONFIG = {
  BASE_URL:
    import.meta.env.VITE_API_BASE_URL || getCurrentConfig().API_BASE_URL,
  API_VERSION: "v1",
  TIMEOUT: 10000,
};

// 应用配置（只保留实际使用的）
export const APP_CONFIG = {
  APP_NAME: "大创项目管理平台",
  APP_VERSION: "1.0.0",
  STORAGE_KEYS: {
    TOKEN: "token",
    REFRESH_TOKEN: "refresh_token",
    USER_ROLE: "user_role",
  },
};

// 统一配置对象
export const CONFIG = {
  api: API_CONFIG,
  app: APP_CONFIG,
  env: getCurrentConfig(),
};
