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
        path: "users/students",
        name: "level1-users-students",
        component: () => import("@/views/admin/level1/users/Students.vue"),
        meta: { title: "学生管理" },
      },
      {
        path: "users/admins",
        name: "level1-users-admins",
        component: () => import("@/views/admin/level1/users/Admins.vue"),
        meta: { title: "学院管理员管理" },
      },
      {
        path: "users/teachers",
        name: "level1-users-teachers",
        component: () => import("@/views/admin/level1/users/TeacherManagement.vue"),
        meta: { title: "指导教师管理" },
      },
      {
        path: "users/experts",
        name: "level1-users-experts",
        component: () => import("@/views/admin/level1/users/ExpertManagement.vue"),
        meta: { title: "专家库管理" },
      },
      {
        path: "data/colleges",
        name: "level1-data-colleges",
        component: () => import("@/views/admin/level1/data/Colleges.vue"),
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
        component: () => import("@/views/admin/shared/expert/Groups.vue"),
            meta: { title: "校级专家组管理" },
          },
          {
            path: "assignment",
            name: "level1-expert-assignment",
        component: () => import("@/views/admin/shared/expert/Assignment.vue"),
            meta: { title: "校级评审分配" },
          },
        ],
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
        path: "review/establishment",
        name: "level1-review-establishment",
        component: () => import("@/views/admin/level1/review/Establishment.vue"),
        meta: { title: "校级立项审核" },
      },
      {
        path: "review/closure",
        name: "level1-review-closure",
        component: () => import("@/views/admin/level1/review/Closure.vue"),
        meta: { title: "校级结题审核" },
      },
      {
        path: "projects/:id",
        name: "level1-project-detail",
        component: () => import("@/views/admin/level1/projects/Detail.vue"),
        meta: { title: "项目详情" },
      },
      {
        path: "change/review",
        name: "level1-change-review",
        component: () => import("@/views/admin/level1/change/Reviews.vue"),
        meta: { title: "项目异动审核" },
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
            component: () => import("@/views/admin/level1/settings/Batches.vue"),
            meta: { title: "批次管理" },
          },
          {
            path: "batches/:id",
            name: "level1-settings-batch-config",
            component: () => import("@/views/admin/level1/settings/SystemConfig.vue"),
            meta: { title: "批次配置" },
          },
          {
            path: "certificate",
            name: "level1-settings-certificate",
            component: () => import("@/views/admin/level1/settings/CertificateSettings.vue"),
            meta: { title: "结题证书" },
          },
          {
            path: "project-dictionaries",
            name: "level1-settings-project-dictionaries",
            component: () => import("@/views/admin/level1/settings/SystemDictionaries.vue"),
            meta: { title: "项目参数", category: "project" },
          },
          {
            path: "org-dictionaries",
            name: "level1-settings-org-dictionaries",
            component: () => import("@/views/admin/level1/settings/SystemDictionaries.vue"),
            meta: { title: "组织参数", category: "org" },
          },
          {
            path: "achievement-dictionaries",
            name: "level1-settings-achievement-dictionaries",
            component: () => import("@/views/admin/level1/settings/SystemDictionaries.vue"),
            meta: { title: "成果参数", category: "achievement" },
          },
          {
            path: "other-dictionaries",
            name: "level1-settings-other-dictionaries",
            component: () => import("@/views/admin/level1/settings/SystemDictionaries.vue"),
            meta: { title: "通用参数", category: "other" },
          },
        ],
      },
    ],
  },
];
