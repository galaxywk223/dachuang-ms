<template>
  <div class="dashboard-container">
    <div class="welcome-section">
      <h1>欢迎回来，一级管理员</h1>
      <p>这里是系统最高管理中心，您可以维护用户数据和基础信息。</p>
    </div>
    
    <div class="stats-cards">
      <el-card class="stat-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>学生总数</span>
          </div>
        </template>
        <div class="card-value">1,234</div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>二级管理员</span>
          </div>
        </template>
        <div class="card-value">56</div>
      </el-card>

      <el-card class="stat-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <span>学院数量</span>
          </div>
        </template>
        <div class="card-value">12</div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
// Logic to fetch stats can go here
</script>

<style scoped>
.dashboard-container {
  padding: 24px;
}
.welcome-section {
  margin-bottom: 32px;
}
.welcome-section h1 {
  font-size: 28px;
  margin-bottom: 8px;
  color: #1e293b;
}
.welcome-section p {
  color: #64748b;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 24px;
}

.stat-card .card-header {
  font-weight: 500;
  color: #64748b;
}

.stat-card .card-value {
  font-size: 32px;
  font-weight: 700;
  color: #0f172a;
  margin-top: 12px;
}
</style>
