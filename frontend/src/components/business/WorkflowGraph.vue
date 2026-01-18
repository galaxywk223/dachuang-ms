<template>
  <div
    ref="container"
    class="workflow-graph-container"
    :style="{ height: height ? `${height}px` : '100%' }"
  ></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick, shallowRef } from "vue";
import { Graph } from "@antv/x6";
import { register } from "@antv/x6-vue-shape";
import type { WorkflowNode } from "@/api/system-settings/batch-workflow";
import GraphNode from "./graph/GraphNode.vue";

// Register custom Vue shape
register({
  shape: "graph-node",
  width: 240,
  height: 125,
  component: GraphNode,
});

const props = defineProps<{
  nodes: WorkflowNode[];
  height?: number;
}>();

const container = ref<HTMLDivElement>();
const graph = shallowRef<Graph | null>(null);

onMounted(() => {
  initGraph();
  renderWorkflow();
});

onUnmounted(() => {
  if (graph.value) {
    graph.value.dispose();
  }
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

  graph.value = new Graph({
    container: container.value,
    width: container.value.clientWidth,
    height: props.height || container.value.clientHeight || 500,
    background: {
      color: "#f8fafc",
    },
    grid: {
      size: 18,
      visible: true,
      type: "dot",
      args: {
        color: "rgba(148, 163, 184, 0.28)",
        thickness: 1,
      },
    },
    interacting: {
      nodeMovable: false,
      edgeLabelMovable: false,
    },
    panning: {
      enabled: false,
    },
    mousewheel: {
      enabled: false,
    },
    connecting: {
      router: "manhattan",
      connector: {
        name: "rounded",
        args: {
          radius: 8,
        },
      },
      anchor: "center",
      connectionPoint: "boundary",
      allowBlank: false,
      allowLoop: false,
      allowNode: false,
      allowEdge: false,
      allowPort: false,
      allowMulti: false,
    },
  });
}

function renderWorkflow() {
  if (!graph.value) return;
  const g = graph.value;

  g.clearCells();

  if (!props.nodes || props.nodes.length === 0) {
    return;
  }

  // Layout configuration
  const nodeWidth = 240;
  const nodeHeight = 125;
  const count = props.nodes.length;
  const containerWidth = container.value?.clientWidth || 900;
  const containerHeight = props.height || container.value?.clientHeight || 500;
  const baseGapX = 170;
  const minGapX = 40;
  const gapX =
    count > 1
      ? Math.min(
          baseGapX,
          Math.max(
            minGapX,
            (containerWidth - nodeWidth * count) / (count - 1)
          )
        )
      : 0;
  const totalWidth = nodeWidth * count + gapX * (count - 1);
  const startX = Math.max(20, (containerWidth - totalWidth) / 2);
  const startY = Math.max(24, containerHeight / 2 - nodeHeight / 2);

  const positions = new Map<number, { x: number; y: number }>();

  // Create Nodes
  props.nodes.forEach((node, index) => {
    const x = startX + index * (nodeWidth + gapX);
    const y = startY;
    positions.set(node.id, { x, y });

    g.addNode({
      id: `node-${node.id}`,
      shape: "graph-node",
      x,
      y,
      width: nodeWidth,
      height: nodeHeight,
      data: node, // Pass data to Vue component
    });

    // Create main flow edges (Success Path)
    if (index > 0) {
      g.addEdge({
        source: `node-${props.nodes[index - 1].id}`,
        target: `node-${node.id}`,
        attrs: {
          line: {
            stroke: "#94a3b8",
            strokeWidth: 2.4,
            strokeLinecap: "round",
            targetMarker: {
              name: "block",
              width: 12,
              height: 8,
              fill: "#94a3b8",
            },
          },
        },
        zIndex: 0,
      });
    }

    // Create Reject/Return Edges
    const targetId = node.allowed_reject_to;
    if (targetId) {
      const targetIndex = props.nodes.findIndex((n) => n.id === targetId);
      // Ensure filtering valid backward links
      if (targetIndex !== -1 && targetIndex < index) {
        const sourcePos = positions.get(node.id);
        const targetPos = positions.get(targetId);
        if (!sourcePos || !targetPos) return;

        const laneIndex = index - targetIndex - 1;
        const laneOffset = 90 + laneIndex * 36;
        const topY = Math.max(24, startY - laneOffset);
        const sourceX = sourcePos.x + nodeWidth / 2;
        const targetX = targetPos.x + nodeWidth / 2;

        g.addEdge({
          source: { cell: `node-${node.id}`, anchor: "top" },
          target: { cell: `node-${targetId}`, anchor: "top" },
          vertices: [
            { x: sourceX, y: topY },
            { x: targetX, y: topY },
          ],
          connector: { name: "rounded", args: { radius: 16 } },
          attrs: {
            line: {
              stroke: "#ef4444",
              strokeWidth: 1.6,
              strokeDasharray: "6 6",
              strokeLinecap: "round",
              targetMarker: {
                name: "classic",
                size: 6,
                fill: "#ef4444",
              },
            },
          },
          labels: [
            {
              attrs: {
                label: {
                  text: "退回",
                  fill: "#ef4444",
                  fontSize: 11,
                  fontWeight: 500,
                },
                rect: {
                  fill: "#fff",
                  stroke: "#ef4444",
                  strokeWidth: 1,
                  rx: 4,
                  ry: 4,
                  refWidth: 10,
                  refHeight: 6,
                },
              },
              position: 0.5,
            },
          ],
          zIndex: 1,
        });
      }
    }
  });

  g.scale(1);
  g.translate(0, 0);
}
</script>

<style scoped lang="scss">
.workflow-graph-container {
  position: relative;
  width: 100%;
  height: 100%;
  background: radial-gradient(
      1200px 600px at -10% -20%,
      rgba(59, 130, 246, 0.12),
      transparent 60%
    ),
    radial-gradient(
      900px 520px at 110% -10%,
      rgba(16, 185, 129, 0.12),
      transparent 55%
    ),
    linear-gradient(180deg, #f8fafc 0%, #eef2f7 100%);
  border-radius: 14px;
  border: 1px solid rgba(148, 163, 184, 0.35);
  overflow: hidden;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.8);
  font-family: "IBM Plex Sans", "PingFang SC", "Hiragino Sans GB",
    "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;

  &::before {
    content: "";
    position: absolute;
    inset: 0;
    background-image: radial-gradient(
      rgba(148, 163, 184, 0.2) 1px,
      transparent 1px
    );
    background-size: 20px 20px;
    opacity: 0.5;
    pointer-events: none;
    z-index: 0;
  }

  :deep(.x6-graph) {
    position: relative;
    z-index: 1;
    width: 100%;
    height: 100%;
  }
}
</style>
