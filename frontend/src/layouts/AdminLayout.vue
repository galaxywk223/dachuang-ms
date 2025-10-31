<template>
  <el-container class="admin-layout">
    <el-aside width="250px" class="sidebar">
      <div class="logo">
        <h2>管理员系统</h2>
      </div>

      <el-menu
        :default-active="activeMenu"
        class="sidebar-menu"
        router
        :unique-opened="true"
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

    <el-container>
      <el-header class="header">
        <div class="header-left">
          <span class="page-title">{{ currentPageTitle }}</span>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <div class="user-info">
              <el-avatar :size="32">{{ userName }}</el-avatar>
              <span class="username">{{ userName }}</span>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                <el-dropdown-item command="logout" divided
                  >退出登录</el-dropdown-item
                >
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main-content">
        <router-view />
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
} from "@element-plus/icons-vue";

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const activeMenu = computed(() => route.path);
const currentPageTitle = computed(() => route.meta.title || "管理员系统");
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
.admin-layout {
  height: 100vh;
}

.sidebar {
  background: #304156;
  color: #fff;

  .logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #2a3f54;
    border-bottom: 1px solid #1f2d3d;

    h2 {
      margin: 0;
      font-size: 20px;
      font-weight: 600;
      color: #fff;
    }
  }

  .sidebar-menu {
    border: none;
    background: transparent;

    :deep(.el-menu-item),
    :deep(.el-sub-menu__title) {
      color: #bfcbd9;

      &:hover {
        background-color: rgba(255, 255, 255, 0.1);
        color: #fff;
      }

      &.is-active {
        background-color: #409eff;
        color: #fff;
      }
    }

    :deep(.el-sub-menu) {
      .el-menu-item {
        background-color: rgba(0, 0, 0, 0.2);
        min-width: 0;

        &.is-active {
          background-color: #409eff;
        }
      }
    }
  }
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  background: #fff;
  border-bottom: 1px solid #e6e6e6;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);

  .header-left {
    .page-title {
      font-size: 18px;
      font-weight: 500;
      color: #303133;
    }
  }

  .header-right {
    .user-info {
      display: flex;
      align-items: center;
      gap: 10px;
      cursor: pointer;

      .username {
        font-size: 14px;
        color: #606266;
      }
    }
  }
}

.main-content {
  background: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}
</style>
