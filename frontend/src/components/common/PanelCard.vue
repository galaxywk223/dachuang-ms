<template>
  <el-card class="panel-card" shadow="never">
    <template v-if="title || caption || $slots.actions || $slots.header" #header>
      <slot name="header">
        <div
          class="panel-header"
          :class="{ 'is-actions-only': !title && !caption }"
        >
          <div v-if="title || caption" class="panel-copy">
            <h3 v-if="title" class="panel-title">{{ title }}</h3>
            <p v-if="caption">{{ caption }}</p>
          </div>
          <div v-if="$slots.actions" class="panel-actions">
            <slot name="actions" />
          </div>
        </div>
      </slot>
    </template>
    <slot />
  </el-card>
</template>

<script setup lang="ts">
defineProps<{
  title?: string;
  caption?: string;
}>();
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.panel-card {
  overflow: hidden;
  border: 1px solid rgba($slate-200, 0.95);
  border-radius: $radius-xl;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: $shadow-md;

  :deep(.el-card__header) {
    padding: 18px 20px;
    border-bottom: 1px solid $slate-100;
    background: linear-gradient(180deg, #ffffff 0%, #fbfdff 100%);
  }

  :deep(.el-card__body) {
    padding: 20px;
  }
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;

  &.is-actions-only {
    justify-content: flex-end;
  }

  .panel-title {
    display: flex;
    align-items: center;
    margin: 0;
    color: $slate-900;
    font-size: 16px;
    font-weight: 800;

    &::before {
      content: "";
      display: inline-block;
      width: 4px;
      height: 18px;
      margin-right: 12px;
      border-radius: 2px;
      background: $primary-600;
    }
  }

  p {
    margin: 4px 0 0;
    color: $slate-500;
    font-size: 13px;
  }
}

.panel-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}
</style>
