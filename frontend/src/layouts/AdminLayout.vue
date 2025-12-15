<template>
  <el-container class="layout-container">
    <!-- Sidebar -->
    <el-aside :width="isCollapse ? '64px' : '260px'" class="app-sidebar">
      <div class="logo-area" :class="{ 'collapsed': isCollapse }">
        <div class="logo-icon admin-logo">
          <el-icon><DataAnalysis /></el-icon>
        </div>
        <transition name="fade">
          <span v-show="!isCollapse" class="app-title">大创管理系统</span>
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
          <el-menu-item index="/admin/dashboard">
            <el-icon><DataAnalysis /></el-icon>
            <template #title>数据统计</template>
          </el-menu-item>

          <el-sub-menu index="project-review">
            <template #title>
              <el-icon><Document /></el-icon>
              <span>项目审核</span>
            </template>
            <el-menu-item index="/admin/review/establishment">立项审核</el-menu-item>
            <el-menu-item index="/admin/review/midterm">中期审核</el-menu-item>
            <el-menu-item index="/admin/review/closure">结题审核</el-menu-item>
          </el-sub-menu>

          <el-menu-item index="/admin/projects">
            <el-icon><Files /></el-icon>
            <template #title>项目管理</template>
          </el-menu-item>

          <el-menu-item index="/admin/users">
            <el-icon><User /></el-icon>
            <template #title>用户管理</template>
          </el-menu-item>

          <el-menu-item index="/admin/settings">
            <el-icon><Setting /></el-icon>
            <template #title>系统设置</template>
          </el-menu-item>
        </el-menu>
      </el-scrollbar>
    </el-aside>

    <!-- Main Content -->
    <el-container class="main-wrapper">
      <el-header class="app-header">
        <div class="header-left">
          <el-button
            type="text"
            class="toggle-btn"
            @click="toggleSidebar"
          >
            <el-icon :size="20">
              <Expand v-if="isCollapse" />
              <Fold v-else />
            </el-icon>
          </el-button>
          
          <el-breadcrumb separator="/" class="breadcrumb">
            <el-breadcrumb-item :to="{ path: '/admin/dashboard' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>{{ route.meta.title || '管理后台' }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="header-right">
          <el-dropdown trigger="click" @command="handleCommand">
            <div class="user-profile">
              <el-avatar :size="36" class="avatar-gradient admin-avatar">
                {{ userInitials }}
              </el-avatar>
              <span class="username">{{ userName }}</span>
              <el-icon><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu class="custom-dropdown">
                <el-dropdown-item command="profile">
                  <el-icon><User /></el-icon>个人中心
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
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user';
import { ElMessage, ElMessageBox } from 'element-plus';
import {
  DataAnalysis, Document, Files, User, Setting,
  Expand, Fold, ArrowDown, SwitchButton
} from '@element-plus/icons-vue';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const isCollapse = ref(false);

const activeMenu = computed(() => route.path);
const userName = computed(() => userStore.user?.real_name || '管理员');
const userInitials = computed(() => userName.value?.[0] || 'A');

const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value;
};

const handleCommand = async (command: string) => {
  if (command === 'logout') {
    try {
      await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        type: 'warning',
        confirmButtonText: '退出',
        cancelButtonText: '取消'
      });
      await userStore.logoutAction();
      router.push('/login');
    } catch {
      // cancel
    }
  } else if (command === 'profile') {
    ElMessage.info('功能开发中');
  }
};
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.layout-container {
  height: 100vh;
  background-color: $color-bg-body;
}

.app-sidebar {
  background-color: $slate-900;
  transition: width $transition-base;
  border-right: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  flex-direction: column;
  overflow: hidden;

  .logo-area {
    height: 64px;
    display: flex;
    align-items: center;
    padding: 0 20px;
    background: rgba(0, 0, 0, 0.2); // Slightly darker for admin
    
    .logo-icon {
      width: 32px;
      height: 32px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      flex-shrink: 0;

      &.admin-logo {
        background: linear-gradient(135deg, $danger, $warning); // Admin distinct color (e.g., Red/Orange or just keep Blue)
        // Actually, stick to Blue for consistency, or maybe Purple?
        background: linear-gradient(135deg, #6366f1, #8b5cf6); // Violet/Indigo
      }
    }

    .app-title {
      margin-left: 12px;
      color: white;
      font-weight: 600;
      font-size: 16px;
      white-space: nowrap;
    }

    &.collapsed {
      padding: 0;
      justify-content: center;
    }
  }

  .sidebar-menu {
    border-right: none;
    padding-top: 10px;

    :deep(.el-menu-item), :deep(.el-sub-menu__title) {
      height: 50px;
      margin: 4px 10px;
      border-radius: $radius-md;
      
      &:hover {
        background-color: rgba(255,255,255, 0.08);
        color: white;
      }

      &.is-active {
        background: linear-gradient(90deg, $primary-600, $primary-500);
        color: white;
        box-shadow: 0 4px 12px rgba($primary-600, 0.3);
      }
    }
  }
}

.main-wrapper {
  flex-direction: column;
}

.app-header {
  height: 64px;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: $shadow-sm;
  z-index: 10;

  .header-left {
    display: flex;
    align-items: center;
    gap: 16px;

    .toggle-btn {
      color: $slate-600;
      &:hover { color: $primary-600; }
    }
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 20px;

    .user-profile {
      display: flex;
      align-items: center;
      gap: 10px;
      cursor: pointer;
      padding: 4px 8px;
      border-radius: 20px;
      transition: background $transition-fast;

      &:hover {
        background: $slate-100;
      }

      .username {
        font-weight: 500;
        color: $slate-700;
        font-size: 14px;
      }

      .avatar-gradient {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        font-weight: 600;
        color: white;
        border: 2px solid white;
        box-shadow: $shadow-sm;
      }
    }
  }
}

.app-main {
  padding: 24px;
  background-color: $slate-50;
  overflow-y: auto;
}

/* Transitions */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.fade-transform-enter-active,
.fade-transform-leave-active {
  transition: all 0.3s ease;
}
.fade-transform-enter-from {
  opacity: 0;
  transform: translateY(10px);
}
.fade-transform-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
