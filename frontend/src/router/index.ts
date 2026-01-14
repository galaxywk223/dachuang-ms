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

  console.log("[路由守卫] 导航到:", to.path);
  console.log("[路由守卫] isLoggedIn:", userStore.isLoggedIn);
  console.log("[路由守卫] userRole:", userRole);
  console.log("[路由守卫] roleInfo:", userStore.roleInfo);
  console.log("[路由守卫] user:", userStore.user);

  if (to.meta.requiresAuth !== false && !userStore.isLoggedIn) {
    // 需要登录但未登录
    next({ name: "login" });
  } else if (to.name === "login" && userStore.isLoggedIn) {
    // 已登录则根据角色信息跳转
    console.log("[路由守卫] 已登录，准备跳转");
    console.log(
      "[路由守卫] roleInfo.default_route:",
      userStore.roleInfo?.default_route
    );

    if (userRole === "student") {
      console.log("[路由守卫] 跳转到学生页面");
      next({ path: "/my-projects" });
    } else if (userRole === "level1_admin") {
      console.log("[路由守卫] 跳转到校级管理员页面");
      next({ path: "/level1-admin/statistics" });
    } else if (userRole === "expert" || userRole === "teacher") {
      // 专家和教师使用相同的页面，因为专家就是被指定为评审的教师
      console.log("[路由守卫] 跳转到教师页面");
      next({ path: "/teacher/dashboard" });
    } else {
      // 所有其他管理员角色（学院管理员、三级管理员等）都跳转到二级管理页面
      console.log("[路由守卫] 跳转到管理员页面");
      next({ path: "/level2-admin/statistics" });
    }
  } else if (userStore.isLoggedIn) {
    // 如果已登录但没有用户信息，尝试获取用户信息
    if (!userStore.user) {
      try {
        await userStore.fetchProfile();
      } catch {
        // 获取用户信息失败（token无效），跳转到登录页
        next({ name: "login" });
        return;
      }
    }

    // 角色权限检查
    const routeRole = to.meta.role as string | undefined;

    console.log("[路由守卫] 页面要求的角色:", routeRole, "用户角色:", userRole);

    // Strict role check
    if (routeRole && routeRole !== userRole) {
      // 对于admin和level2_admin页面，允许所有管理员角色访问
      if (routeRole === "level2_admin" || routeRole === "admin") {
        // 检查用户是否是管理员：校级、院级或其他管理员角色
        console.log(
          "[路由守卫] roleInfo完整对象:",
          JSON.stringify(userStore.roleInfo)
        );
        console.log(
          "[路由守卫] scope_dimension值:",
          userStore.roleInfo?.scope_dimension
        );
        const isAdmin =
          userRole === "level1_admin" ||
          userRole === "level2_admin" ||
          userRole === "admin" ||
          userStore.roleInfo?.scope_dimension; // 有scope_dimension就是管理员
        console.log("[路由守卫] isAdmin检查结果:", isAdmin);
        if (isAdmin) {
          console.log("[路由守卫] 管理员角色，允许访问");
          next();
        } else {
          console.log("[路由守卫] 非管理员，拒绝访问");
          next({ name: "login" });
        }
      } else if (routeRole === "level1_admin" && userRole !== "level1_admin") {
        console.log("[路由守卫] 需要校级管理员，拒绝访问");
        next({ name: "login" });
      } else if (routeRole === "student" && userRole !== "student") {
        console.log("[路由守卫] 需要学生，拒绝访问");
        next({ name: "login" });
      } else {
        console.log("[路由守卫] 角色不匹配，但允许通过");
        next();
      }
    } else {
      console.log("[路由守卫] 角色匹配或无需检查，允许通过");
      next();
    }
  } else {
    next();
  }
});

export default router;
