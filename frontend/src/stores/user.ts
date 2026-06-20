import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { login, logout, getProfile } from "@/api/auth";
import { CONFIG } from "@/config";
import { UserRole } from "@/types";
import type { User } from "@/types";

const STORAGE_KEYS = CONFIG.app.STORAGE_KEYS;

const clearAuthStorage = () => {
  localStorage.removeItem(STORAGE_KEYS.TOKEN);
  localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
  localStorage.removeItem(STORAGE_KEYS.ROLE_INFO);
  localStorage.removeItem(STORAGE_KEYS.USER_ROLE);
};

const readStoredRoleInfo = () => {
  const storedValue = localStorage.getItem(STORAGE_KEYS.ROLE_INFO);
  if (!storedValue) return null;

  try {
    return JSON.parse(storedValue) as {
      id: number;
      code: string;
      name: string;
      default_route: string;
      scope_dimension?: string | null;
    };
  } catch {
    localStorage.removeItem(STORAGE_KEYS.ROLE_INFO);
    return null;
  }
};

export const useUserStore = defineStore("user", () => {
  const token = ref<string>(localStorage.getItem(STORAGE_KEYS.TOKEN) || "");

  const user = ref<User | null>(null);
  const roleInfo = ref<{
    id: number;
    code: string;
    name: string;
    default_route: string;
    scope_dimension?: string | null;
  } | null>(readStoredRoleInfo());

  const isLoggedIn = computed(() => !!token.value);

  const normalizeUserRole = (data: User | null): User | null => {
    if (!data) return data;
    if (typeof data.role === "string") {
      const normalized = data.role.toLowerCase();
      localStorage.setItem(STORAGE_KEYS.USER_ROLE, normalized);
      const roles = Object.values(UserRole);
      if (roles.includes(normalized as UserRole)) {
        return { ...data, role: normalized as UserRole };
      }
      return data;
    }
    return data;
  };

  async function loginAction(
    employeeId: string,
    password: string
  ): Promise<boolean> {
    try {
      const response = (await login(employeeId, password)) as {
        code?: number;
        data?: {
          access_token: string;
          refresh_token: string;
          user: User & {
            role_info?: {
              id: number;
              code: string;
              name: string;
              default_route: string;
              scope_dimension?: string | null;
            };
            default_route?: string;
          };
        };
      };
      if (response.code === 200 && response.data) {
        token.value = response.data.access_token;
        const userData = response.data.user ?? null;
        user.value = normalizeUserRole(userData);

        // 存储角色信息
        if (userData?.role_info) {
          roleInfo.value = userData.role_info;
        }

        localStorage.setItem(STORAGE_KEYS.TOKEN, response.data.access_token);
        localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, response.data.refresh_token);
        if (userData?.role_info) {
          localStorage.setItem(
            STORAGE_KEYS.ROLE_INFO,
            JSON.stringify(userData.role_info)
          );
        } else {
          localStorage.removeItem(STORAGE_KEYS.ROLE_INFO);
        }
        // 不需要再次存储user_role，normalizeUserRole已经处理了
        return true;
      }
      return false;
    } catch (error) {
      console.error("Login error:", error);
      return false;
    }
  }

  async function logoutAction(): Promise<void> {
    const refreshToken = localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
    try {
      await logout(refreshToken);
    } catch (error) {
      console.warn("Logout request failed; clearing local session.", error);
    } finally {
      token.value = "";
      user.value = null;
      roleInfo.value = null;
      clearAuthStorage();
    }
  }

  async function fetchProfile(): Promise<void> {
    try {
      const response = (await getProfile()) as {
        code?: number;
        data?: User & {
          role_info?: {
            id: number;
            code: string;
            name: string;
            default_route: string;
          };
        };
      };
      if (response.code === 200) {
        const userData = response.data ?? null;
        user.value = normalizeUserRole(userData);

        // 更新角色信息
        if (userData?.role_info) {
          roleInfo.value = userData.role_info;
          localStorage.setItem(
            STORAGE_KEYS.ROLE_INFO,
            JSON.stringify(userData.role_info)
          );
        } else {
          roleInfo.value = null;
          localStorage.removeItem(STORAGE_KEYS.ROLE_INFO);
        }

        if (user.value?.role) {
          localStorage.setItem(STORAGE_KEYS.USER_ROLE, user.value.role);
        }
      }
    } catch (error) {
      console.error("Fetch profile error:", error);
      // 如果获取用户信息失败（如token过期），清理登录状态
      token.value = "";
      user.value = null;
      roleInfo.value = null;
      clearAuthStorage();
      throw error;
    }
  }

  return {
    token,
    user,
    roleInfo,
    isLoggedIn,
    role: computed(() => user.value?.role),
    loginAction,
    logoutAction,
    fetchProfile,
  };
});
