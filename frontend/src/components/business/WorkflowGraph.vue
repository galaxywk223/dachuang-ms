<template>
  <div ref="container" class="workflow-graph-container"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from "vue";
import { Graph, Node, Edge } from "@antv/x6";
import type { WorkflowNode } from "@/api/system-settings/batch-workflow";

const props = defineProps<{
  nodes: WorkflowNode[];
  height?: number;
}>();

const container = ref<HTMLDivElement>();
let graph: Graph | null = null;

const NODE_TYPE_COLORS = {
  SUBMIT: "#52c41a",
  REVIEW: "#1890ff",
  APPROVAL: "#fa8c16",
};

const NODE_TYPE_NAMES = {
  SUBMIT: "提交",
  REVIEW: "审核",
  APPROVAL: "确认",
};

onMounted(() => {
  initGraph();
  renderWorkflow();
});

watch(
  () => props.nodes,
  () => {
    nextTick(() => {
      renderWorkflow();
    });
  },
  { deep: true }
);

function initGraph() {
  if (!container.value) return;

  graph = new Graph({
    container: container.value,
    width: container.value.clientWidth,
    height: props.height || 400,
    background: {
      color: "#f5f5f5",
    },
    grid: {
      size: 10,
      visible: true,
      type: "dot",
      args: {
        color: "#d0d0d0",
        thickness: 1,
      },
    },
    interacting: false, // 禁用交互
    panning: true, // 允许平移
    mousewheel: {
      enabled: true,
      modifiers: "ctrl",
    },
  });
}

function renderWorkflow() {
  if (!graph) return;

  graph.clearCells();

  if (!props.nodes || props.nodes.length === 0) {
    return;
  }

  const nodeSpacing = 150;
  const nodeHeight = 60;
  const startX = 50;
  const startY = 50;

  const graphNodes: Node[] = [];
  const graphEdges: Edge[] = [];

  // 创建节点
  props.nodes.forEach((node, index) => {
    const x = startX + index * nodeSpacing;
    const y = startY;
    const isExpertRequired = Boolean(node.require_expert_review);
    const typeName = NODE_TYPE_NAMES[node.node_type] || node.node_type;
    const labelSuffix = isExpertRequired ? `${typeName}+专家` : typeName;

    const graphNode = graph!.addNode({
      id: `node-${node.id}`,
      shape: "rect",
      x,
      y,
      width: 120,
      height: nodeHeight,
      attrs: {
        body: {
          fill: NODE_TYPE_COLORS[node.node_type] || "#1890ff",
          stroke: isExpertRequired ? "#faad14" : "#5c7bd9",
          strokeWidth: 2,
          rx: 6,
          ry: 6,
        },
        label: {
          text: `${node.name}\n(${labelSuffix})`,
          fill: "#ffffff",
          fontSize: 12,
          textWrap: {
            width: 100,
            height: 50,
            ellipsis: true,
          },
        },
      },
      data: node,
    });

    graphNodes.push(graphNode);

    // 创建主流程连线
    if (index > 0) {
      const edge = graph!.addEdge({
        source: `node-${props.nodes[index - 1].id}`,
        target: `node-${node.id}`,
        attrs: {
          line: {
            stroke: "#5c7bd9",
            strokeWidth: 2,
            targetMarker: {
              name: "classic",
              size: 8,
            },
          },
        },
        labels: [
          {
            attrs: {
              label: {
                text: "通过",
                fill: "#5c7bd9",
                fontSize: 11,
              },
              rect: {
                fill: "#ffffff",
                stroke: "#5c7bd9",
                strokeWidth: 1,
                rx: 3,
                ry: 3,
              },
            },
            position: 0.5,
          },
        ],
      });
      graphEdges.push(edge);
    }

    // 创建退回连线
    const rejectTargets = Array.isArray(node.allowed_reject_to)
      ? node.allowed_reject_to
      : node.allowed_reject_to
      ? [node.allowed_reject_to]
      : [];
    if (rejectTargets.length > 0) {
      rejectTargets.forEach((targetId: number) => {
        const targetIndex = props.nodes.findIndex((n) => n.id === targetId);
        if (targetIndex !== -1 && targetIndex < index) {
          graph!.addEdge({
            source: `node-${node.id}`,
            target: `node-${targetId}`,
            attrs: {
              line: {
                stroke: "#ff4d4f",
                strokeWidth: 1.5,
                strokeDasharray: "5 5",
                targetMarker: {
                  name: "classic",
                  size: 6,
                },
              },
            },
            labels: [
              {
                attrs: {
                  label: {
                    text: "退回",
                    fill: "#ff4d4f",
                    fontSize: 10,
                  },
                  rect: {
                    fill: "#ffffff",
                    stroke: "#ff4d4f",
                    strokeWidth: 1,
                    rx: 3,
                    ry: 3,
                  },
                },
                position: 0.3,
              },
            ],
            router: {
              name: "manhattan",
              args: {
                padding: 10,
              },
            },
            connector: {
              name: "rounded",
            },
          });
        }
      });
    }
  });

  // 自动居中
  graph.centerContent();
}
</script>

<style scoped lang="scss">
.workflow-graph-container {
  width: 100%;
  height: 100%;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  overflow: hidden;
}
</style>
