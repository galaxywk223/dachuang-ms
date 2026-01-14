import type { RouteRecordRaw } from "vue-router";

export const teacherRoutes: RouteRecordRaw[] = [
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
        path: "projects/:id",
        name: "teacher-project-detail",
        component: () => import("@/views/admin/level1/projects/Detail.vue"),
        meta: { title: "项目详情" },
      },
    ],
  },
];
