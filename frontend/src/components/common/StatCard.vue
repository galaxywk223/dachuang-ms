<template>
  <div class="stat-card">
    <div class="stat-icon-wrapper" :style="{ background: iconBg }">
      <component :is="icon" :size="24" class="stat-icon" />
    </div>
    <div class="stat-content">
      <div class="stat-value">{{ value }}</div>
      <div class="stat-label">{{ label }}</div>
    </div>
    <div class="stat-decoration"></div>
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
});
</script>

<style scoped lang="scss">
.stat-card {
  position: relative;
  background: white;
  border-radius: 20px;
  padding: 24px;
  display: flex;
  align-items: flex-start;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid rgba(0, 0, 0, 0.02);
  overflow: hidden;
  height: 100%;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.08);

    .stat-decoration {
      transform: scale(1.5);
      opacity: 0.1;
    }
  }

  .stat-icon-wrapper {
    width: 48px;
    height: 48px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    margin-right: 16px;
    flex-shrink: 0;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    z-index: 1;
  }

  .stat-icon {
    width: 24px;
    height: 24px;
  }

  .stat-content {
    flex: 1;
    z-index: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    height: 48px;

    .stat-value {
      font-size: 28px;
      font-weight: 700;
      color: #1a1a1a;
      line-height: 1.2;
      font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    .stat-label {
      font-size: 13px;
      color: #8c8c8c;
      margin-top: 4px;
      font-weight: 500;
    }
  }

  .stat-decoration {
    position: absolute;
    top: -20px;
    right: -20px;
    width: 100px;
    height: 100px;
    background: currentColor;
    border-radius: 50%;
    opacity: 0;
    transition: all 0.5s ease;
    pointer-events: none;
  }
}
</style>
