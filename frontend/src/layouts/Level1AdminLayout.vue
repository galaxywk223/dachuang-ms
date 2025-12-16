<template>
  <el-container class="layout-container">
    <!-- Sidebar -->
    <el-aside :width="isCollapse ? '64px' : '260px'" class="app-sidebar">
      <div class="logo-area" :class="{ 'collapsed': isCollapse }" @click="toggleSidebar">
        <div class="logo-icon admin-logo">
          <el-icon><Management /></el-icon>
        </div>
        <transition name="fade">
          <span v-show="!isCollapse" class="app-title">系统管理中心</span>
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
          <el-menu-item index="/level1-admin/dashboard">
            <el-icon><Odometer /></el-icon>
            <template #title>控制台</template>
          </el-menu-item>

          <!-- 用户管理 -->
          <el-sub-menu index="users">
            <template #title>
              <el-icon><UserFilled /></el-icon>
              <span>用户维护</span>
            </template>
            <el-menu-item index="/level1-admin/users/students">学生管理</el-menu-item>
            <el-menu-item index="/level1-admin/users/admins">二级管理员</el-menu-item>
          </el-sub-menu>

          <!-- 数据维护 -->
          <el-sub-menu index="data">
            <template #title>
              <el-icon><DataLine /></el-icon>
              <span>数据维护</span>
            </template>
            <el-menu-item index="/level1-admin/data/colleges">学院信息</el-menu-item>
            <!-- Add more as needed -->
          </el-sub-menu>

        </el-menu>
      </el-scrollbar>
    </el-aside>

    <!-- Main Content -->
    <el-container class="main-wrapper">
      <el-header class="app-header">
        <div class="header-left">
          <el-breadcrumb separator="/" class="breadcrumb">
            <el-breadcrumb-item :to="{ path: '/level1-admin' }">首页</el-breadcrumb-item>
            <template v-for="(matched, index) in breadcrumbs" :key="matched.path">
               <el-breadcrumb-item
                  v-if="matched.meta && matched.meta.title"
                  :to="{ path: matched.path }"
               >
                  {{ matched.meta.title }}
               </el-breadcrumb-item>
            </template>
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
                <el-dropdown-item command="logout">
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
  Management, Odometer, UserFilled, DataLine,
  ArrowDown, SwitchButton
} from '@element-plus/icons-vue';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const isCollapse = ref(false);

const activeMenu = computed(() => route.path);
const userName = computed(() => userStore.user?.real_name || '一级管理员');
const userInitials = computed(() => userName.value?.[0] || 'A');

const breadcrumbs = computed(() => {
  return route.matched.filter(item => item.meta && item.meta.title && item.path !== '/' && item.path !== '/level1-admin');
});

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
  }
};
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.layout-container {
  height: 100vh;
  background-color: #f8fafc;
}

.app-sidebar {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); // Darker for Level 1
  transition: width $transition-base;
  border-right: none;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 4px 0 24px rgba(0,0,0,0.1);
  z-index: 20;

  .logo-area {
    height: 70px;
    display: flex;
    align-items: center;
    padding: 0 20px;
    background: rgba(255, 255, 255, 0.05);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    cursor: pointer;
    transition: background 0.3s;
    
    .logo-icon {
      width: 36px;
      height: 36px;
      background: rgba(255, 255, 255, 0.2);
      backdrop-filter: blur(10px);
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      margin-right: 14px;
    }
    
    .app-title {
      font-weight: 700;
      color: white;
      font-size: 16px;
      white-space: nowrap;
    }
    &.collapsed {
        justify-content: center;
        .app-title { display: none; }
        .logo-icon { margin-right: 0; }
    }
  }

  .sidebar-menu {
    border-right: none;
    padding-top: 16px;
    
    :deep(.el-menu-item) {
        &:hover { background-color: rgba(255,255,255,0.1); }
        &.is-active {
            background: rgba(255,255,255,0.15);
            color: white;
            font-weight: 600;
        }
    }
  }
}

.main-wrapper {
  flex-direction: column;
}

.app-header {
  height: 70px;
  background: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 32px;
  border-bottom: 1px solid #e2e8f0;
}

.app-main {
  padding: 32px;
  background-color: #f8fafc;
  overflow-y: auto;
}
</style>
