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
    role?: "admin" | "student";
  }
}

const routes: RouteRecordRaw[] = [
  {
    path: "/login",
    name: "login",
    component: () => import("@/views/Login.vue"),
    meta: { requiresAuth: false },
  },
  // 管理员路由
  {
    path: "/admin",
    component: () => import("@/layouts/AdminLayout.vue"),
    meta: { requiresAuth: true, role: "admin" },
    children: [
      {
        path: "",
        redirect: "/admin/dashboard",
      },
      {
        path: "dashboard",
        name: "admin-dashboard",
        component: () => import("@/views/admin/Dashboard.vue"),
        meta: { title: "数据统计" },
      },
      {
        path: "review/establishment",
        name: "admin-review-establishment",
        component: () => import("@/views/admin/review/Establishment.vue"),
        meta: { title: "立项审核" },
      },
      {
        path: "review/midterm",
        name: "admin-review-midterm",
        component: () => import("@/views/admin/review/Midterm.vue"),
        meta: { title: "中期审核" },
      },
      {
        path: "review/closure",
        name: "admin-review-closure",
        component: () => import("@/views/admin/review/Closure.vue"),
        meta: { title: "结题审核" },
      },
      {
        path: "projects",
        name: "admin-projects",
        component: () => import("@/views/admin/Projects.vue"),
        meta: { title: "项目管理" },
      },
      {
        path: "users",
        name: "admin-users",
        component: () => import("@/views/admin/Users.vue"),
        meta: { title: "用户管理" },
      },
      {
        path: "settings",
        name: "admin-settings",
        component: () => import("@/views/admin/Settings.vue"),
        meta: { title: "系统设置" },
      },
    ],
  },
  // 学生路由
  {
    path: "/",
    component: () => import("@/layouts/MainLayout.vue"),
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
        path: "midterm",
        name: "midterm",
        redirect: "/midterm/submit",
        meta: { title: "中期管理" },
        children: [
          {
            path: "submit",
            name: "midterm-submit",
            component: () => import("@/views/student/midterm/Submit.vue"),
            meta: { title: "提交中期检查" },
          },
          {
            path: "my-checks",
            name: "midterm-my-checks",
            component: () => import("@/views/student/midterm/MyChecks.vue"),
            meta: { title: "我的中期检查" },
          },
          {
            path: "drafts",
            name: "midterm-drafts",
            component: () => import("@/views/student/midterm/Drafts.vue"),
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
router.beforeEach((to, _from, next) => {
  const userStore = useUserStore();
  const userRole = localStorage.getItem('user_role'); // 获取用户角色

  if (to.meta.requiresAuth !== false && !userStore.isLoggedIn) {
    // 需要登录但未登录
    next({ name: "login" });
  } else if (to.name === "login" && userStore.isLoggedIn) {
    // 已登录则根据角色跳转
    if (userRole === "student") {
      next({ path: "/establishment/apply" });
    } else if (userRole === "admin") {
      next({ path: "/admin/dashboard" });
    } else {
      next({ path: "/establishment/apply" });
    }
  } else if (userStore.isLoggedIn) {
    // 角色权限检查
    const routeRole = to.meta.role as string | undefined;
    
    if (routeRole === "admin" && userRole !== "admin") {
      // 非管理员访问管理员页面
      next({ path: "/establishment/apply" });
    } else if (routeRole === "student" && userRole === "admin") {
      // 管理员访问学生页面
      next({ path: "/admin/dashboard" });
    } else {
      next();
    }
  } else {
    next();
  }
});

export default router;
