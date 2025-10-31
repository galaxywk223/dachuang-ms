<template>
  <el-container class="main-layout">
    <el-aside width="200px">
      <div class="logo">
        <h3>大创管理系统</h3>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/dashboard">
          <el-icon><HomeFilled /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        
        <!-- 学生菜单 -->
        <template v-if="userStore.user?.role === 'STUDENT'">
          <el-menu-item index="/student/projects">
            <el-icon><Folder /></el-icon>
            <span>我的项目</span>
          </el-menu-item>
          <el-menu-item index="/student/project/create">
            <el-icon><Plus /></el-icon>
            <span>项目申报</span>
          </el-menu-item>
        </template>
        
        <!-- 二级管理员菜单 -->
        <template v-if="userStore.user?.role === 'LEVEL2_ADMIN'">
          <el-menu-item index="/admin2/reviews">
            <el-icon><DocumentChecked /></el-icon>
            <span>项目审核</span>
          </el-menu-item>
          <el-menu-item index="/admin2/projects">
            <el-icon><Folder /></el-icon>
            <span>项目管理</span>
          </el-menu-item>
        </template>
        
        <!-- 一级管理员菜单 -->
        <template v-if="userStore.user?.role === 'LEVEL1_ADMIN'">
          <el-menu-item index="/admin1/reviews">
            <el-icon><DocumentChecked /></el-icon>
            <span>项目审核</span>
          </el-menu-item>
          <el-menu-item index="/admin1/projects">
            <el-icon><Folder /></el-icon>
            <span>所有项目</span>
          </el-menu-item>
        </template>
        
        <el-menu-item index="/notifications">
          <el-icon><Bell /></el-icon>
          <span>通知中心</span>
        </el-menu-item>
        
        <el-menu-item index="/profile">
          <el-icon><User /></el-icon>
          <span>个人信息</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <el-container>
      <el-header>
        <div class="header-content">
          <div class="left">
            <span class="page-title">{{ pageTitle }}</span>
          </div>
          <div class="right">
            <el-dropdown @command="handleCommand">
              <span class="user-info">
                <el-icon><User /></el-icon>
                {{ userStore.user?.real_name }}
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">个人信息</el-dropdown-item>
                  <el-dropdown-item command="logout" divided>退出登录</el-dropdown-item>
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
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const activeMenu = computed(() => route.path)
const pageTitle = computed(() => route.meta.title || '大创管理系统')

onMounted(async () => {
  if (!userStore.user) {
    await userStore.fetchProfile()
  }
})

const handleCommand = async (command) => {
  if (command === 'logout') {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await userStore.logoutAction()
    router.push('/login')
  } else if (command === 'profile') {
    router.push('/profile')
  }
}
</script>

<style scoped>
.main-layout {
  height: 100vh;
}

.el-aside {
  background-color: #304156;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  background-color: #2d3a4b;
}

.logo h3 {
  margin: 0;
  font-size: 18px;
}

.el-header {
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  align-items: center;
}

.header-content {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  font-size: 18px;
  font-weight: 500;
  color: #303133;
}

.user-info {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
}

.el-main {
  background-color: #f0f2f5;
  padding: 20px;
}
</style>
