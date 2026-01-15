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
      <div v-if="nodeData.start_date || nodeData.end_date" class="node-date">
        {{ formatDateRange(nodeData.start_date, nodeData.end_date) }}
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
  const role = nodeData.value.role;
  if (role === "TEACHER") return User;
  if (role === "LEVEL2_ADMIN") return Management; // School/Management
  if (role === "LEVEL1_ADMIN") return School;
  if (role === "EXPERT") return Avatar;
  return Files;
});

const roleLabel = computed(() => {
  const role = nodeData.value.role_name || nodeData.value.role;
  if (
    nodeData.value.code === "STUDENT_SUBMIT" ||
    (nodeData.value.name && nodeData.value.name.includes("学生"))
  )
    return "学生";
  return role || "未知角色";
});

const roleTagType = computed(() => {
  const role = nodeData.value.role;
  if (role === "TEACHER") return "success";
  if (role === "LEVEL2_ADMIN") return "primary";
  if (role === "LEVEL1_ADMIN") return "danger";
  return "info";
});

const formatDateRange = (start?: string | null, end?: string | null) => {
  if (!start && !end) return "";
  const s = start ? start.substring(5) : "?";
  const e = end ? end.substring(5) : "?";
  return `${s} ~ ${e}`;
};
</script>

<style scoped lang="scss">
.graph-node {
  width: 100%;
  height: 100%;
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1),
    0 2px 4px -1px rgba(0, 0, 0, 0.06);
  border: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: all 0.2s ease;
  user-select: none;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1),
      0 4px 6px -2px rgba(0, 0, 0, 0.05);
  }

  // Type-specific colors styling
  &.type-submit {
    border-left: 4px solid #10b981;
    .node-icon {
      color: #10b981;
      background: #ecfdf5;
    }
  }
  &.type-review {
    border-left: 4px solid #3b82f6;
    .node-icon {
      color: #3b82f6;
      background: #eff6ff;
    }
  }
  &.type-approval {
    border-left: 4px solid #f59e0b;
    .node-icon {
      color: #f59e0b;
      background: #fffbeb;
    }
  }

  .node-header {
    display: flex;
    align-items: center;
    padding: 16px 12px 12px;
    gap: 12px;

    .node-icon {
      width: 36px;
      height: 36px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
      flex-shrink: 0;
    }

    .node-title {
      font-weight: 600;
      color: #334155;
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
    padding: 0 12px 12px;
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

    .node-date {
      font-size: 12px;
      color: #94a3b8;
      background: #f8fafc;
      padding: 2px 6px;
      border-radius: 4px;
      text-align: center;
    }
  }
}
</style>
