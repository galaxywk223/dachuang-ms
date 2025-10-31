<template>
  <div class="project-item" @click="$emit('click')">
    <div class="project-info">
      <div class="project-name">{{ project.title }}</div>
      <div class="project-meta">
        <el-tag :type="getStatusType(project.status)" size="small">
          {{ getStatusText(project.status) }}
        </el-tag>
        <span class="project-date">{{ formatDate(project.created_at) }}</span>
      </div>
    </div>
    <el-icon class="project-arrow"><ArrowRight /></el-icon>
  </div>
</template>

<script setup>
import { ArrowRight } from "@element-plus/icons-vue";
import { formatDate, getStatusType, getStatusText } from "@/utils/common";

defineEmits(["click"]);

defineProps({
  project: {
    type: Object,
    required: true,
  },
});
</script>

<style scoped lang="scss">
.project-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
  border: 1px solid #f0f0f0;
  margin-bottom: 8px;

  &:hover {
    background-color: #f5f7fa;

    .project-arrow {
      color: #409eff;
    }
  }

  .project-info {
    flex: 1;

    .project-name {
      font-weight: 500;
      color: #303133;
      margin-bottom: 4px;
    }

    .project-meta {
      display: flex;
      align-items: center;
      gap: 8px;

      .project-date {
        font-size: 12px;
        color: #909399;
      }
    }
  }

  .project-arrow {
    color: #c0c4cc;
    transition: color 0.2s;
  }
}
</style>
