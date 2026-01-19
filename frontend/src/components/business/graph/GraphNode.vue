<template>
  <div class="graph-node" :class="nodeTypeClass">
    <div class="node-header">
      <div class="node-icon">
        <component :is="nodeIcon" />
      </div>
      <div class="node-title">{{ nodeData.name }}</div>
    </div>
    <div class="node-body">
      <div class="node-tags">
        <el-tag
          size="small"
          :type="roleTagType"
          effect="plain"
          class="role-tag"
        >
          {{ roleLabel }}
        </el-tag>
        <el-tag
          v-if="nodeData.require_expert_review"
          size="small"
          type="warning"
          effect="dark"
          class="expert-tag"
        >
          专家评审
        </el-tag>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, inject, onMounted, ref } from "vue";
import type { Node } from "@antv/x6";
import type { WorkflowNode } from "@/api/system-settings/batch-workflow";
import {
  Document,
  Files,
  Check,
  User,
  School,
  Avatar,
  Management,
} from "@element-plus/icons-vue";

type NodeData = Partial<WorkflowNode>;

// Inject 'getNode' from x6-vue-shape
const getNode = inject<() => Node>("getNode");

const nodeData = ref<NodeData>({});

const toNodeData = (data: unknown): NodeData => {
  if (data && typeof data === "object") {
    return data as NodeData;
  }
  return {};
};

onMounted(() => {
  const node = getNode?.();
  if (!node) return;

  nodeData.value = toNodeData(node.getData());

  // Listen for data changes if needed
  node.on("change:data", ({ current }: { current: unknown }) => {
    nodeData.value = toNodeData(current);
  });
});

const nodeTypeClass = computed(() => {
  const type = nodeData.value.node_type || "REVIEW";
  return `type-${type.toLowerCase()}`;
});

const nodeIcon = computed(() => {
  const type = nodeData.value.node_type;
  if (type === "SUBMIT") return Document;
  if (type === "APPROVAL") return Check;
  // Default to REVIEW, vary by role if possible
  const role = nodeData.value.role_code;
  if (role === "TEACHER") return User;
  if (role === "LEVEL2_ADMIN") return Management; // School/Management
  if (role === "LEVEL1_ADMIN") return School;
  if (role === "EXPERT") return Avatar;
  return Files;
});

const roleLabel = computed(() => {
  const role = nodeData.value.role_name || nodeData.value.role_code;
  if (
    nodeData.value.code === "STUDENT_SUBMIT" ||
    (nodeData.value.name && nodeData.value.name.includes("学生"))
  )
    return "学生";
  return role || "未知角色";
});

const roleTagType = computed(() => {
  const role = nodeData.value.role_code;
  if (role === "TEACHER") return "success";
  if (role === "LEVEL2_ADMIN") return "primary";
  if (role === "LEVEL1_ADMIN") return "danger";
  return "info";
});

</script>

<style scoped lang="scss">
.graph-node {
  --node-accent: #2563eb;
  --node-accent-soft: rgba(37, 99, 235, 0.18);
  --node-ink: #0f172a;

  position: relative;
  width: 100%;
  height: 100%;
  background: linear-gradient(145deg, #ffffff 0%, #f8fafc 65%, #f1f5f9 100%);
  border-radius: 14px;
  box-shadow: 0 14px 28px rgba(15, 23, 42, 0.08),
    0 4px 10px rgba(15, 23, 42, 0.06);
  border: 1px solid rgba(148, 163, 184, 0.4);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: box-shadow 0.2s ease, border-color 0.2s ease;
  user-select: none;
  font-family: "IBM Plex Sans", "PingFang SC", "Hiragino Sans GB",
    "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;

  &:hover {
    border-color: rgba(59, 130, 246, 0.35);
    box-shadow: 0 20px 38px rgba(15, 23, 42, 0.12),
      0 8px 18px rgba(15, 23, 42, 0.08);
  }

  &::before {
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 6px;
    background: linear-gradient(180deg, var(--node-accent), transparent);
    opacity: 0.9;
  }

  &::after {
    content: "";
    position: absolute;
    left: 6px;
    right: 0;
    top: 0;
    height: 3px;
    background: linear-gradient(
      90deg,
      rgba(15, 23, 42, 0.08),
      transparent 60%
    );
  }

  // Type-specific colors styling
  &.type-submit {
    --node-accent: #16a34a;
    --node-accent-soft: rgba(22, 163, 74, 0.18);
    .node-icon {
      color: #16a34a;
    }
  }
  &.type-review {
    --node-accent: #2563eb;
    --node-accent-soft: rgba(37, 99, 235, 0.2);
    .node-icon {
      color: #2563eb;
    }
  }
  &.type-approval {
    --node-accent: #f59e0b;
    --node-accent-soft: rgba(245, 158, 11, 0.2);
    .node-icon {
      color: #f59e0b;
    }
  }

  .node-header {
    display: flex;
    align-items: center;
    padding: 18px 16px 12px 18px;
    gap: 14px;

    .node-icon {
      width: 40px;
      height: 40px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
      flex-shrink: 0;
      background: linear-gradient(
        140deg,
        var(--node-accent-soft),
        rgba(255, 255, 255, 0.95)
      );
      box-shadow: inset 0 0 0 1px rgba(148, 163, 184, 0.3),
        0 10px 20px rgba(15, 23, 42, 0.08);
    }

    .node-title {
      font-weight: 600;
      color: #1f2937;
      font-size: 15px;
      line-height: 1.4;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }
  }

  .node-body {
    padding: 0 16px 14px 18px;
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    gap: 8px;

    .node-tags {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }

  }

  .role-tag {
    border-radius: 999px;
    padding: 1px 10px;
    font-weight: 600;
    letter-spacing: 0.2px;
  }

  .expert-tag {
    border-radius: 999px;
    padding: 1px 10px;
  }
}

</style>
