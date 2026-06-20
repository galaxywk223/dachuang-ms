<template>
  <div class="metric-card" :class="[tone, `is-${density}`]">
    <div class="metric-topline">
      <span>{{ label }}</span>
      <div v-if="$slots.icon" class="metric-icon">
        <slot name="icon" />
      </div>
    </div>
    <strong>{{ value }}</strong>
    <p v-if="hint">{{ hint }}</p>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    label: string;
    value: string | number;
    hint?: string;
    tone?: "primary" | "success" | "warning" | "info" | "danger";
    density?: "normal" | "compact";
  }>(),
  {
    tone: "primary",
    density: "normal",
  }
);
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.metric-card {
  position: relative;
  min-height: 132px;
  padding: 20px;
  overflow: hidden;
  border: 1px solid $slate-200;
  border-radius: $radius-xl;
  background: #fff;
  box-shadow: $shadow-md;

  &::after {
    position: absolute;
    right: -36px;
    bottom: -48px;
    width: 132px;
    height: 132px;
    content: "";
    border-radius: 50%;
    background: rgba($primary-500, 0.08);
  }

  strong {
    position: relative;
    z-index: 1;
    display: block;
    margin-top: 16px;
    color: $slate-900;
    font-size: 32px;
    font-weight: 850;
    letter-spacing: -0.04em;
  }

  p {
    position: relative;
    z-index: 1;
    margin: 6px 0 0;
    color: $slate-500;
    font-size: 12px;
  }

  &.is-compact {
    min-height: 88px;
    padding: 14px 16px;

    &::after {
      right: -28px;
      bottom: -44px;
      width: 104px;
      height: 104px;
    }

    strong {
      margin-top: 10px;
      font-size: 26px;
    }

    p {
      margin-top: 3px;
      font-size: 12px;
    }
  }
}

.metric-topline {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;

  span {
    color: $slate-500;
    font-size: 13px;
    font-weight: 700;
  }
}

.metric-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: 12px;
  background: $primary-50;
  color: $primary-700;
}

.is-compact {
  .metric-topline {
    gap: 8px;

    span {
      font-size: 12px;
    }
  }

  .metric-icon {
    width: 30px;
    height: 30px;
    border-radius: 10px;
  }
}

.success {
  &::after,
  .metric-icon {
    background: rgba($success, 0.10);
    color: $success;
  }
}

.warning {
  &::after,
  .metric-icon {
    background: rgba($warning, 0.12);
    color: $warning;
  }
}

.info {
  &::after,
  .metric-icon {
    background: rgba($info, 0.10);
    color: $info;
  }
}

.danger {
  &::after,
  .metric-icon {
    background: rgba($danger, 0.10);
    color: $danger;
  }
}
</style>
