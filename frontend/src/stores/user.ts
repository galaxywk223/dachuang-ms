import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { login, logout, getProfile } from "@/api/auth";
import { UserRole } from "@/types";
import type { User } from "@/types";

export const useUserStore = defineStore("user", () => {
  const token = ref<string>(localStorage.getItem("token") || "");

  // 从localStorage恢复权限和角色信息
  const storedPermissions = localStorage.getItem("permissions");
  const storedRoleInfo = localStorage.getItem("role_info");

  const user = ref<User | null>(null);
  const permissions = ref<string[]>(
    storedPermissions ? JSON.parse(storedPermissions) : []
  );
  const roleInfo = ref<{
    id: number;
    code: string;
    name: string;
    default_route: string;
  } | null>(storedRoleInfo ? JSON.parse(storedRoleInfo) : null);

  const isLoggedIn = computed(() => !!token.value);

  const normalizeUserRole = (data: User | null): User | null => {
    if (!data) return data;
    if (typeof data.role === "string") {
      const normalized = data.role.toLowerCase();
      console.log("[角色标准化] 原始角色:", data.role, "标准化后:", normalized);
      // 总是存储用户角色，不管是否在预定义枚举中
      localStorage.setItem("user_role", normalized);
      console.log("[角色标准化] 存储到localStorage的user_role:", normalized);
      const roles = Object.values(UserRole);
      if (roles.includes(normalized as UserRole)) {
        return { ...data, role: normalized as UserRole };
      }
      // 自定义角色也返回数据
      console.log("[角色标准化] 自定义角色，直接返回");
      return data;
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
      // 如果获取用户信息失败（如token过期），清理登录状态
      token.value = "";
      user.value = null;
      permissions.value = [];
      roleInfo.value = null;
      localStorage.removeItem("token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("role_info");
      localStorage.removeItem("permissions");
      localStorage.removeItem("user_role");
      throw error; // 重新抛出错误，让路由守卫可以处理
    }
  }

  return {
    token,
    user,
    permissions,
    roleInfo,
    isLoggedIn,
    role: computed(() => user.value?.role),
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    loginAction,
    logoutAction,
    fetchProfile,
  };
});
