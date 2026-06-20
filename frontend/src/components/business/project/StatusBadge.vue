<template>
  <div class="status-dot">
    <span class="dot" :class="statusClass"></span>
    <span>{{ label }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
  status: string;
  label?: string;
}>();

const label = computed(() => props.label ?? props.status);

const statusClass = computed(() => {
  const status = props.status || "";
  if (status.includes("APPROVED")) return "dot-success";
  if (status.includes("REJECTED")) return "dot-danger";
  if (
    status.includes("REVIEWING") ||
    status.includes("AUDITING") ||
    status === "SUBMITTED"
  ) {
    return "dot-warning";
  }
  return "dot-info";
});
</script>

<style scoped>
.status-dot {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 13px;
}

.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.dot-success {
  background: var(--el-color-success);
  box-shadow: 0 0 0 2px rgba(103, 194, 58, 0.2);
}

.dot-warning {
  background: var(--el-color-warning);
  box-shadow: 0 0 0 2px rgba(230, 162, 60, 0.2);
}

.dot-danger {
  background: var(--el-color-danger);
  box-shadow: 0 0 0 2px rgba(245, 108, 108, 0.2);
}

.dot-info {
  background: var(--el-color-info);
}
</style>
