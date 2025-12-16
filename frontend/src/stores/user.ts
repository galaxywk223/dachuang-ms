import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { login, logout, getProfile } from "@/api/auth";
import type { User } from "@/types";

export const useUserStore = defineStore("user", () => {
  const token = ref<string>(localStorage.getItem("token") || "");
  const user = ref<User | null>(null);

  const isLoggedIn = computed(() => !!token.value);

  async function loginAction(
    employeeId: string,
    password: string,
    role: string = "student"
  ): Promise<boolean> {
    try {
      const response = await login(employeeId, password, role);
      if (response.code === 200) {
        token.value = response.data.access_token;
        const userData = response.data.user;
        if (userData?.role) (userData as any).role = userData.role.toLowerCase();
        user.value = userData;
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
      const response = await getProfile();
      if (response.code === 200) {
        const userData = response.data;
        if (userData?.role) (userData as any).role = userData.role.toLowerCase();
        user.value = userData;
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
