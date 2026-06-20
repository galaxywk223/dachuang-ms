<template>
  <ProjectManagement
    scope="level1"
    title="系统项目管理"
    :allow-create="false"
    :show-project-no="true"
    :show-approved-budget="true"
    :show-certificate="true"
  />
</template>

<script setup lang="ts">
import ProjectManagement from "@/views/admin/shared/ProjectManagement.vue";

defineOptions({ name: "Level1ProjectsView" });
</script>
