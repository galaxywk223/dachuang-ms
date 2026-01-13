import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { login, logout, getProfile } from "@/api/auth";
import { UserRole } from "@/types";
import type { User } from "@/types";

export const useUserStore = defineStore("user", () => {
  const token = ref<string>(localStorage.getItem("token") || "");
  const user = ref<User | null>(null);
  const permissions = ref<string[]>([]);
  const roleInfo = ref<{
    id: number;
    code: string;
    name: string;
    default_route: string;
  } | null>(null);

  const isLoggedIn = computed(() => !!token.value);

  const normalizeUserRole = (data: User | null): User | null => {
    if (!data) return data;
    if (typeof data.role === "string") {
      const normalized = data.role.toLowerCase();
      const roles = Object.values(UserRole);
      if (roles.includes(normalized as UserRole)) {
        const normalizedUser = { ...data, role: normalized as UserRole };
        localStorage.setItem("user_role", normalized);
        return normalizedUser;
      }
    }
    return data;
  };

  // 检查用户是否有某个权限
  const hasPermission = (permission: string): boolean => {
    return permissions.value.includes(permission);
  };

  // 检查用户是否有任意一个权限
  const hasAnyPermission = (permissionList: string[]): boolean => {
    return permissionList.some((p) => permissions.value.includes(p));
  };

  // 检查用户是否有所有权限
  const hasAllPermissions = (permissionList: string[]): boolean => {
    return permissionList.every((p) => permissions.value.includes(p));
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
            };
            permissions?: string[];
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

        // 存储权限列表
        if (userData?.permissions) {
          permissions.value = userData.permissions;
        }

        localStorage.setItem("token", response.data.access_token);
        localStorage.setItem("refresh_token", response.data.refresh_token);
        if (userData?.role_info) {
          localStorage.setItem("role_info", JSON.stringify(userData.role_info));
        }
        if (userData?.permissions) {
          localStorage.setItem(
            "permissions",
            JSON.stringify(userData.permissions)
          );
        }
        if (user.value?.role) {
          localStorage.setItem("user_role", user.value.role);
        }
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
      permissions.value = [];
      roleInfo.value = null;
      localStorage.removeItem("token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("role_info");
      localStorage.removeItem("permissions");
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
          permissions?: string[];
        };
      };
      if (response.code === 200) {
        const userData = response.data ?? null;
        user.value = normalizeUserRole(userData);

        // 更新角色信息
        if (userData?.role_info) {
          roleInfo.value = userData.role_info;
        }

        // 更新权限列表
        if (userData?.permissions) {
          permissions.value = userData.permissions;
        }
        if (user.value?.role) {
          localStorage.setItem("user_role", user.value.role);
        }
      }
    } catch (error) {
      console.error("Fetch profile error:", error);
    }
  }

  return {
    token,
    user,
    permissions,
    roleInfo,
    isLoggedIn,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    loginAction,
    logoutAction,
    fetchProfile,
  };
});
