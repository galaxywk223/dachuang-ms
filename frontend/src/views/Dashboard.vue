<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="我的项目" :value="statistics.myProjects">
            <template #prefix>
              <el-icon><Folder /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="待审核" :value="statistics.pending">
            <template #prefix>
              <el-icon><Clock /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="进行中" :value="statistics.inProgress">
            <template #prefix>
              <el-icon><Loading /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="未读通知" :value="statistics.unreadNotifications">
            <template #prefix>
              <el-icon><Bell /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>
    
    <el-card style="margin-top: 20px">
      <template #header>
        <span>欢迎使用大创项目管理平台</span>
      </template>
      <el-result
        icon="success"
        title="系统已就绪"
        sub-title="请从左侧菜单开始使用"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const statistics = ref({
  myProjects: 0,
  pending: 0,
  inProgress: 0,
  unreadNotifications: 0
})

onMounted(() => {
  // TODO: 加载统计数据
})
</script>

<style scoped>
.dashboard {
  /* 样式 */
}
</style>
