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
    role?: "admin" | "student" | "level1_admin" | "level2_admin" | "expert" | "teacher";
    category?: string;
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
        redirect: "/level1-admin/statistics",
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
        meta: { title: "学院管理员管理" },
      },
      {
        path: "users/teachers",
        name: "level1-users-teachers",
        component: () => import("@/views/level1_admin/users/TeacherManagement.vue"),
        meta: { title: "指导教师管理" },
      },
      {
        path: "users/experts",
        name: "level1-users-experts",
        component: () => import("@/views/level1_admin/users/ExpertManagement.vue"),
        meta: { title: "专家库管理" },
      },
      {
        path: "data/colleges",
        name: "level1-data-colleges",
        component: () => import("@/views/level1_admin/data/Colleges.vue"),
        meta: { title: "学院信息维护" },
      },
      {
        path: "expert",
        name: "level1-expert",
        redirect: "/level1-admin/expert/groups",
        meta: { title: "专家管理" },
        children: [
          {
            path: "groups",
            name: "level1-expert-groups",
            component: () => import("@/views/level2_admin/expert/Groups.vue"),
            meta: { title: "校级专家组管理" },
          },
          {
            path: "assignment",
            name: "level1-expert-assignment",
            component: () => import("@/views/level2_admin/expert/Assignment.vue"),
            meta: { title: "校级评审分配" },
          }
        ]
      },
      {
        path: "projects/all",
        name: "level1-projects-all",
        component: () => import("@/views/level1_admin/projects/AllProjects.vue"),
        meta: { title: "项目库管理" },
      },
      {
        path: "funds",
        name: "level1-funds",
        component: () => import("@/views/admin/Funds.vue"),
        meta: { title: "经费管理" },
      },
      {
        path: "statistics",
        name: "level1-statistics",
        component: () => import("@/views/admin/Statistics.vue"),
        meta: { title: "统计概览" },
      },
      {
        path: "review/establishment",
        name: "level1-review-establishment",
        component: () => import("@/views/level1_admin/review/Establishment.vue"),
        meta: { title: "校级立项审核" },
      },
      {
        path: "review/closure",
        name: "level1-review-closure",
        component: () => import("@/views/level1_admin/review/Closure.vue"),
        meta: { title: "校级结题审核" },
      },
      {
        path: "projects/:id",
        name: "level1-project-detail",
        component: () => import("@/views/level1_admin/projects/ProjectDetail.vue"),
        meta: { title: "项目详情" },
      },
      {
        path: "change/review",
        name: "level1-change-review",
        component: () => import("@/views/level1_admin/change/Reviews.vue"),
        meta: { title: "项目异动审核" },
      },
      {
        path: "settings/project-dictionaries",
        name: "level1-settings-project-dictionaries",
        component: () => import("@/views/level1_admin/settings/SystemDictionaries.vue"),
        meta: { title: "项目参数", category: "project" },
      },
      {
        path: "settings/batches",
        name: "level1-settings-batches",
        component: () => import("@/views/level1_admin/settings/Batches.vue"),
        meta: { title: "批次管理" },
      },
      {
        path: "settings/batches/:id",
        name: "level1-settings-batch-config",
        component: () => import("@/views/level1_admin/settings/SystemConfig.vue"),
        meta: { title: "批次配置" },
      },
      {
        path: "settings/system-config",
        name: "level1-settings-system-config",
        redirect: "/level1-admin/settings/batches",
      },
      {
        path: "settings/certificate",
        name: "level1-settings-certificate",
        component: () => import("@/views/level1_admin/settings/CertificateSettings.vue"),
        meta: { title: "结题证书" },
      },
      {
        path: "settings/org-dictionaries",
        name: "level1-settings-org-dictionaries",
        component: () => import("@/views/level1_admin/settings/SystemDictionaries.vue"),
        meta: { title: "组织参数", category: "org" },
      },
      {
        path: "settings/achievement-dictionaries",
        name: "level1-settings-achievement-dictionaries",
        component: () => import("@/views/level1_admin/settings/SystemDictionaries.vue"),
        meta: { title: "成果参数", category: "achievement" },
      },
      {
        path: "settings/other-dictionaries",
        name: "level1-settings-other-dictionaries",
        component: () => import("@/views/level1_admin/settings/SystemDictionaries.vue"),
        meta: { title: "通用参数", category: "other" },
      },
    ],
  },
  // 二级管理员路由 (院级)
  {
    path: "/level2-admin",
    component: () => import("@/layouts/AppLayout.vue"),
    meta: { requiresAuth: true, role: "level2_admin" },
    children: [
      {
        path: "",
        redirect: "/level2-admin/projects",
      },

      {
        path: "review/establishment",
        name: "admin-review-establishment",
        component: () => import("@/views/level2_admin/review/Establishment.vue"),
        meta: { title: "立项审核" },
      },

      {
        path: "review/closure",
        name: "admin-review-closure",
        component: () => import("@/views/level2_admin/review/Closure.vue"),
        meta: { title: "结题审核" },
      },
      {
        path: "users/experts",
        name: "level2-users-experts",
        component: () => import("@/views/level2_admin/users/ExpertManagement.vue"),
        meta: { title: "院级专家库管理" },
      },
      {
        path: "expert",
        name: "admin-expert",
        redirect: "/level2-admin/expert/groups",
        meta: { title: "专家管理" },
        children: [
          {
            path: "groups",
            name: "admin-expert-groups",
            component: () => import("@/views/level2_admin/expert/Groups.vue"),
            meta: { title: "院系专家组管理" },
          },
          {
            path: "assignment",
            name: "admin-expert-assignment",
            component: () => import("@/views/level2_admin/expert/Assignment.vue"),
            meta: { title: "院系评审分配" },
          }
        ]
      },
      {
        path: "review/midterm",
        name: "admin-review-midterm",
        component: () => import("@/views/level2_admin/review/MidTerm.vue"),
        meta: { title: "中期审核" },
      },
      {
        path: "review/achievements",
        name: "admin-review-achievements",
        component: () => import("@/views/level2_admin/review/Achievements.vue"),
        meta: { title: "结题成果查看" },
      },
      {
        path: "change/review",
        name: "admin-change-review",
        component: () => import("@/views/level2_admin/change/Reviews.vue"),
        meta: { title: "项目异动审核" },
      },
      {
        path: "projects",
        name: "admin-projects",
        component: () => import("@/views/level2_admin/Projects.vue"),
        meta: { title: "项目管理" },
      },
      {
        path: "funds",
        name: "level2-funds",
        component: () => import("@/views/admin/Funds.vue"),
        meta: { title: "经费管理" },
      },
      {
        path: "statistics",
        name: "admin-statistics",
        component: () => import("@/views/admin/Statistics.vue"),
        meta: { title: "统计概览" },
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
        path: "midterm",
        name: "midterm",
        redirect: "/midterm/apply",
        meta: { title: "中期检查" },
        children: [
          {
            path: "apply",
            name: "midterm-apply",
            component: () => import("@/views/student/midterm/Apply.vue"),
            meta: { title: "提交报告" },
          },
        ],
      },
      {
        path: "funds",
        name: "student-funds",
        component: () => import("@/views/student/funds/List.vue"),
        meta: { title: "经费管理" },
      },
      {
        path: "achievements",
        name: "student-achievements",
        component: () => import("@/views/student/achievements/Index.vue"),
        meta: { title: "成果管理" },
      },
      {
        path: "change-requests",
        name: "student-change-requests",
        component: () => import("@/views/student/change/Requests.vue"),
        meta: { title: "项目异动" },
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
        component: () => import("@/views/admin/Funds.vue"),
        meta: { title: "经费管理" },
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
