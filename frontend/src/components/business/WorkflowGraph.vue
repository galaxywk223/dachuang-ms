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
  width: 220,
  height: 110,
  component: GraphNode,
});

const props = defineProps<{
  nodes: WorkflowNode[];
  height?: number;
}>();

const container = ref<HTMLDivElement>();
const graph = shallowRef<Graph | null>(null);
let resizeObserver: ResizeObserver | null = null;

onMounted(() => {
  initGraph();
  if (container.value) {
    resizeObserver = new ResizeObserver(() => {
      if (graph.value && container.value) {
        const width = container.value.clientWidth;
        const height = props.height || 500;
        if (width > 0 && height > 0) {
          graph.value.resize(width, height);
          graph.value.centerContent();
        }
      }
    });
    resizeObserver.observe(container.value);
  }
  renderWorkflow();
});

onUnmounted(() => {
  if (resizeObserver) {
    resizeObserver.disconnect();
  }
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

watch(
  () => props.height,
  (newHeight) => {
    if (graph.value && container.value) {
      graph.value.resize(container.value.clientWidth, newHeight || 500);
      graph.value.centerContent();
    }
  }
);

function initGraph() {
  if (!container.value) return;

  graph.value = new Graph({
    container: container.value,
    width: container.value.clientWidth,
    height: props.height || 500,
    background: {
      color: "#fafafa", // Lighter background
    },
    grid: {
      size: 10,
      visible: true,
      type: "dot",
      args: {
        color: "#e5e7eb",
        thickness: 1,
      },
    },
    interacting: {
      nodeMovable: false,
      edgeLabelMovable: false,
    },
    panning: {
      enabled: true,
      modifiers: undefined,
    },
    mousewheel: {
      enabled: true,
      zoomAtMousePosition: true,
      modifiers: "ctrl",
      minScale: 0.5,
      maxScale: 2,
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
  const nodeWidth = 220;
  const nodeHeight = 110;
  const gapX = 150; // Increased gap from 80 to 150
  const startX = 60;
  const startY = (props.height || 500) / 2 - nodeHeight / 2;

  // Create Nodes
  props.nodes.forEach((node, index) => {
    const x = startX + index * (nodeWidth + gapX);
    const y = startY;

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
            stroke: "#cbd5e1", // Softer gray
            strokeWidth: 2,
            targetMarker: {
              name: "block",
              width: 12,
              height: 8,
              fill: "#cbd5e1",
            },
          },
        },
        zIndex: 0,
      });
    }

    // Create Reject/Return Edges
    const rejectTargets = Array.isArray(node.allowed_reject_to)
      ? node.allowed_reject_to
      : node.allowed_reject_to
      ? [node.allowed_reject_to]
      : [];

    if (rejectTargets.length > 0) {
      rejectTargets.forEach((targetId: number) => {
        const targetIndex = props.nodes.findIndex((n) => n.id === targetId);
        // Ensure filtering valid backward links
        if (targetIndex !== -1 && targetIndex < index) {
          // Calculate curve logic
          g.addEdge({
            source: { cell: `node-${node.id}`, anchor: "top" },
            target: { cell: `node-${targetId}`, anchor: "top" },
            router: {
              name: "metro",
              args: {
                startDirections: ["top"],
                endDirections: ["top"],
                padding: 60 + (index - targetIndex) * 20, // Increased padding/step
              },
            },
            connector: { name: "rounded", args: { radius: 20 } }, // Smoother radius
            attrs: {
              line: {
                stroke: "#f87171", // Softer red
                strokeWidth: 1.5,
                strokeDasharray: "5 5",
                targetMarker: {
                  name: "classic",
                  size: 6,
                  fill: "#f87171",
                },
              },
            },
            labels: [
              {
                attrs: {
                  label: {
                    text: "退回",
                    fill: "#f87171",
                    fontSize: 11,
                    fontWeight: 500,
                  },
                  rect: {
                    fill: "#fff",
                    stroke: "#f87171",
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
      });
    }
  });

  g.centerContent();
}
</script>

<style scoped lang="scss">
.workflow-graph-container {
  width: 100%;
  height: 100%;
  background-color: #fafafa;
  border-radius: 8px;
  overflow: hidden;
}
</style>
