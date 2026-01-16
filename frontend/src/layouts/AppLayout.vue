<template>
  <el-container class="layout-container">
    <!-- Sidebar -->
    <el-aside :width="isCollapse ? '64px' : '260px'" class="app-sidebar">
      <div
        class="logo-area"
        :class="{ collapsed: isCollapse }"
        @click="toggleSidebar"
      >
        <div class="logo-icon">
          <img
            src="@/assets/ahut_logo.jpg"
            alt="Logo"
            style="
              width: 100%;
              height: 100%;
              object-fit: cover;
              border-radius: 50%;
            "
          />
        </div>
        <transition name="fade">
          <span v-show="!isCollapse" class="app-title">{{ appTitle }}</span>
        </transition>
      </div>

      <el-scrollbar>
        <el-menu
          :default-active="activeMenu"
          :collapse="isCollapse"
          :collapse-transition="false"
          unique-opened
          router
          background-color="transparent"
          text-color="#94a3b8"
          active-text-color="#ffffff"
          class="sidebar-menu"
        >
          <!-- Dynamic Menu Generation -->
          <template v-for="item in currentMenus" :key="menuEntryKey(item)">
            <template v-if="isMenuGroup(item)">
              <template v-for="groupItem in item.items" :key="groupItem.index">
                <!-- Submenu -->
                <el-sub-menu v-if="groupItem.children" :index="groupItem.index">
                  <template #title>
                    <el-icon><component :is="groupItem.icon" /></el-icon>
                    <span>{{ groupItem.title }}</span>
                  </template>
                  <el-menu-item
                    v-for="child in groupItem.children"
                    :key="child.index"
                    :index="child.index"
                  >
                    {{ child.title }}
                  </el-menu-item>
                </el-sub-menu>

                <!-- Regular Item -->
                <el-menu-item v-else :index="groupItem.index">
                  <el-icon><component :is="groupItem.icon" /></el-icon>
                  <template #title>{{ groupItem.title }}</template>
                </el-menu-item>
              </template>
            </template>

            <template v-else>
              <!-- Submenu -->
              <el-sub-menu v-if="item.children" :index="item.index">
                <template #title>
                  <el-icon><component :is="item.icon" /></el-icon>
                  <span>{{ item.title }}</span>
                </template>
                <el-menu-item
                  v-for="child in item.children"
                  :key="child.index"
                  :index="child.index"
                >
                  {{ child.title }}
                </el-menu-item>
              </el-sub-menu>

              <!-- Regular Item -->
              <el-menu-item v-else :index="item.index">
                <el-icon><component :is="item.icon" /></el-icon>
                <template #title>{{ item.title }}</template>
              </el-menu-item>
            </template>
          </template>
        </el-menu>
      </el-scrollbar>
    </el-aside>

    <!-- Main Content -->
    <el-container class="main-wrapper">
      <el-header class="app-header">
        <div class="header-left">
          <div class="toggle-btn" @click="toggleSidebar">
            <el-icon :size="20"
              ><Expand v-if="isCollapse" /><Fold v-else
            /></el-icon>
          </div>
          <el-breadcrumb separator="/" class="breadcrumb">
            <el-breadcrumb-item :to="{ path: homePath }"
              >首页</el-breadcrumb-item
            >
            <template v-for="matched in breadcrumbs" :key="matched.path">
              <el-breadcrumb-item
                v-if="matched.meta && matched.meta.title"
                :to="{ path: matched.path }"
              >
                {{ matched.meta.title }}
              </el-breadcrumb-item>
            </template>
          </el-breadcrumb>
          <div class="current-batch">
            <span class="batch-label">当前批次</span>
            <el-tag
              :type="currentBatch ? 'success' : 'info'"
              effect="light"
              size="small"
            >
              {{ currentBatch ? currentBatchLabel : "暂无进行中批次" }}
            </el-tag>
          </div>
        </div>

        <div class="header-right">
          <!-- Notification Bell (Common) -->
          <el-button circle text class="icon-btn" @click="goNotifications">
            <el-badge is-dot class="badge-dot" :hidden="!hasUnread">
              <el-icon :size="20"><Bell /></el-icon>
            </el-badge>
          </el-button>

          <el-dropdown trigger="click" @command="handleCommand">
            <div class="user-profile">
              <el-avatar :size="36" class="avatar-gradient" :class="roleClass">
                {{ userInitials }}
              </el-avatar>
              <span class="username">{{ userName }}</span>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu class="custom-dropdown">
                <el-dropdown-item command="changepw">
                  <el-icon><Lock /></el-icon>修改密码
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="app-main">
        <router-view v-slot="{ Component }">
          <transition name="fade-transform" mode="out-in">
            <component :is="Component" :key="route.fullPath" />
          </transition>
        </router-view>
      </el-main>

      <!-- Password Dialog -->
      <el-dialog
        v-model="passwordDialogVisible"
        title="修改密码"
        width="400px"
        @closed="resetPasswordForm"
        destroy-on-close
      >
        <el-form
          ref="passwordFormRef"
          :model="passwordForm"
          :rules="passwordRules"
          label-width="80px"
          label-position="top"
        >
          <el-form-item label="原密码" prop="oldPassword">
            <el-input
              v-model="passwordForm.oldPassword"
              type="password"
              placeholder="请输入原密码"
              show-password
            />
          </el-form-item>
          <el-form-item label="新密码" prop="newPassword">
            <el-input
              v-model="passwordForm.newPassword"
              type="password"
              placeholder="请输入新密码（至少6位）"
              show-password
            />
          </el-form-item>
          <el-form-item label="确认密码" prop="confirmPassword">
            <el-input
              v-model="passwordForm.confirmPassword"
              type="password"
              placeholder="请再次输入新密码"
              show-password
            />
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="passwordDialogVisible = false">取消</el-button>
            <el-button
              type="primary"
              :loading="passwordLoading"
              @click="handleSubmitPassword"
            >
              确认修改
            </el-button>
          </span>
        </template>
      </el-dialog>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted, watch, type Component } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useUserStore } from "@/stores/user";
import {
  ElMessageBox,
  ElMessage,
  type FormInstance,
  type FormRules,
} from "element-plus";
import {
  DocumentAdd,
  DocumentChecked,
  QuestionFilled,
  Bell,
  ArrowDown,
  SwitchButton,
  Expand,
  Fold,
  Lock,
  Setting,
  Folder,
  User,
} from "@element-plus/icons-vue";
import { getCurrentBatch } from "@/api/system-settings/batches";
import { getUnreadCount } from "@/api/notifications";

type CurrentBatch = {
  name?: string;
  year?: number | string;
  status?: string;
};

type ApiResponse = {
  code?: number;
  message?: string;
  data?: unknown;
};

type MenuItem = {
  index: string;
  title: string;
  icon?: Component;
  children?: MenuItem[];
};

type MenuGroup = {
  groupTitle: string;
  items: MenuItem[];
};

type MenuEntry = MenuItem | MenuGroup;

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null;

const isMenuGroup = (item: MenuEntry): item is MenuGroup => "items" in item;

const menuEntryKey = (item: MenuEntry) =>
  isMenuGroup(item) ? `group-${item.groupTitle}` : item.index;

const getErrorMessage = (error: unknown, fallback: string) => {
  if (!isRecord(error)) return fallback;
  const response = error.response;
  if (
    isRecord(response) &&
    isRecord(response.data) &&
    typeof response.data.message === "string"
  ) {
    return response.data.message;
  }
  if (typeof error.message === "string") return error.message;
  return fallback;
};

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const isCollapse = ref(false);
const hasUnread = ref(false);

// User Info
const userRole = computed(() =>
  String(
    userStore.user?.role || localStorage.getItem("user_role") || "student"
  ).toLowerCase()
);
const isExpertUser = computed(() => Boolean(userStore.user?.is_expert));
const userName = computed(
  () =>
    userStore.user?.real_name ||
    (userRole.value === "student" ? "学生用户" : "管理员")
);
const userInitials = computed(() => userName.value?.[0] || "U");

const currentBatch = ref<CurrentBatch | null>(null);
const currentBatchLabel = computed(() => {
  if (!currentBatch.value) return "";
  const name = currentBatch.value.name || "";
  const year = currentBatch.value.year ? `(${currentBatch.value.year})` : "";
  return `${name}${year}`;
});

// Role-based helper classes
const roleClass = computed(() => {
  switch (userRole.value) {
    case "level1_admin":
      return "role-admin-1";
    case "level2_admin":
      return "role-admin-2";
    default:
      return "role-student";
  }
});

const appTitle = computed(() => {
  switch (userRole.value) {
    case "level1_admin":
      return "系统管理中心";
    case "level2_admin":
      return "大创管理系统";
    default:
      return "大创管理平台";
  }
});

const homePath = computed(() => {
  switch (userRole.value) {
    case "level1_admin":
      return "/level1-admin/statistics";
    case "level2_admin":
      return "/level2-admin/projects";
    case "teacher":
      return "/teacher/dashboard";
    case "expert":
      return "/expert/reviews";
    default:
      return "/";
  }
});

const activeMenu = computed(() => {
  if (route.path === "/teacher/dashboard") {
    const tab = Array.isArray(route.query.tab)
      ? route.query.tab[0]
      : route.query.tab;
    const reviewScope = Array.isArray(route.query.review_scope)
      ? route.query.review_scope[0]
      : route.query.review_scope;
    if (reviewScope === "expert") {
      return "/teacher/dashboard?review_scope=expert&tab=pending";
    }
    return tab === "pending"
      ? "/teacher/dashboard?tab=pending"
      : "/teacher/dashboard?tab=my_projects";
  }
  return route.path;
});
const breadcrumbs = computed(() => {
  return route.matched.filter(
    (item) =>
      item.meta &&
      item.meta.title &&
      item.path !== "/" &&
      item.path !== "/admin" &&
      item.path !== "/level1-admin"
  );
});

const loadCurrentBatch = async () => {
  try {
    const res = (await getCurrentBatch()) as ApiResponse | unknown;
    const data = (isRecord(res) && "data" in res ? res.data : res) as
      | CurrentBatch
      | undefined;
    if (data && data.status === "active") {
      currentBatch.value = data;
      return;
    }
  } catch (error) {
    console.error("加载当前批次失败", error);
  }
  currentBatch.value = null;
};

// Definition of Menus
const currentMenus = computed<MenuEntry[]>(() => {
  switch (userRole.value) {
    case "student":
      return [
        {
          index: "/my-projects",
          title: "我的项目",
          icon: Folder,
        },
        {
          groupTitle: "项目流程",
          items: [
            {
              index: "establishment",
              title: "立项管理",
              icon: DocumentAdd,
              children: [
                { index: "/establishment/apply", title: "申请项目" },
                { index: "/establishment/drafts", title: "草稿箱" },
              ],
            },
            {
              index: "midterm",
              title: "中期检查",
              icon: DocumentChecked,
              children: [
                { index: "/midterm/list", title: "提交报告" },
                { index: "/midterm/drafts", title: "草稿箱" },
              ],
            },
            {
              index: "closure",
              title: "结题管理",
              icon: DocumentChecked,
              children: [
                { index: "/closure/pending", title: "待结题项目" },
                { index: "/closure/applied", title: "已申请结题" },
                { index: "/closure/drafts", title: "草稿箱" },
              ],
            },
          ],
        },
        {
          groupTitle: "消息与支持",
          items: [
            {
              index: "/notifications",
              title: "通知中心",
              icon: Bell,
            },
            {
              index: "/recycle-bin",
              title: "回收站",
              icon: Folder,
            },
            {
              index: "/help",
              title: "使用帮助",
              icon: QuestionFilled,
            },
          ],
        },
      ];
    case "level2_admin":
      return [
        {
          index: "/level2-admin/statistics",
          title: "统计概览",
          icon: Folder,
        },
        {
          index: "/teacher/dashboard?tab=pending",
          title: "我的项目",
          icon: DocumentAdd,
        },
        {
          index: "level2-review",
          title: "审核管理",
          icon: DocumentChecked,
          children: [
            { index: "/level2-admin/review/establishment", title: "立项审核" },
            { index: "/level2-admin/review/midterm", title: "中期审核" },
            { index: "/level2-admin/review/closure", title: "结题审核" },
            { index: "/level2-admin/change/review", title: "异动审核" },
          ],
        },
        {
          index: "/level2-admin/projects",
          title: "项目管理",
          icon: Folder,
        },
        {
          index: "expert",
          title: "专家管理",
          icon: User,
          children: [
            { index: "/level2-admin/users/experts", title: "院级专家库管理" },
            { index: "/level2-admin/expert/groups", title: "院系专家组管理" },
            { index: "/level2-admin/expert/assignment", title: "院系评审分配" },
          ],
        },
        {
          index: "/notifications",
          title: "通知中心",
          icon: Bell,
        },
        {
          index: "/recycle-bin",
          title: "回收站",
          icon: Folder,
        },
      ];
    case "level1_admin":
      return [
        {
          index: "/level1-admin/statistics",
          title: "统计概览",
          icon: Folder,
        },
        {
          index: "/teacher/dashboard?tab=pending",
          title: "我的项目",
          icon: DocumentAdd,
        },
        {
          index: "level1-review",
          title: "审核管理",
          icon: DocumentChecked,
          children: [
            { index: "/level1-admin/review/establishment", title: "立项审核" },
            { index: "/level1-admin/review/closure", title: "结题审核" },
            { index: "/level1-admin/review/change", title: "异动审核" },
          ],
        },
        {
          index: "/level1-admin/projects/all",
          title: "项目管理",
          icon: Folder,
        },
        {
          index: "level1-experts",
          title: "专家与评审",
          icon: User,
          children: [
            { index: "/level1-admin/users/experts", title: "专家库管理" },
            { index: "/level1-admin/expert/groups", title: "校级专家组管理" },
            { index: "/level1-admin/expert/assignment", title: "校级评审分配" },
          ],
        },
        {
          index: "/level1-admin/users",
          title: "用户管理",
          icon: User,
        },
        {
          index: "level1-settings",
          title: "系统配置",
          icon: Setting,
          children: [
            { index: "/level1-admin/settings/batches", title: "批次管理" },
            { index: "/level1-admin/settings/certificate", title: "结题证书" },
            { index: "/level1-admin/settings/dictionaries", title: "系统参数" },
          ],
        },
        {
          index: "/notifications",
          title: "通知中心",
          icon: Bell,
        },
        {
          index: "/recycle-bin",
          title: "回收站",
          icon: Folder,
        },
      ];
    case "teacher":
      return [
        {
          index: "/teacher/dashboard?tab=pending",
          title: "我的项目",
          icon: DocumentAdd,
        },
        ...(isExpertUser.value
          ? [
              {
                index: "/teacher/dashboard?review_scope=expert&tab=pending",
                title: "评审任务",
                icon: DocumentChecked,
              },
            ]
          : []),
        {
          index: "/notifications",
          title: "通知中心",
          icon: Bell,
        },
        {
          index: "/recycle-bin",
          title: "回收站",
          icon: Folder,
        },
      ];
    case "expert":
      return [
        {
          index: "/expert/reviews",
          title: "评审任务",
          icon: DocumentChecked,
        },
        {
          index: "/notifications",
          title: "通知中心",
          icon: Bell,
        },
        {
          index: "/recycle-bin",
          title: "回收站",
          icon: Folder,
        },
      ];
    default:
      return [];
  }
});

const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value;
};

const refreshUnread = async () => {
  try {
    const res = await getUnreadCount();
    const payload = isRecord(res) && "data" in res ? res.data : res;
    const count =
      (isRecord(payload) &&
        isRecord(payload.data) &&
        typeof payload.data.count === "number" &&
        payload.data.count) ||
      (isRecord(payload) &&
        typeof payload.count === "number" &&
        payload.count) ||
      0;
    hasUnread.value = count > 0;
  } catch {
    hasUnread.value = false;
  }
};

const goNotifications = () => {
  router.push("/notifications");
};

const handleCommand = async (command: string) => {
  if (command === "logout") {
    try {
      await ElMessageBox.confirm("确定要退出登录吗？", "提示", {
        type: "warning",
        confirmButtonText: "退出",
        cancelButtonText: "取消",
      });
      await userStore.logoutAction();
      router.push("/login");
    } catch {
      // cancel
    }
  } else if (command === "changepw") {
    passwordDialogVisible.value = true;
  }
};

// Password Change Logic
import { changePassword } from "@/api/auth";

const passwordDialogVisible = ref(false);
const passwordFormRef = ref<FormInstance>();
const passwordLoading = ref(false);

const passwordForm = reactive({
  oldPassword: "",
  newPassword: "",
  confirmPassword: "",
});

const passwordRules: FormRules = {
  oldPassword: [{ required: true, message: "请输入原密码", trigger: "blur" }],
  newPassword: [
    { required: true, message: "请输入新密码", trigger: "blur" },
    { min: 6, message: "密码长度不能少于6位", trigger: "blur" },
  ],
  confirmPassword: [
    { required: true, message: "请确认新密码", trigger: "blur" },
    {
      validator: (
        _rule: unknown,
        value: string,
        callback: (error?: Error) => void
      ) => {
        if (value !== passwordForm.newPassword) {
          callback(new Error("两次输入密码不一致"));
        } else {
          callback();
        }
      },
      trigger: "blur",
    },
  ],
};

const handleSubmitPassword = async () => {
  if (!passwordFormRef.value) return;

  try {
    const valid = await passwordFormRef.value.validate();
    if (!valid) {
      ElMessage.error("请完善必填信息");
      return;
    }
  } catch {
    return;
  }

  passwordLoading.value = true;
  try {
    const res = await changePassword(
      passwordForm.oldPassword,
      passwordForm.newPassword,
      passwordForm.confirmPassword
    );

    if (res.code === 200) {
      ElMessage.success("密码修改成功，请重新登录");
      passwordDialogVisible.value = false;
      await userStore.logoutAction();
      router.push("/login");
    } else {
      ElMessage.error(res.message || "修改失败");
    }
  } catch (error) {
    ElMessage.error(getErrorMessage(error, "请求失败"));
  } finally {
    passwordLoading.value = false;
  }
};

const resetPasswordForm = () => {
  if (passwordFormRef.value) {
    passwordFormRef.value.resetFields();
  }
};

onMounted(async () => {
  await loadCurrentBatch();
  await refreshUnread();
});

watch(
  () => route.path,
  async () => {
    await loadCurrentBatch();
    await refreshUnread();
  }
);
</script>

<style scoped lang="scss" src="./AppLayout.scss"></style>
