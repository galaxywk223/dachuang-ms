import {
  createRouter,
  createWebHistory,
  type RouteRecordRaw,
} from "vue-router";
import { useUserStore } from "@/stores/user";

declare module "vue-router" {
  interface RouteMeta {
    title?: string;
    requiresAuth?: boolean;
    role?: "admin" | "student" | "level1_admin" | "level2_admin";
  }
}

const routes: RouteRecordRaw[] = [
  {
    path: "/login",
    name: "login",
    component: () => import("@/views/Login.vue"),
    meta: { requiresAuth: false },
  },
  // 一级管理员路由 (校级)
  {
    path: "/level1-admin",
    component: () => import("@/layouts/AppLayout.vue"),
    meta: { requiresAuth: true, role: "level1_admin" },
    children: [
      {
        path: "",
        redirect: "/level1-admin/users/students",
      },
      {
        path: "users/students",
        name: "level1-users-students",
        component: () => import("@/views/level1_admin/users/Students.vue"),
        meta: { title: "学生管理" },
      },
      {
        path: "users/admins",
        name: "level1-users-admins",
        component: () => import("@/views/level1_admin/users/Admins.vue"),
        meta: { title: "二级管理员管理" },
      },
      {
        path: "users/teachers",
        name: "level1-users-teachers",
        component: () => import("@/views/level1_admin/users/TeacherManagement.vue"),
        meta: { title: "指导教师管理" },
      },
      {
        path: "data/colleges",
        name: "level1-data-colleges",
        component: () => import("@/views/level1_admin/data/Colleges.vue"),
        meta: { title: "学院信息维护" },
      },
      {
        path: "settings/dictionaries",
        name: "level1-settings-dictionaries",
        component: () => import("@/views/level1_admin/settings/SystemDictionaries.vue"),
        meta: { title: "系统字典管理" },
      },
    ],
  },
  // 二级管理员路由 (院级) - Maintained at /admin for backward compatibility but role updated
  {
    path: "/admin",
    component: () => import("@/layouts/AppLayout.vue"),
    meta: { requiresAuth: true, role: "level2_admin" },
    children: [
      {
        path: "",
        redirect: "/admin/projects",
      },

      {
        path: "review/establishment",
        name: "admin-review-establishment",
        component: () => import("@/views/admin/review/Establishment.vue"),
        meta: { title: "立项审核" },
      },

      {
        path: "review/closure",
        name: "admin-review-closure",
        component: () => import("@/views/admin/review/Closure.vue"),
        meta: { title: "结题审核" },
      },
      {
        path: "review/achievements",
        name: "admin-review-achievements",
        component: () => import("@/views/admin/review/Achievements.vue"),
        meta: { title: "结题成果查看" },
      },
      {
        path: "projects",
        name: "admin-projects",
        component: () => import("@/views/admin/Projects.vue"),
        meta: { title: "项目管理" },
      },

    ],
  },
  // 学生路由
  {
    path: "/",
    component: () => import("@/layouts/AppLayout.vue"),
    meta: { requiresAuth: true, role: "student" },
    children: [
      {
        path: "",
        redirect: "/establishment/apply",
      },
      {
        path: "establishment",
        name: "establishment",
        redirect: "/establishment/apply",
        meta: { title: "立项管理" },
        children: [
          {
            path: "apply",
            name: "establishment-apply",
            component: () => import("@/views/student/establishment/Apply.vue"),
            meta: { title: "申请项目" },
          },
          {
            path: "my-projects",
            name: "establishment-my-projects",
            component: () => import("@/views/student/establishment/MyProjects.vue"),
            meta: { title: "我的项目" },
          },
          {
            path: "drafts",
            name: "establishment-drafts",
            component: () => import("@/views/student/establishment/Drafts.vue"),
            meta: { title: "草稿箱" },
          },
        ],
      },

      {
        path: "closure",
        name: "closure",
        redirect: "/closure/pending",
        meta: { title: "结题管理" },
        children: [
          {
            path: "apply",
            name: "closure-apply",
            component: () => import("@/views/student/closure/Apply.vue"),
            meta: { title: "申请结题" },
          },
          {
            path: "pending",
            name: "closure-pending",
            component: () => import("@/views/student/closure/Pending.vue"),
            meta: { title: "待结题项目" },
          },
          {
            path: "applied",
            name: "closure-applied",
            component: () => import("@/views/student/closure/Applied.vue"),
            meta: { title: "已申请结题项目" },
          },
          {
            path: "drafts",
            name: "closure-drafts",
            component: () => import("@/views/student/closure/Drafts.vue"),
            meta: { title: "草稿箱" },
          },
        ],
      },
      {
        path: "help",
        name: "help",
        component: () => import("@/views/Help.vue"),
        meta: { title: "使用帮助" },
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
router.beforeEach(async (to, _from, next) => {
  const userStore = useUserStore();
  const userRole = localStorage.getItem('user_role'); // 获取用户角色

  if (to.meta.requiresAuth !== false && !userStore.isLoggedIn) {
    // 需要登录但未登录
    next({ name: "login" });
  } else if (to.name === "login" && userStore.isLoggedIn) {
    // 已登录则根据角色跳转
    if (userRole === "student") {
      next({ path: "/establishment/apply" });
    } else if (userRole === "level1_admin") {
      next({ path: "/level1-admin/users/students" });
    } else if (userRole === "level2_admin" || userRole === "admin") {
      next({ path: "/admin/projects" });
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
      if (routeRole === 'level1_admin' && userRole !== 'level1_admin') {
        next({ name: 'login' }); // or forbidden page 
      } else if ((routeRole === 'level2_admin' || routeRole === 'admin') &&
        (userRole !== 'level2_admin' && userRole !== 'admin')) {
        next({ name: 'login' });
      } else if (routeRole === 'student' && userRole !== 'student') {
        next({ name: 'login' });
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
