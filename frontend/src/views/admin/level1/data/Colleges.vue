<template>
  <div class="colleges-page">
    <div class="page-header">
      <span class="title">学院信息维护</span>
      <span class="desc">管理系统中的学院列表</span>
    </div>

    <!-- 复用SystemDictionaries组件，指定字典类型为college -->
    <SystemDictionaries category="org" dict-type-code="college" />
  </div>
</template>

<script setup lang="ts">
import SystemDictionaries from "../settings/SystemDictionaries.vue";

defineOptions({ name: "Level1CollegesView" });
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.colleges-page {
  padding: 20px;

  .page-header {
    margin-bottom: 20px;
    display: flex;
    align-items: baseline;
    gap: 12px;

    .title {
      font-size: 18px;
      color: $slate-800;
      font-weight: 600;
    }

    .desc {
      font-size: 13px;
      color: $slate-500;
    }
  }
}
</style>
