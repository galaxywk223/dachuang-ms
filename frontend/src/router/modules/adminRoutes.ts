import type { RouteRecordRaw } from "vue-router";

export const adminRoutes: RouteRecordRaw[] = [
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
        path: "users",
        name: "level1-users",
        component: () => import("@/views/admin/level1/users/UserManagement.vue"),
        meta: { title: "用户管理" },
      },
      {
        path: "roles",
        name: "level1-roles",
        component: () => import("@/views/admin/level1/users/RoleManagement.vue"),
        meta: { title: "角色管理" },
      },
      {
        path: "users/students",
        name: "level1-users-students",
        redirect: { path: "/level1-admin/users", query: { role: "STUDENT" } },
      },
      {
        path: "users/admins",
        name: "level1-users-admins",
        redirect: { path: "/level1-admin/users", query: { role: "LEVEL2_ADMIN" } },
      },
      {
        path: "users/teachers",
        name: "level1-users-teachers",
        redirect: { path: "/level1-admin/users", query: { role: "TEACHER" } },
      },
      {
        path: "users/experts",
        name: "level1-users-experts",
        redirect: { path: "/level1-admin/users", query: { role: "EXPERT" } },
      },
      {
        path: "expert/groups",
        name: "level1-expert-groups",
        component: () => import("@/views/admin/shared/expert/Groups.vue"),
        meta: { title: "校级专家组管理" },
      },
      {
        path: "expert/assignment",
        name: "level1-expert-assignment",
        component: () => import("@/views/admin/shared/expert/Assignment.vue"),
        meta: { title: "校级评审分配" },
      },
      {
        path: "projects/all",
        name: "level1-projects-all",
        component: () => import("@/views/admin/level1/projects/Index.vue"),
        meta: { title: "项目库管理" },
      },
      {
        path: "funds",
        name: "level1-funds",
        component: () => import("@/views/admin/shared/Funds.vue"),
        meta: { title: "经费管理" },
      },
      {
        path: "statistics",
        name: "level1-statistics",
        component: () => import("@/views/admin/shared/Statistics.vue"),
        meta: { title: "统计概览" },
      },
      {
        path: "review",
        name: "level1-review",
        component: () =>
          import("@/views/admin/level1/review/ReviewManagement.vue"),
        meta: { title: "审核管理" },
      },
      {
        path: "projects/:id",
        name: "level1-project-detail",
        component: () => import("@/views/admin/level1/projects/Detail.vue"),
        meta: { title: "项目详情" },
      },
      {
        path: "settings",
        component: () => import("@/layouts/BlankLayout.vue"),
        meta: { title: "系统配置" },
        redirect: "/level1-admin/settings/batches",
        children: [
          {
            path: "batches",
            name: "level1-settings-batches",
            component: () =>
              import("@/views/admin/level1/settings/Batches.vue"),
            meta: { title: "批次管理" },
          },
          {
            path: "batches/:id",
            name: "level1-settings-batch-config",
            component: () =>
              import("@/views/admin/level1/settings/SystemConfig.vue"),
            meta: { title: "批次配置" },
          },
          {
            path: "certificate",
            name: "level1-settings-certificate",
            component: () =>
              import("@/views/admin/level1/settings/CertificateSettings.vue"),
            meta: { title: "结题证书" },
          },
          {
            path: "workflows",
            name: "level1-settings-workflows",
            component: () =>
              import("@/views/admin/level1/settings/WorkflowConfig.vue"),
            meta: { title: "流程配置" },
          },
          {
            path: "review-templates",
            name: "level1-settings-review-templates",
            component: () =>
              import("@/views/admin/level1/settings/ReviewTemplates.vue"),
            meta: { title: "评审模板" },
          },
          {
            path: "dictionaries",
            name: "level1-settings-dictionaries",
            component: () =>
              import("@/views/admin/level1/settings/DictionaryManagement.vue"),
            meta: { title: "字典参数" },
          },
        ],
      },
    ],
  },
];
