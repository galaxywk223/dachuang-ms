<template>
  <el-container class="admin-layout">
    <!-- 侧边栏 -->
    <el-aside width="240px" class="sidebar">
      <div class="logo">
        <div class="logo-icon"></div>
        <h2>大创管理系统</h2>
      </div>

      <el-menu
        :default-active="activeMenu"
        class="sidebar-menu"
        router
        :unique-opened="true"
        background-color="transparent"
        text-color="#94a3b8"
        active-text-color="#ffffff"
      >
        <el-menu-item index="/admin/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据统计</span>
        </el-menu-item>

        <el-sub-menu index="project-review">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>项目审核</span>
          </template>
          <el-menu-item index="/admin/review/establishment"
            >立项审核</el-menu-item
          >
          <el-menu-item index="/admin/review/midterm">中期审核</el-menu-item>
          <el-menu-item index="/admin/review/closure">结题审核</el-menu-item>
        </el-sub-menu>

        <el-menu-item index="/admin/projects">
          <el-icon><Files /></el-icon>
          <span>项目管理</span>
        </el-menu-item>

        <el-menu-item index="/admin/users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>

        <el-menu-item index="/admin/settings">
          <el-icon><Setting /></el-icon>
          <span>系统设置</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- 右侧主体 -->
    <el-container class="main-container">
      <el-header class="header text-ellipsis">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/admin/dashboard' }"
              >首页</el-breadcrumb-item
            >
            <el-breadcrumb-item>{{ currentPageTitle }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand" trigger="click">
            <div class="user-info">
              <span class="username">{{ userName }}</span>
              <el-avatar :size="36" class="user-avatar"
                >{{ userName.charAt(0) }}
              </el-avatar>
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu class="user-dropdown">
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>个人信息
                </el-dropdown-item>
                <el-dropdown-item divided command="logout">
                  <el-icon><SwitchButton /></el-icon>退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade-transform" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useUserStore } from "@/stores/user";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  DataAnalysis,
  Document,
  Files,
  User,
  Setting,
  ArrowDown,
  SwitchButton,
} from "@element-plus/icons-vue";

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const activeMenu = computed(() => route.path);
const currentPageTitle = computed(() => route.meta.title || "控制台");
const userName = computed(
  () => userStore.user?.real_name || userStore.user?.username || "管理员"
);

const handleCommand = async (command: string) => {
  if (command === "logout") {
    try {
      await ElMessageBox.confirm("确定要退出登录吗？", "提示", {
        confirmButtonText: "确定",
        cancelButtonText: "取消",
        type: "warning",
      });

      await userStore.logoutAction();
      ElMessage.success("已退出登录");
      router.push("/login");
    } catch {
      // 用户取消
    }
  } else if (command === "profile") {
    ElMessage.info("个人信息功能开发中");
  }
};
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.admin-layout {
  height: 100vh;
  background-color: $background-base;
}

.sidebar {
  background-color: $background-dark; // Slate 900
  color: #fff;
  transition: width 0.3s;
  display: flex;
  flex-direction: column;
  z-index: $z-index-sticky;
  box-shadow: $box-shadow-md;

  .logo {
    height: 64px;
    display: flex;
    align-items: center;
    padding: 0 20px;
    background-color: rgba(255, 255, 255, 0.03);
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);

    .logo-icon {
      width: 32px;
      height: 32px;
      background: linear-gradient(135deg, $primary-color, $primary-light);
      border-radius: 8px;
      margin-right: 12px;
    }

    h2 {
      margin: 0;
      font-size: 18px;
      font-weight: 600;
      letter-spacing: 0.5px;
      color: #fff;
    }
  }

  .sidebar-menu {
    border: none;
    flex: 1;
    padding: 12px 0;

    :deep(.el-menu-item),
    :deep(.el-sub-menu__title) {
      height: 50px;
      line-height: 50px;
      margin: 4px 12px;
      border-radius: 8px;
      padding-left: 16px !important;

      &:hover {
        background-color: rgba(255, 255, 255, 0.08);
        color: #fff;
      }

      &.is-active {
        background: linear-gradient(
          90deg,
          rgba($primary-color, 0.9),
          rgba($primary-color, 0.7)
        );
        color: #fff;
        font-weight: 500;
        box-shadow: 0 4px 12px rgba($primary-color, 0.3);
      }

      .el-icon {
        margin-right: 10px;
        font-size: 18px;
      }
    }

    :deep(.el-sub-menu) {
      .el-menu-item {
        padding-left: 48px !important;
        background-color: transparent;

        &.is-active {
          background: rgba(255, 255, 255, 0.08);
          box-shadow: none;
          color: $primary-light;
        }
      }
    }
  }
}

.main-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.header {
  height: 64px;
  background-color: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid $border-light;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 32px;
  box-shadow: $box-shadow-sm;
  z-index: 10;

  .header-left {
    display: flex;
    align-items: center;

    :deep(.el-breadcrumb__inner) {
      font-weight: normal;
      color: $text-secondary;

      &.is-link:hover {
        color: $primary-color;
      }
    }

    :deep(.el-breadcrumb__item:last-child .el-breadcrumb__inner) {
      color: $text-primary;
      font-weight: 500;
    }
  }

  .header-right {
    .user-info {
      display: flex;
      align-items: center;
      gap: 12px;
      cursor: pointer;
      padding: 6px 10px;
      border-radius: 8px;
      transition: background 0.2s;

      &:hover {
        background: $background-base;
      }

      .username {
        font-size: 14px;
        font-weight: 500;
        color: $text-primary;
      }

      .user-avatar {
        background-color: $primary-light;
        color: #fff;
        font-weight: 600;
        border: 2px solid #fff;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
      }

      .el-icon--right {
        color: $text-secondary;
        font-size: 12px;
      }
    }
  }
}

.main-content {
  flex: 1;
  padding: 24px 32px;
  overflow-y: auto;
  overflow-x: hidden;
  position: relative;
}

// 页面切换动画
.fade-transform-enter-active,
.fade-transform-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.fade-transform-enter-from {
  opacity: 0;
  transform: translateX(-15px);
}

.fade-transform-leave-to {
  opacity: 0;
  transform: translateX(15px);
}
</style>
