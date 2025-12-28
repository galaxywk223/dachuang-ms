<template>
  <div class="welcome-section">
    <div class="welcome-content">
      <div class="welcome-text">
        <h2>欢迎回来，{{ user?.real_name }}！</h2>
        <p>{{ greeting }}，祝您工作愉快！</p>
      </div>
      <div class="welcome-actions">
        <slot name="actions"></slot>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

interface Props {
  user?: {
    real_name?: string;
  };
}

defineProps<Props>();

defineSlots<{
  actions?: () => void;
}>();

const greeting = computed(() => {
  const hour = new Date().getHours();
  if (hour < 12) return "上午好";
  if (hour < 18) return "下午好";
  return "晚上好";
});
</script>

<style scoped lang="scss">
.welcome-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 24px;
  color: white;
  margin-bottom: 24px;

  .welcome-content {
    display: flex;
    justify-content: space-between;
    align-items: center;

    .welcome-text {
      h2 {
        margin: 0 0 8px 0;
        font-size: 24px;
        font-weight: 600;
      }

      p {
        margin: 0;
        opacity: 0.9;
        font-size: 16px;
      }
    }

    .welcome-actions {
      display: flex;
      gap: 12px;
    }
  }
}
</style>
