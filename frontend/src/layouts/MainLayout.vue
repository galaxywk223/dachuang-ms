<template>
  <el-container class="layout-container">
    <!-- Sidebar -->
    <el-aside :width="isCollapse ? '64px' : '260px'" class="app-sidebar">
      <div class="logo-area" :class="{ 'collapsed': isCollapse }" @click="toggleSidebar">
        <div class="logo-icon">
          <el-icon><School /></el-icon>
        </div>
        <transition name="fade">
          <span v-show="!isCollapse" class="app-title">大创管理平台</span>
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
          <!-- 立项管理 -->
          <el-sub-menu index="establishment">
            <template #title>
              <el-icon><DocumentAdd /></el-icon>
              <span>立项管理</span>
            </template>
            <el-menu-item index="/establishment/apply">申请项目</el-menu-item>
            <el-menu-item index="/establishment/my-projects">我的项目</el-menu-item>
            <el-menu-item index="/establishment/drafts">草稿箱</el-menu-item>
          </el-sub-menu>



          <!-- 结题管理 -->
          <el-sub-menu index="closure">
            <template #title>
              <el-icon><DocumentChecked /></el-icon>
              <span>结题管理</span>
            </template>
            <el-menu-item index="/closure/pending">待结题项目</el-menu-item>
            <el-menu-item index="/closure/applied">已申请结题</el-menu-item>
            <el-menu-item index="/closure/drafts">草稿箱</el-menu-item>
          </el-sub-menu>

          <!-- 使用帮助 -->
          <el-menu-item index="/help">
            <el-icon><QuestionFilled /></el-icon>
            <template #title>使用帮助</template>
          </el-menu-item>
        </el-menu>
      </el-scrollbar>
    </el-aside>

    <!-- Main Content -->
    <el-container class="main-wrapper">
      <el-header class="app-header">
        <div class="header-left">
          <el-breadcrumb separator="/" class="breadcrumb">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <template v-for="(matched, index) in breadcrumbs" :key="matched.path">
               <!-- Make breadcrumb clickable if it has a redirect or component, and is not the last item -->
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
          <!-- TODO: Notifications -->
          <el-button circle text class="icon-btn">
            <el-badge is-dot class="badge-dot" :hidden="!hasUnread">
              <el-icon :size="20"><Bell /></el-icon>
            </el-badge>
          </el-button>

          <el-dropdown trigger="click" @command="handleCommand">
            <div class="user-profile">
              <el-avatar :size="36" class="avatar-gradient">
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
import { ElMessageBox } from 'element-plus';
import {
  School, DocumentAdd, DocumentChecked, 
  QuestionFilled, Bell, ArrowDown, 
  User, SwitchButton
} from '@element-plus/icons-vue';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const isCollapse = ref(false);
const hasUnread = ref(true); // Demo state

const activeMenu = computed(() => route.path);
const userName = computed(() => userStore.user?.real_name || '学生用户');
const userInitials = computed(() => userName.value?.[0] || 'S');

// Generate breadcrumbs from matched routes
const breadcrumbs = computed(() => {
  return route.matched.filter(item => item.meta && item.meta.title && item.path !== '/');
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
  } else if (command === 'profile') {
    // Navigate to profile
  }
};
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.layout-container {
  height: 100vh;
  background-color: #f8fafc; // Light Slate
}

.app-sidebar {
  background: linear-gradient(135deg, #312e81 0%, #4338ca 100%); // Deep Indigo (Matches Login)
  transition: width $transition-base;
  border-right: none;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 4px 0 24px rgba(0,0,0,0.1); // Add depth
  z-index: 20;

  .logo-area {
    height: 70px; // Slightly taller
    display: flex;
    align-items: center;
    padding: 0 20px;
    background: rgba(255, 255, 255, 0.05);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    cursor: pointer;
    transition: background 0.3s;

    &:hover {
      background: rgba(255, 255, 255, 0.1);
    }
    
    .logo-icon {
      width: 36px;
      height: 36px;
      background: rgba(255, 255, 255, 0.2); // Glassy
      backdrop-filter: blur(10px);
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      flex-shrink: 0;
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);

      .el-icon { font-size: 20px; }
    }

    .app-title {
      margin-left: 14px;
      color: white;
      font-weight: 700;
      font-size: 16px;
      white-space: nowrap;
      letter-spacing: 0.5px;
      text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    &.collapsed {
      padding: 0;
      justify-content: center;
    }
  }

  .sidebar-menu {
    border-right: none;
    padding-top: 16px;

    /* Standard Menu Item Styles */
    :deep(.el-menu-item), :deep(.el-sub-menu__title) {
      height: 50px;
      margin: 4px 12px;
      border-radius: $radius-md;
      
      &:hover {
        background-color: rgba(255,255,255, 0.1);
        color: white;
      }

      &.is-active {
        background: rgba(255, 255, 255, 0.15); // Translucent active
        color: white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        font-weight: 600;
        
        &::before {
             content: '';
             position: absolute;
             left: 0;
             top: 50%;
             transform: translateY(-50%);
             width: 4px;
             height: 20px;
             background: #6366f1; // Indigo accent
             border-radius: 0 4px 4px 0;
        }
      }
    }
    
    /* Collapsed State Overrides - Fix Messiness */
    &.el-menu--collapse {
      :deep(.el-menu-item), :deep(.el-sub-menu__title) {
         margin: 4px 0 !important; /* Remove horizontal margins */
         padding: 0 !important; /* Force center */
         display: flex;
         justify-content: center;
         align-items: center;
      }
      
      :deep(.el-menu-item.is-active), :deep(.el-sub-menu__title.is-active) {
         background: transparent !important; /* Remove background block in collapsed to avoid boxy look */
         
         .el-icon { 
            color: #fff;
            filter: drop-shadow(0 0 4px rgba(99, 102, 241, 0.6)); /* Glow instead of bg */
         }

         &::before { display: none; } /* Hide border accent */
      }
    }

    :deep(.el-sub-menu .el-menu-item) {
        min-width: unset;
    }
  }
}

.main-wrapper {
  flex-direction: column;
}

.app-header {
  height: 70px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  border-bottom: 1px solid $slate-100;
  z-index: 10;

  .header-left {
    display: flex;
    align-items: center;
    gap: 20px;
    
    .breadcrumb {
        font-size: 14px;
        /* Make breadcrumbs clickable style */
        :deep(.el-breadcrumb__inner.is-link) {
           color: $slate-500;
           font-weight: normal;
           &:hover { color: $primary-600; }
        }
    }
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 24px;

    .icon-btn {
      color: $slate-400;
      transition: all 0.2s;
      
      &:hover { 
          color: $slate-700; 
          background: $slate-50;
      }
    }

    .user-profile {
      display: flex;
      align-items: center;
      gap: 12px;
      cursor: pointer;
      padding: 6px 12px;
      border-radius: 30px;
      transition: background $transition-fast;
      border: 1px solid transparent;

      &:hover {
        background: $slate-50;
        border-color: $slate-200;
      }

      .username {
        font-weight: 500;
        color: $slate-700;
        font-size: 14px;
      }

      .avatar-gradient {
        background: linear-gradient(135deg, #6366f1, #818cf8);
        font-weight: 700;
        color: white;
        border: 2px solid white;
        box-shadow: 0 2px 6px rgba(99, 102, 241, 0.3);
      }
    }
  }
}

.app-main {
  padding: 32px; // More breathing room
  background-color: #f8fafc;
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
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
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
