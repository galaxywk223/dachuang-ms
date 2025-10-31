import {
  createRouter,
  createWebHistory,
  type RouteRecordRaw,
} from "vue-router";
import { useUserStore } from "@/stores/user";
import type { UserRole } from "@/types";

declare module "vue-router" {
  interface RouteMeta {
    title?: string;
    requiresAuth?: boolean;
    role?: UserRole;
  }
}

const routes: RouteRecordRaw[] = [
  {
    path: "/login",
    name: "login",
    component: () => import("@/views/Login.vue"),
    meta: { requiresAuth: false },
  },
  {
    path: "/",
    component: () => import("@/layouts/MainLayout.vue"),
    meta: { requiresAuth: true },
    children: [
      {
        path: "",
        redirect: "/dashboard",
      },
      {
        path: "dashboard",
        name: "dashboard",
        component: () => import("@/views/Dashboard.vue"),
        meta: { title: "仪表盘" },
      },
      // 学生路由
      {
        path: "student/projects",
        name: "student-projects",
        component: () => import("@/views/student/Projects.vue"),
        meta: { title: "我的项目", role: "student" as UserRole },
      },
      {
        path: "student/project/create",
        name: "student-project-create",
        component: () => import("@/views/student/ProjectForm.vue"),
        meta: { title: "项目申报", role: "student" as UserRole },
      },
      {
        path: "student/project/:id",
        name: "student-project-detail",
        component: () => import("@/views/student/ProjectDetail.vue"),
        meta: { title: "项目详情", role: "student" as UserRole },
      },
      // 二级管理员路由
      {
        path: "admin2/reviews",
        name: "admin2-reviews",
        component: () => import("@/views/admin/Level2Reviews.vue"),
        meta: { title: "申报审核", role: "teacher" as UserRole },
      },
      {
        path: "admin2/projects",
        name: "admin2-projects",
        component: () => import("@/views/admin/Projects.vue"),
        meta: { title: "项目管理", role: "teacher" as UserRole },
      },
      // 一级管理员路由
      {
        path: "admin1/reviews",
        name: "admin1-reviews",
        component: () => import("@/views/admin/Level1Reviews.vue"),
        meta: { title: "申报审核", role: "expert" as UserRole },
      },
      {
        path: "admin1/projects",
        name: "admin1-projects",
        component: () => import("@/views/admin/AllProjects.vue"),
        meta: { title: "所有项目", role: "expert" as UserRole },
      },
      // 通用路由
      {
        path: "notifications",
        name: "notifications",
        component: () => import("@/views/Notifications.vue"),
        meta: { title: "通知中心" },
      },
      {
        path: "profile",
        name: "profile",
        component: () => import("@/views/Profile.vue"),
        meta: { title: "个人信息" },
      },
    ],
  },
  {
    path: "/:pathMatch(.*)*",
    name: "not-found",
    component: () => import("@/views/NotFound.vue"),
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

// 路由守卫
router.beforeEach((to, _from, next) => {
  const userStore = useUserStore();

  if (to.meta.requiresAuth !== false && !userStore.isLoggedIn) {
    // 需要登录但未登录
    next({ name: "login" });
  } else if (to.name === "login" && userStore.isLoggedIn) {
    // 已登录则跳转到首页
    next({ name: "dashboard" });
  } else if (to.meta.role && to.meta.role !== userStore.user?.role) {
    // 角色不匹配
    next({ name: "dashboard" });
  } else {
    next();
  }
});

export default router;
