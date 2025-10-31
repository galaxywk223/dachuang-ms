<template>
  <el-container class="main-layout">
    <el-aside width="240px" class="sidebar">
      <div class="logo">
        <el-icon class="logo-icon"><School /></el-icon>
        <h3>大创项目管理平台</h3>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#001529"
        text-color="#8c8c8c"
        active-text-color="#ffffff"
        class="sidebar-menu"
      >
        <!-- 立项管理 -->
        <el-sub-menu index="establishment">
          <template #title>
            <el-icon><DocumentAdd /></el-icon>
            <span>立项管理</span>
          </template>
          <el-menu-item index="/establishment/apply">
            <el-icon><Edit /></el-icon>
            <span>申请项目</span>
          </el-menu-item>
          <el-menu-item index="/establishment/my-projects">
            <el-icon><User /></el-icon>
            <span>我的项目</span>
          </el-menu-item>
          <el-menu-item index="/establishment/drafts">
            <el-icon><Files /></el-icon>
            <span>草稿箱</span>
          </el-menu-item>
        </el-sub-menu>

        <!-- 中期管理 -->
        <el-sub-menu index="midterm">
          <template #title>
            <el-icon><Document /></el-icon>
            <span>中期管理</span>
          </template>
          <el-menu-item index="/midterm/submit">
            <el-icon><Edit /></el-icon>
            <span>提交中期检查</span>
          </el-menu-item>
          <el-menu-item index="/midterm/my-checks">
            <el-icon><User /></el-icon>
            <span>我的中期检查</span>
          </el-menu-item>
          <el-menu-item index="/midterm/drafts">
            <el-icon><Files /></el-icon>
            <span>草稿箱</span>
          </el-menu-item>
        </el-sub-menu>

        <!-- 结题管理 -->
        <el-sub-menu index="closure">
          <template #title>
            <el-icon><DocumentChecked /></el-icon>
            <span>结题管理</span>
          </template>
          <el-menu-item index="/closure/pending">
            <el-icon><Clock /></el-icon>
            <span>待结题项目</span>
          </el-menu-item>
          <el-menu-item index="/closure/applied">
            <el-icon><Document /></el-icon>
            <span>已申请结题项目</span>
          </el-menu-item>
          <el-menu-item index="/closure/drafts">
            <el-icon><Files /></el-icon>
            <span>草稿箱</span>
          </el-menu-item>
        </el-sub-menu>

        <!-- 使用帮助 -->
        <el-menu-item index="/help">
          <el-icon><QuestionFilled /></el-icon>
          <span>使用帮助</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="main-header">
        <div class="header-content">
          <div class="left">
            <el-button
              v-if="!sidebarCollapsed"
              :icon="Fold"
              text
              @click="toggleSidebar"
              class="collapse-btn"
            />
            <el-button
              v-else
              :icon="Expand"
              text
              @click="toggleSidebar"
              class="collapse-btn"
            />
            <span class="page-title">{{ pageTitle }}</span>
          </div>
          <div class="right">
            <span class="welcome-text"
              >您好, {{ userStore.user?.real_name || "用户" }}</span
            >
            <el-badge
              :value="unreadCount"
              :hidden="unreadCount === 0"
              class="notifications-badge"
            >
              <el-button
                :icon="Bell"
                circle
                text
                @click="$router.push('/notifications')"
              />
            </el-badge>
            <el-dropdown @command="handleCommand" class="user-dropdown">
              <div class="user-info">
                <el-avatar :size="32" class="user-avatar">
                  {{ userStore.user?.real_name?.[0] || "U" }}
                </el-avatar>
                <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">
                    <el-icon><User /></el-icon>个人信息
                  </el-dropdown-item>
                  <el-dropdown-item command="logout" divided>
                    <el-icon><SwitchButton /></el-icon>退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-header>

      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useUserStore } from "@/stores/user";
import {
  DocumentAdd,
  DocumentChecked,
  Document,
  Folder,
  QuestionFilled,
  Bell,
  User,
  School,
  Fold,
  Expand,
  ArrowDown,
  SwitchButton,
  Edit,
  Files,
  Clock,
} from "@element-plus/icons-vue";
import { ElMessageBox } from "element-plus";

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

// 侧边栏状态
const sidebarCollapsed = ref(false);

// 未读通知数量
const unreadCount = ref(0);

const activeMenu = computed(() => route.path);
const pageTitle = computed(() => route.meta.title || "大创项目管理平台");

// 切换侧边栏
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value;
};

// 获取用户信息和通知数量
onMounted(async () => {
  if (!userStore.user) {
    await userStore.fetchProfile();
  }
  // TODO: 获取未读通知数量
  // unreadCount.value = await fetchUnreadNotificationCount()
});

const handleCommand = async (command) => {
  if (command === "logout") {
    await ElMessageBox.confirm("确定要退出登录吗？", "提示", {
      confirmButtonText: "确定",
      cancelButtonText: "取消",
      type: "warning",
    });
    await userStore.logoutAction();
    router.push("/login");
  } else if (command === "profile") {
    router.push("/profile");
  }
};
</script>

<style scoped lang="scss">
.main-layout {
  height: 100vh;
  background: #f0f2f5;
}

// 侧边栏样式
.sidebar {
  background: linear-gradient(180deg, #001529 0%, #002140 100%);
  box-shadow: 2px 0 6px 0 rgba(0, 21, 41, 0.35);
  transition: all 0.3s;

  .logo {
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    background: rgba(255, 255, 255, 0.05);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);

    .logo-icon {
      font-size: 28px;
      margin-right: 12px;
      color: #1890ff;
    }

    h3 {
      margin: 0;
      font-size: 18px;
      font-weight: 600;
      letter-spacing: 0.5px;
    }
  }

  .sidebar-menu {
    border: none;

    :deep(.el-sub-menu) {
      .el-sub-menu__title {
        height: 48px;
        line-height: 48px;
        margin: 4px 12px;
        border-radius: 8px;
        transition: all 0.3s;

        &:hover {
          background: rgba(24, 144, 255, 0.1) !important;
          color: #ffffff !important;
        }

        .el-icon {
          margin-right: 12px;
          font-size: 16px;
          color: inherit;
        }
      }

      .el-menu {
        background-color: #000c17 !important;
      }

      .el-menu-item {
        height: 44px;
        line-height: 44px;
        margin: 4px 12px;
        padding-left: 48px !important;
        border-radius: 8px;
        transition: all 0.3s;

        &:hover {
          background: rgba(24, 144, 255, 0.1) !important;
          color: #ffffff !important;
        }

        &.is-active {
          background: linear-gradient(
            90deg,
            #1890ff 0%,
            #40a9ff 100%
          ) !important;
          color: #ffffff !important;
          box-shadow: 0 2px 8px rgba(24, 144, 255, 0.3);
        }

        .el-icon {
          margin-right: 8px;
          font-size: 14px;
        }
      }
    }

    :deep(.el-menu-item) {
      height: 48px;
      line-height: 48px;
      margin: 4px 12px;
      border-radius: 8px;
      transition: all 0.3s;

      &:hover {
        background: rgba(24, 144, 255, 0.1) !important;
        color: #ffffff !important;
      }

      &.is-active {
        background: linear-gradient(90deg, #1890ff 0%, #40a9ff 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 2px 8px rgba(24, 144, 255, 0.3);

        &::before {
          display: none;
        }
      }

      .el-icon {
        margin-right: 12px;
        font-size: 16px;
      }
    }
  }
}

// 头部样式
.main-header {
  background: #ffffff;
  border-bottom: 1px solid #f0f0f0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  padding: 0 24px;

  .header-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 100%;

    .left {
      display: flex;
      align-items: center;

      .collapse-btn {
        font-size: 18px;
        color: #666;
        margin-right: 16px;

        &:hover {
          background: #f5f5f5;
        }
      }

      .page-title {
        font-size: 18px;
        font-weight: 500;
        color: #262626;
      }
    }

    .right {
      display: flex;
      align-items: center;
      gap: 16px;

      .welcome-text {
        font-size: 14px;
        color: #262626;
        margin-right: 8px;
      }

      .notifications-badge {
        .el-button {
          color: #666;
          font-size: 18px;

          &:hover {
            background: #f5f5f5;
            color: #1890ff;
          }
        }
      }

      .user-dropdown {
        .user-info {
          display: flex;
          align-items: center;
          cursor: pointer;
          padding: 8px 12px;
          border-radius: 20px;
          transition: all 0.3s;

          &:hover {
            background: #f5f5f5;
          }

          .user-avatar {
            margin-right: 8px;
            background: linear-gradient(135deg, #1890ff 0%, #40a9ff 100%);
            font-weight: 500;
          }

          .dropdown-icon {
            font-size: 12px;
            color: #999;
            transition: transform 0.3s;
          }
        }

        &:hover .dropdown-icon {
          transform: rotate(180deg);
        }
      }
    }
  }
}

// 主内容区域样式
:deep(.el-main) {
  background: #f0f2f5;
  padding: 24px;
  overflow-y: auto;

  &::-webkit-scrollbar {
    width: 6px;
  }

  &::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 3px;
  }

  &::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 3px;

    &:hover {
      background: #a8a8a8;
    }
  }
}

// 下拉菜单样式
:deep(.el-dropdown-menu) {
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border: 1px solid #e8e8e8;
  padding: 8px;

  .el-dropdown-menu__item {
    border-radius: 6px;
    padding: 8px 12px;
    margin: 2px 0;

    .el-icon {
      margin-right: 8px;
    }

    &:hover {
      background: #f5f5f5;
      color: #1890ff;
    }
  }
}
</style>
