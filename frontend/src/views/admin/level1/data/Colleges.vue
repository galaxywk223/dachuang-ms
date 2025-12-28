<template>
  <div class="colleges-page">
    <el-card class="main-card" shadow="never">
      <template #header>
         <div class="card-header">
           <div class="header-left">
             <span class="header-title">学院管理</span>
           </div>
         </div>
      </template>
      <el-empty description="此模块正在开发中..." />
    </el-card>
  </div>
</template>

<script setup lang="ts">
defineOptions({ name: "Level1CollegesView" });
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.colleges-page {
  padding: 20px;
}

.main-card {
  border-radius: 8px;
  :deep(.el-card__header) {
      padding: 16px 20px;
      font-weight: 600;
      border-bottom: 1px solid $color-border-light;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
    display: flex;
    align-items: center;
}

.header-title {
    font-size: 16px;
    color: $slate-800;
}
</style>
