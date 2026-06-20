<template>
  <ProjectManagement
    scope="level2"
    title="项目管理"
    :allow-create="true"
    :show-project-no="false"
    :show-approved-budget="false"
    :show-certificate="false"
  />
</template>

<script setup lang="ts">
import ProjectManagement from "@/views/admin/shared/ProjectManagement.vue";

defineOptions({ name: "Level2ProjectsView" });
</script>
