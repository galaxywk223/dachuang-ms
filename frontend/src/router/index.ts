import {
  createRouter,
  createWebHistory,
  type RouteRecordRaw,
} from "vue-router";
import { useUserStore } from "@/stores/user";
import { adminRoutes } from "./modules/adminRoutes";
import { level2Routes } from "./modules/level2Routes";
import { studentRoutes } from "./modules/studentRoutes";

declare module "vue-router" {
  interface RouteMeta {
    title?: string;
    requiresAuth?: boolean;
    role?: "admin" | "student" | "level1_admin" | "level2_admin" | "expert" | "teacher";
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
  ...adminRoutes,
  ...level2Routes,
  ...studentRoutes,
  // 专家路由
  {
    path: "/expert",
    component: () => import("@/layouts/AppLayout.vue"),
    meta: { requiresAuth: true, role: "expert" },
    children: [
      {
        path: "",
        redirect: "/expert/reviews",
      },
      {
        path: "reviews",
        name: "expert-reviews",
        component: () => import("@/views/expert/Reviews.vue"),
        meta: { title: "评审任务" },
      },
    ],
  },
  // 指导教师路由
  {
    path: "/teacher",
    component: () => import("@/layouts/AppLayout.vue"),
    meta: { requiresAuth: true, role: "teacher" },
    children: [
      {
        path: "",
        redirect: "/teacher/dashboard",
      },
      {
        path: "dashboard",
        name: "teacher-dashboard",
        component: () => import("@/views/teacher/Dashboard.vue"),
        meta: { title: "指导项目" },
      },
      {
        path: "change-reviews",
        name: "teacher-change-reviews",
        component: () => import("@/views/teacher/ChangeReviews.vue"),
        meta: { title: "项目异动审核" },
      },
      {
        path: "funds",
        name: "teacher-funds",
        component: () => import("@/views/admin/shared/Funds.vue"),
        meta: { title: "经费管理" },
      },
    ],
  },
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
    // 已登录则根据角色跳转
    if (userRole === "student") {
      next({ path: "/establishment/apply" });
    } else if (userRole === "level1_admin") {
      next({ path: "/level1-admin/statistics" });
    } else if (userRole === "level2_admin" || userRole === "admin") {
      next({ path: "/level2-admin/projects" });
    } else if (userRole === "expert") {
      next({ path: "/expert/reviews" });
    } else if (userRole === "teacher") {
      next({ path: "/teacher/dashboard" });
    } else {
      next({ path: "/establishment/apply" }); // Default fallback
    }
  } else if (userStore.isLoggedIn) {
    // 如果已登录但没有用户信息，尝试获取用户信息
    if (!userStore.user) {
      await userStore.fetchProfile();
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
