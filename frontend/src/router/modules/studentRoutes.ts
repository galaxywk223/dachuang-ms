import type { RouteRecordRaw } from "vue-router";

export const studentRoutes: RouteRecordRaw[] = [
  {
    path: "/",
    component: () => import("@/layouts/AppLayout.vue"),
    meta: { requiresAuth: true, role: "student" },
    children: [
      {
        path: "",
        redirect: "/my-projects",
      },
      {
        path: "my-projects",
        name: "student-my-projects",
        component: () => import("@/views/student/establishment/MyProjects.vue"),
        meta: { title: "我的项目" },
      },
      {
        path: "funds",
        name: "student-funds-projects",
        component: () => import("@/views/student/funds/Projects.vue"),
        meta: { title: "经费管理" },
      },
      {
        path: "change-requests",
        name: "student-change-projects",
        component: () => import("@/views/student/change/Projects.vue"),
        meta: { title: "异动管理" },
      },
      {
        path: "history-projects",
        name: "student-history-projects",
        component: () => import("@/views/common/HistoryProjects.vue"),
        meta: { title: "历史项目" },
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
        redirect: "/midterm/list",
        meta: { title: "中期检查" },
        children: [
          {
            path: "list",
            name: "midterm-list",
            component: () => import("@/views/student/midterm/Index.vue"),
            meta: { title: "提交报告" },
          },
          {
            path: "apply",
            name: "midterm-apply",
            component: () => import("@/views/student/midterm/Apply.vue"),
            meta: { title: "中期报告" },
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
            meta: { title: "已申请结题" },
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
        path: "project/:projectId/change-requests",
        name: "student-project-change-requests",
        component: () => import("@/views/student/change/Requests.vue"),
        meta: { title: "异动管理" },
      },
      {
        path: "project/:projectId/funds",
        name: "student-project-funds",
        component: () => import("@/views/student/funds/Index.vue"),
        meta: { title: "经费管理" },
      },
    ],
  },
];
