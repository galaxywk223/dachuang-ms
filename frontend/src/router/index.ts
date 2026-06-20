import {
  createRouter,
  createWebHistory,
  type RouteRecordRaw,
} from "vue-router";
import { useUserStore } from "@/stores/user";
import { CONFIG } from "@/config";
import { adminRoutes } from "./modules/adminRoutes";
import { level2Routes } from "./modules/level2Routes";
import { studentRoutes } from "./modules/studentRoutes";
import { teacherRoutes } from "./modules/teacherRoutes";

declare module "vue-router" {
  interface RouteMeta {
    title?: string;
    requiresAuth?: boolean;
    role?:
      | "admin"
      | "student"
      | "level1_admin"
      | "level2_admin"
      | "expert"
      | "teacher";
    category?: string;
  }
}

const routes: RouteRecordRaw[] = [
  {
    path: "/login",
    name: "login",
    component: () => import("@/views/common/Login.vue"),
    meta: { requiresAuth: false },
  },
  {
    path: "/notifications",
    component: () => import("@/layouts/AppLayout.vue"),
    meta: { requiresAuth: true },
    children: [
      {
        path: "",
        name: "notifications",
        component: () => import("@/views/common/Notifications.vue"),
        meta: { title: "消息中心" },
      },
    ],
  },
  ...adminRoutes,
  ...level2Routes,
  ...studentRoutes,
  ...teacherRoutes,
  {
    path: "/:pathMatch(.*)*",
    name: "not-found",
    component: () => import("@/views/common/NotFound.vue"),
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

const resolveDefaultRoute = (
  role: string,
  defaultRoute?: string,
  hasScopeDimension = false
) => {
  if (hasScopeDimension || role === "level2_admin") return "/level2-admin/projects";
  if (role === "student") return "/my-projects";
  if (role === "level1_admin") return "/level1-admin/statistics";
  if (role === "teacher" || role === "expert") return "/teacher/dashboard";
  if (defaultRoute) return defaultRoute;
  return "/notifications";
};

const hasRouteAccess = (
  routeRole: string,
  userRole: string,
  hasScopeDimension: boolean
) => {
  if (!routeRole) return true;
  if (routeRole === "teacher") {
    // 专家与教师使用同一套教师端页面。
    return userRole === "teacher" || userRole === "expert";
  }
  if (routeRole === "level2_admin" || routeRole === "admin") {
    return userRole === "level2_admin" || userRole === "admin" || hasScopeDimension;
  }
  return routeRole === userRole;
};

const getUserRole = (userStore: ReturnType<typeof useUserStore>) =>
  (
    userStore.user?.role ||
    localStorage.getItem(CONFIG.app.STORAGE_KEYS.USER_ROLE) ||
    ""
  ).toLowerCase();

// 路由守卫
router.beforeEach(async (to, _from, next) => {
  const userStore = useUserStore();

  const ensureProfile = async () => {
    if (!userStore.user && userStore.isLoggedIn) {
      try {
        await userStore.fetchProfile();
      } catch {
        await userStore.logoutAction();
        next({ name: "login" });
        return false;
      }
    }
    return true;
  };

  if (to.meta.requiresAuth !== false && !userStore.isLoggedIn) {
    next({ name: "login" });
    return;
  }

  if (to.name === "login" && userStore.isLoggedIn) {
    if (!(await ensureProfile())) return;
    const role = getUserRole(userStore);
    next({
      path: resolveDefaultRoute(
        role,
        userStore.roleInfo?.default_route,
        Boolean(userStore.roleInfo?.scope_dimension)
      ),
    });
    return;
  }

  if (!userStore.isLoggedIn) {
    next();
    return;
  }

  if (!(await ensureProfile())) return;

  const userRole = getUserRole(userStore);
  const routeRole = (to.meta.role as string | undefined) || "";
  const hasScopeDimension = Boolean(userStore.roleInfo?.scope_dimension);

  if (!hasRouteAccess(routeRole, userRole, hasScopeDimension)) {
    next({
      path: resolveDefaultRoute(
        userRole,
        userStore.roleInfo?.default_route,
        hasScopeDimension
      ),
    });
    return;
  }

  next();
});

export default router;
