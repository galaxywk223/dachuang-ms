<template>
  <el-container class="layout-container">
    <!-- Sidebar -->
    <el-aside :width="isCollapse ? '64px' : '260px'" class="app-sidebar">
      <div class="logo-area" :class="{ 'collapsed': isCollapse }" @click="toggleSidebar">
        <div class="logo-icon">
             <img src="@/assets/ahut_logo.jpg" alt="Logo" style="width: 100%; height: 100%; object-fit: cover; border-radius: 50%;" />
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
          <template v-for="item in currentMenus" :key="item.index">
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
        </el-menu>
      </el-scrollbar>
    </el-aside>

    <!-- Main Content -->
    <el-container class="main-wrapper">
      <el-header class="app-header">
        <div class="header-left">
          <div class="toggle-btn" @click="toggleSidebar">
             <el-icon :size="20"><Expand v-if="isCollapse" /><Fold v-else /></el-icon>
          </div>
          <el-breadcrumb separator="/" class="breadcrumb">
            <el-breadcrumb-item :to="{ path: homePath }">首页</el-breadcrumb-item>
            <template v-for="matched in breadcrumbs" :key="matched.path">
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
          <!-- Notification Bell (Common) -->
          <el-button circle text class="icon-btn">
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
                <el-button type="primary" :loading="passwordLoading" @click="handleSubmitPassword">
                    确认修改
                </el-button>
            </span>
        </template>
      </el-dialog>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from '@/stores/user';
import { ElMessageBox, ElMessage } from 'element-plus';
import {
  School, DocumentAdd, DocumentChecked, 
  QuestionFilled, Bell, ArrowDown, 
  SwitchButton, Management,

  DataAnalysis, UserFilled,
  DataLine, Expand, Fold, Lock, Setting
} from '@element-plus/icons-vue';
import { reactive } from 'vue';

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const isCollapse = ref(false);
const hasUnread = ref(false); 

// User Info
const userRole = computed(() => String(userStore.user?.role || localStorage.getItem('user_role') || 'student').toLowerCase());
const userName = computed(() => userStore.user?.real_name || (userRole.value === 'student' ? '学生用户' : '管理员'));
const userInitials = computed(() => userName.value?.[0] || 'U');

// Role-based helper classes
const roleClass = computed(() => {
    switch(userRole.value) {
        case 'level1_admin': return 'role-admin-1';
        case 'level2_admin': return 'role-admin-2';
        default: return 'role-student';
    }
});

const appTitle = computed(() => {
    switch(userRole.value) {
        case 'level1_admin': return '系统管理中心';
        case 'level2_admin': return '大创管理系统';
        default: return '大创管理平台';
    }
});

const homePath = computed(() => {
    switch(userRole.value) {
        case 'level1_admin': return '/level1-admin/users/students';
        case 'level2_admin': return '/admin/projects';
        default: return '/';
    }
});

const activeMenu = computed(() => route.path);
const breadcrumbs = computed(() => {
  return route.matched.filter(item => item.meta && item.meta.title && item.path !== '/' && item.path !== '/admin' && item.path !== '/level1-admin');
});

// Definition of Menus
const currentMenus = computed(() => {
    switch (userRole.value) {
        case 'student':
            return [
                {
                    index: 'establishment',
                    title: '立项管理',
                    icon: DocumentAdd,
                    children: [
                        { index: '/establishment/apply', title: '申请项目' },
                        { index: '/establishment/my-projects', title: '我的项目' },
                        { index: '/establishment/drafts', title: '草稿箱' }
                    ]
                },
                {
                    index: 'closure',
                    title: '结题管理',
                    icon: DocumentChecked,
                    children: [
                        { index: '/closure/pending', title: '待结题项目' },
                        { index: '/closure/applied', title: '已申请结题' },
                        { index: '/closure/drafts', title: '草稿箱' }
                    ]
                },
                {
                    index: '/help',
                    title: '使用帮助',
                    icon: QuestionFilled
                }
            ];
        case 'level2_admin':
            return [
                 {
                    index: 'establishment',
                    title: '立项管理',
                    icon: DocumentAdd,
                    children: [
                        { index: '/admin/review/establishment', title: '立项审核' },
                        { index: '/admin/projects', title: '查看项目' },
                    ]
                },
                {
                    index: 'closure',
                    title: '结题管理',
                    icon: DocumentChecked,
                    children: [
                        { index: '/admin/review/closure', title: '结题项目审核' },
                        { index: '/admin/review/achievements', title: '结题成果查看' },
                    ]
                },
            ];
        case 'level1_admin':
             return [
                {
                    index: 'users',
                    title: '用户维护',
                    icon: UserFilled,
                    children: [
                        { index: '/level1-admin/users/students', title: '学生管理' },
                        { index: '/level1-admin/users/admins', title: '二级管理员' },
                    ]
                },
                {
                    index: 'settings',
                    title: '系统配置',
                    icon: Setting,
                    children: [
                         { index: '/level1-admin/settings/dictionaries', title: '字典管理' },
                    ]
                }
             ];
        default:
            return [];
    }
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
  } else if (command === 'changepw') {
      passwordDialogVisible.value = true;
  }
};

// Password Change Logic
import { changePassword } from '@/api/auth';

const passwordDialogVisible = ref(false);
const passwordFormRef = ref();
const passwordLoading = ref(false);

const passwordForm = reactive({
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
});

const passwordRules = {
    oldPassword: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
    newPassword: [
        { required: true, message: '请输入新密码', trigger: 'blur' },
        { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
    ],
    confirmPassword: [
        { required: true, message: '请确认新密码', trigger: 'blur' },
        { 
            validator: (rule: any, value: string, callback: any) => {
                if (value !== passwordForm.newPassword) {
                    callback(new Error('两次输入密码不一致'));
                } else {
                    callback();
                }
            }, 
            trigger: 'blur' 
        }
    ]
};

const handleSubmitPassword = async () => {
    if (!passwordFormRef.value) return;
    
    await passwordFormRef.value.validate(async (valid: boolean) => {
        if (valid) {
            passwordLoading.value = true;
            try {
                const res = await changePassword(
                    passwordForm.oldPassword,
                    passwordForm.newPassword,
                    passwordForm.confirmPassword
                );
                
                if (res.code === 200) {
                    ElMessage.success('密码修改成功，请重新登录');
                    passwordDialogVisible.value = false;
                    await userStore.logoutAction();
                    router.push('/login');
                } else {
                    ElMessage.error(res.message || '修改失败');
                }
            } catch (error: any) {
                ElMessage.error(error.message || '请求失败');
            } finally {
                passwordLoading.value = false;
            }
        }
    });
};

const resetPasswordForm = () => {
    if (passwordFormRef.value) {
        passwordFormRef.value.resetFields();
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
  background-color: $color-bg-sidebar; // Solid Dark Slate
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
    background: rgba(0, 0, 0, 0.2); // Darker top area
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    cursor: pointer;
    transition: background 0.3s;

    &:hover {
      background: rgba(255, 255, 255, 0.05);
    }
    
    .logo-icon {
      width: 36px;
      height: 36px;
      background: rgba(255, 255, 255, 0.1);
      backdrop-filter: blur(10px);
      border-radius: 8px; // Slightly squarer for pro look
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      flex-shrink: 0;
      box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }

    .app-title {
      margin-left: 14px;
      color: $slate-100;
      font-weight: 600;
      font-size: 16px;
      white-space: nowrap;
      letter-spacing: 0.5px;
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
        background-color: rgba(255,255,255, 0.05);
        color: white;
      }

      &.is-active {
        background: $primary-600; // Steady Blue-Grey
        color: white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        font-weight: 500;
      }
    }
    
    /* Collapsed State Overrides */
    &.el-menu--collapse {
      :deep(.el-menu-item), :deep(.el-sub-menu__title) {
         margin: 4px 0 !important;
         padding: 0 !important;
         display: flex;
         justify-content: center;
         align-items: center;
      }
      
      :deep(.el-menu-item.is-active), :deep(.el-sub-menu__title.is-active) {
         background: transparent !important;
         
         .el-icon { 
            color: $primary-400; // Lighten icon for visibility
            filter: drop-shadow(0 0 8px rgba($primary-400, 0.4));
         }
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
  height: 64px; // Slightly more compact header
  background: #ffffff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  border-bottom: 1px solid $slate-200; // Define border clearly
  z-index: 10;
  box-shadow: $shadow-sm;

  .header-left {
    display: flex;
    align-items: center;
    gap: 16px;

    .toggle-btn {
        display: flex;
        align-items: center;
        cursor: pointer;
        color: $slate-500;
        transition: color 0.2s;
        
        &:hover { color: $slate-800; }
    }
    
    .breadcrumb {
        font-size: 14px;
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
    gap: 20px;

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
      padding: 4px 8px 4px 4px;
      border-radius: 30px;
      transition: background $transition-fast;
      border: 1px solid transparent;

      &:hover {
        background: $slate-50;
        border-color: $slate-100;
      }

      .username {
        font-weight: 500;
        color: $slate-700;
        font-size: 14px;
      }

      .avatar-gradient {
        // Default (Student)
        background: linear-gradient(135deg, $primary-500, $primary-700);
        font-weight: 700;
        color: white;
        border: 2px solid white;
        box-shadow: $shadow-sm;

        &.role-admin-1 { // Admin Level 1 (Gold/Amber hint or distinct)
             background: linear-gradient(135deg, $slate-700, $slate-900);
        }
        &.role-admin-2 { // Admin Level 2
             background: linear-gradient(135deg, $primary-600, $primary-800);
        }
      }
    }
  }
}

.app-main {
  padding: 24px; // Tighter padding for efficiency
  background-color: $color-bg-body;
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
