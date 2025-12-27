import type { RouteRecordRaw } from "vue-router";

export const expertRoutes: RouteRecordRaw[] = [
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
];
