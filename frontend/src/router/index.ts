import {
  createRouter,
  createWebHistory,
  type RouteRecordRaw,
} from "vue-router";
import { useUserStore } from "@/stores/user";
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
        meta: { title: "通知中心" },
      },
    ],
  },
  {
    path: "/recycle-bin",
    component: () => import("@/layouts/AppLayout.vue"),
    meta: { requiresAuth: true },
    children: [
      {
        path: "",
        name: "recycle-bin",
        component: () => import("@/views/common/RecycleBin.vue"),
        meta: { title: "回收站" },
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

// 路由守卫
router.beforeEach(async (to, _from, next) => {
  const userStore = useUserStore();
  const userRole = localStorage.getItem("user_role"); // 获取用户角色

  if (to.meta.requiresAuth !== false && !userStore.isLoggedIn) {
    // 需要登录但未登录
    next({ name: "login" });
  } else if (to.name === "login" && userStore.isLoggedIn) {
    // 已登录则根据角色信息跳转
    if (userRole === "student") {
      next({ path: "/establishment/apply" });
    } else if (userRole === "level1_admin") {
      next({ path: "/level1-admin/statistics" });
    } else if (userRole === "expert" || userRole === "teacher") {
      // 专家和教师使用相同的页面，因为专家就是被指定为评审的教师
      next({ path: "/teacher/dashboard" });
    } else {
      // 所有其他管理员角色（学院管理员、三级管理员等）都跳转到二级管理页面
      next({ path: "/level2-admin/projects" });
    }
  } else if (userStore.isLoggedIn) {
    // 如果已登录但没有用户信息，尝试获取用户信息
    if (!userStore.user) {
      try {
        await userStore.fetchProfile();
      } catch (error) {
        // 获取用户信息失败（token无效），跳转到登录页
        next({ name: "login" });
        return;
      }
    }

    // 角色权限检查
    const routeRole = to.meta.role as string | undefined;

    // Strict role check
    if (routeRole && routeRole !== userRole) {
      // Allow legacy match for admin/level2_admin if strictness causes issues, but for now strict:
      if (routeRole === "level1_admin" && userRole !== "level1_admin") {
        next({ name: "login" }); // or forbidden page
      } else if (
        (routeRole === "level2_admin" || routeRole === "admin") &&
        userRole !== "level2_admin" &&
        userRole !== "admin"
      ) {
        next({ name: "login" });
      } else if (routeRole === "student" && userRole !== "student") {
        next({ name: "login" });
      } else {
        next();
      }
    } else {
      next();
    }
  } else {
    next();
  }
});

export default router;
