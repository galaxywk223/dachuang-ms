<template>
  <div class="dictionary-management">
    <el-tabs v-model="activeTab" class="custom-tabs">
      <el-tab-pane label="项目参数" name="project">
        <SystemDictionaries category="project" />
      </el-tab-pane>
      <el-tab-pane label="组织参数" name="org">
        <SystemDictionaries category="org" :extra-types="orgExtraTypes">
          <template #custom-content="{ type }">
            <RoleManagement v-if="type.code === 'roles'" />
          </template>
        </SystemDictionaries>
      </el-tab-pane>
      <el-tab-pane label="成果参数" name="achievement">
        <SystemDictionaries category="achievement" />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import SystemDictionaries from "./SystemDictionaries.vue";
import RoleManagement from "@/views/admin/level1/users/RoleManagement.vue";

const activeTab = ref("project");

const orgExtraTypes = [
  {
    id: -1, // Use a negative ID to avoid conflict with DB IDs (assuming DB IDs are positive)
    code: "roles",
    name: "用户角色",
    description: "设置系统用户角色及其权限范围",
    isLocal: true,
  },
];
</script>

<style scoped lang="scss">
.dictionary-management {
  padding: 20px;
  .sub-tab-container {
    margin-bottom: 20px;
  }
}
</style>
