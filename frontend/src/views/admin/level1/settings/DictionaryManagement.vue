<template>
  <div class="dictionary-management">
    <el-tabs v-model="activeTab" class="custom-tabs">
      <el-tab-pane label="项目参数" name="project">
        <SystemDictionaries category="project" />
      </el-tab-pane>
      <el-tab-pane label="组织参数" name="org">
        <SystemDictionaries category="org" />
      </el-tab-pane>
      <el-tab-pane label="成果参数" name="achievement">
        <SystemDictionaries category="achievement" />
      </el-tab-pane>
      <el-tab-pane label="用户角色" name="roles">
        <RoleManagement />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import SystemDictionaries from "./SystemDictionaries.vue";
// Import RoleManagement from its location
import RoleManagement from "@/views/admin/level1/users/RoleManagement.vue";

const activeTab = ref("project");
</script>

<style scoped lang="scss">
.dictionary-management {
  padding: 20px;
}
</style>
