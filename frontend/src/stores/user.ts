import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { login, logout, getProfile } from "@/api/auth";
import { UserRole } from "@/types";
import type { User } from "@/types";

export const useUserStore = defineStore("user", () => {
  const token = ref<string>(localStorage.getItem("token") || "");
  const user = ref<User | null>(null);

  const isLoggedIn = computed(() => !!token.value);

  const normalizeUserRole = (data: User | null): User | null => {
    if (!data) return data;
    if (typeof data.role === "string") {
      const normalized = data.role.toLowerCase();
      const roles = Object.values(UserRole);
      return roles.includes(normalized as UserRole)
        ? { ...data, role: normalized as UserRole }
        : data;
    }
    return data;
  };

  async function loginAction(
    employeeId: string,
    password: string,
    role: string = "student"
  ): Promise<boolean> {
    try {
      const response = (await login(employeeId, password, role)) as {
        code?: number;
        data?: {
          access_token: string;
          refresh_token: string;
          user: User;
        };
      };
      if (response.code === 200 && response.data) {
        token.value = response.data.access_token;
        const userData = response.data.user ?? null;
        user.value = normalizeUserRole(userData);
        localStorage.setItem("token", response.data.access_token);
        localStorage.setItem("refresh_token", response.data.refresh_token);
        localStorage.setItem("user_role", role);
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
      localStorage.removeItem("token");
      localStorage.removeItem("refresh_token");
    }
  }

  async function fetchProfile(): Promise<void> {
    try {
      const response = (await getProfile()) as {
        code?: number;
        data?: User;
      };
      if (response.code === 200) {
        const userData = response.data ?? null;
        user.value = normalizeUserRole(userData);
      }
    } catch (error) {
      console.error("Fetch profile error:", error);
    }
  }

  return {
    token,
    user,
    isLoggedIn,
    loginAction,
    logoutAction,
    fetchProfile,
  };
});
