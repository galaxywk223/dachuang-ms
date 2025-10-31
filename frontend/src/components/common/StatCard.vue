<template>
  <div class="stat-card">
    <div class="stat-icon" :style="{ background: iconBg }">
      <component :is="icon" :size="32" />
    </div>
    <div class="stat-content">
      <div class="stat-value">{{ value }}</div>
      <div class="stat-label">{{ label }}</div>
      <div class="stat-change" v-if="changeText">
        <span class="change-text">{{ changeText }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  icon: {
    type: [String, Object],
    required: true,
  },
  iconBg: {
    type: String,
    default: "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
  },
  value: {
    type: [String, Number],
    required: true,
  },
  label: {
    type: String,
    required: true,
  },
  changeText: {
    type: String,
    default: "",
  },
});
</script>

<style scoped lang="scss">
.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  display: flex;
  align-items: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  border: 1px solid #f0f0f0;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.12);
  }

  .stat-icon {
    width: 60px;
    height: 60px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    margin-right: 16px;
  }

  .stat-content {
    flex: 1;

    .stat-value {
      font-size: 24px;
      font-weight: bold;
      color: #303133;
      margin-bottom: 4px;
    }

    .stat-label {
      font-size: 14px;
      color: #909399;
      margin-bottom: 4px;
    }

    .stat-change {
      font-size: 12px;

      .change-text {
        color: #67c23a;
      }
    }
  }
}
</style>
