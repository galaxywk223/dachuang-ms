import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { login, logout, getProfile } from "@/api/auth";
import { UserRole } from "@/types";
import type { User } from "@/types";

export const useUserStore = defineStore("user", () => {
  const token = ref<string>(localStorage.getItem("token") || "");

  // 从 localStorage 恢复角色信息
  const storedRoleInfo = localStorage.getItem("role_info");

  const user = ref<User | null>(null);
  const roleInfo = ref<{
    id: number;
    code: string;
    name: string;
    default_route: string;
    scope_dimension?: string | null;
  } | null>(storedRoleInfo ? JSON.parse(storedRoleInfo) : null);

  const isLoggedIn = computed(() => !!token.value);

  const normalizeUserRole = (data: User | null): User | null => {
    if (!data) return data;
    if (typeof data.role === "string") {
      const normalized = data.role.toLowerCase();
      localStorage.setItem("user_role", normalized);
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
        console.log("[登录调试] 登录响应数据:", response.data);
        token.value = response.data.access_token;
        const userData = response.data.user ?? null;
        console.log("[登录调试] 用户数据:", userData);
        console.log("[登录调试] 角色信息:", userData?.role_info);
        user.value = normalizeUserRole(userData);

        // 存储角色信息
        if (userData?.role_info) {
          roleInfo.value = userData.role_info;
          console.log("[登录调试] 设置 roleInfo:", roleInfo.value);
        }

        localStorage.setItem("token", response.data.access_token);
        localStorage.setItem("refresh_token", response.data.refresh_token);
        if (userData?.role_info) {
          localStorage.setItem("role_info", JSON.stringify(userData.role_info));
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
    try {
      await logout();
    } finally {
      token.value = "";
      user.value = null;
      roleInfo.value = null;
      localStorage.removeItem("token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("role_info");
      localStorage.removeItem("user_role");
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
        }

        if (user.value?.role) {
          localStorage.setItem("user_role", user.value.role);
        }
      }
    } catch (error) {
      console.error("Fetch profile error:", error);
      // 如果获取用户信息失败（如token过期），清理登录状态
      token.value = "";
      user.value = null;
      roleInfo.value = null;
      localStorage.removeItem("token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("role_info");
      localStorage.removeItem("user_role");
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
