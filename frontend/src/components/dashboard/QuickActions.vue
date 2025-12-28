<template>
  <el-card class="content-card">
    <template #header>
      <div class="card-header">
        <span>快速操作</span>
      </div>
    </template>
    <div class="quick-actions">
      <div
        v-for="action in filteredActions"
        :key="action.text"
        class="action-item"
        @click="$router.push(action.route)"
      >
        <div class="action-icon">
          <component :is="action.icon" :size="24" />
        </div>
        <div class="action-text">{{ action.text }}</div>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { computed } from "vue";
import {
  Plus,
  Folder,
  DocumentChecked,
  Bell,
  User,
} from "@element-plus/icons-vue";

const props = defineProps({
  userRole: {
    type: String,
    required: true,
  },
});

const allActions = [
  {
    icon: Plus,
    text: "新建项目",
    route: "/student/project/create",
    roles: ["STUDENT"],
  },
  {
    icon: Folder,
    text: "我的项目",
    route: "/student/projects",
    roles: ["STUDENT"],
  },
  {
    icon: DocumentChecked,
    text: "项目审核",
    route: "/admin2/reviews",
    roles: ["LEVEL2_ADMIN"],
  },
  {
    icon: DocumentChecked,
    text: "项目审核",
    route: "/admin1/reviews",
    roles: ["LEVEL1_ADMIN"],
  },
  {
    icon: Bell,
    text: "通知中心",
    route: "/notifications",
    roles: ["STUDENT", "LEVEL1_ADMIN", "LEVEL2_ADMIN"],
  },
  {
    icon: User,
    text: "个人资料",
    route: "/profile",
    roles: ["STUDENT", "LEVEL1_ADMIN", "LEVEL2_ADMIN"],
  },
];

const filteredActions = computed(() => {
  return allActions.filter((action) => action.roles.includes(props.userRole));
});
</script>

<style scoped lang="scss">
.content-card {
  margin-bottom: 24px;

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 500;
  }

  .quick-actions {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 16px;

    .action-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 20px;
      border-radius: 8px;
      background: #f5f7fa;
      cursor: pointer;
      transition: all 0.2s;

      &:hover {
        background: #ecf5ff;
        transform: translateY(-2px);
      }

      .action-icon {
        width: 48px;
        height: 48px;
        background: #409eff;
        color: white;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 12px;
      }

      .action-text {
        font-size: 14px;
        color: #303133;
        text-align: center;
      }
    }
  }
}
</style>
