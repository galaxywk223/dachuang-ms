import type { RouteRecordRaw } from "vue-router";

export const level2Routes: RouteRecordRaw[] = [
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
        component: () => import("@/views/admin/level2/review/Establishment.vue"),
        meta: { title: "立项审核" },
      },
      {
        path: "review/closure",
        name: "admin-review-closure",
        component: () => import("@/views/admin/level2/review/Closure.vue"),
        meta: { title: "结题审核" },
      },
      {
        path: "users/experts",
        name: "level2-users-experts",
        component: () => import("@/views/admin/level2/users/ExpertManagement.vue"),
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
            component: () => import("@/views/admin/shared/expert/Groups.vue"),
            meta: { title: "院系专家组管理" },
          },
          {
            path: "assignment",
            name: "admin-expert-assignment",
            component: () => import("@/views/admin/shared/expert/Assignment.vue"),
            meta: { title: "院系评审分配" },
          },
        ],
      },
      {
        path: "review/midterm",
        name: "admin-review-midterm",
        component: () => import("@/views/admin/level2/review/MidTerm.vue"),
        meta: { title: "中期审核" },
      },
      {
        path: "review/achievements",
        name: "admin-review-achievements",
        component: () => import("@/views/admin/level2/review/Achievements.vue"),
        meta: { title: "结题成果查看" },
      },
      {
        path: "change/review",
        name: "admin-change-review",
        component: () => import("@/views/admin/level2/change/Reviews.vue"),
        meta: { title: "项目异动审核" },
      },
      {
        path: "projects",
        name: "admin-projects",
        component: () => import("@/views/admin/level2/projects/Index.vue"),
        meta: { title: "项目管理" },
      },
      {
        path: "funds",
        name: "level2-funds",
        component: () => import("@/views/admin/shared/Funds.vue"),
        meta: { title: "经费管理" },
      },
      {
        path: "statistics",
        name: "admin-statistics",
        component: () => import("@/views/admin/shared/Statistics.vue"),
        meta: { title: "统计概览" },
      },
    ],
  },
];
