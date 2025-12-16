<template>
  <div class="page-container">
    <div class="page-header">
      <div class="title-area">
        <h1>学院信息维护</h1>
        <p class="subtitle">管理全校学院及部门基础数据</p>
      </div>
    </div>

    <el-card class="content-card" shadow="never">
       <el-empty description="此模块正在开发中..." />
    </el-card>
  </div>
</template>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.page-container {
  padding: 0;
}

.page-header {
  margin-bottom: 24px;
  h1 {
    font-size: 24px;
    font-weight: 600;
    color: $slate-800;
    margin: 0 0 8px 0;
  }
}

.subtitle {
  color: $slate-500;
  margin: 0;
}
</style>
