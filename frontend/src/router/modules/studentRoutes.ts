import type { RouteRecordRaw } from "vue-router";

export const studentRoutes: RouteRecordRaw[] = [
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
        redirect: "/midterm/list",
        meta: { title: "中期检查" },
        children: [
          {
            path: "list",
            name: "midterm-list",
            component: () => import("@/views/student/midterm/List.vue"),
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
];
