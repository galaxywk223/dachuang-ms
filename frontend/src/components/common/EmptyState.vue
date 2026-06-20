<template>
  <div class="empty-state">
    <div class="empty-mark">{{ mark }}</div>
    <strong>{{ title }}</strong>
    <p v-if="description">{{ description }}</p>
    <slot />
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    title: string;
    description?: string;
    mark?: string;
  }>(),
  {
    mark: "—",
  }
);
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.empty-state {
  display: flex;
  align-items: center;
  flex-direction: column;
  justify-content: center;
  min-height: 220px;
  padding: 34px;
  border: 1px dashed $slate-200;
  border-radius: $radius-xl;
  background: linear-gradient(180deg, #fff 0%, #f8fafc 100%);
  color: $slate-500;
  text-align: center;

  strong {
    margin-top: 12px;
    color: $slate-800;
    font-size: 16px;
  }

  p {
    max-width: 360px;
    margin: 6px 0 0;
    font-size: 13px;
  }
}

.empty-mark {
  display: grid;
  width: 54px;
  height: 54px;
  place-items: center;
  border-radius: 18px;
  background: $primary-50;
  color: $primary-700;
  font-size: 26px;
  font-weight: 900;
}
</style>
