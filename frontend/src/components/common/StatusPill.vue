<template>
  <span class="status-pill" :class="tone">
    <i />
    {{ label || status || "-" }}
  </span>
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
  status?: string;
  label?: string;
}>();

const tone = computed(() => {
  const status = props.status || "";
  if (["SUCCESS", "PUBLISHED", "APPROVED", "COMPLETED", "CLOSED"].some((key) => status.includes(key))) {
    return "success";
  }
  if (["FAILED", "REJECTED", "RETURNED"].some((key) => status.includes(key))) {
    return "danger";
  }
  if (["RUNNING", "REVIEWING", "AUDITING", "SUBMITTED", "CONFIRMED", "RECOMMENDED"].some((key) => status.includes(key))) {
    return "warning";
  }
  return "info";
});
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  min-height: 26px;
  padding: 4px 10px;
  border-radius: 999px;
  background: $slate-100;
  color: $slate-600;
  font-size: 12px;
  font-weight: 800;

  i {
    width: 7px;
    height: 7px;
    border-radius: 999px;
    background: currentColor;
  }
}

.success {
  background: rgba($success, 0.10);
  color: $success;
}

.danger {
  background: rgba($danger, 0.10);
  color: $danger;
}

.warning {
  background: rgba($warning, 0.14);
  color: #b45309;
}

.info {
  background: rgba($info, 0.10);
  color: $info;
}
</style>
