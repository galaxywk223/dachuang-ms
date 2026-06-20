<template>
  <div class="workflow-graph-shell">
    <div class="graph-hints">
      <span>{{ readonly ? "只读模式" : "拖拽节点调整顺序" }}</span>
      <span>红色端口连接前序节点可设置退回</span>
      <span>Ctrl + 滚轮缩放，拖动画布平移</span>
    </div>
    <div
      ref="container"
      class="workflow-graph-container"
      :class="{ 'is-readonly': readonly }"
      :style="{ height: height ? `${height}px` : '100%' }"
    ></div>
  </div>
</template>

<script setup lang="ts">
import { nextTick, onMounted, onUnmounted, ref, shallowRef, watch } from "vue";
import { Graph, Node } from "@antv/x6";
import { register } from "@antv/x6-vue-shape";
import type { WorkflowNode } from "@/api/system-settings/batch-workflow";
import GraphNode from "./graph/GraphNode.vue";

type RejectLinkPayload = {
  sourceId: number;
  targetId: number | null;
};

type NodeData = WorkflowNode & {
  selected?: boolean;
  readonly?: boolean;
  orderLabel?: string;
};

type X6CellLike = {
  id: string | number;
  getData: () => unknown;
};

type MagnetValidationArgs = {
  magnet: Element;
};

type ConnectionValidationArgs = {
  sourceCell?: X6CellLike | null;
  targetCell?: X6CellLike | null;
  sourcePort?: string | null;
  targetPort?: string | null;
};

type EdgeTerminal = {
  cell?: string | number | null;
};

type EdgeLike = {
  remove: () => void;
  getData?: () => unknown;
  getSource?: () => EdgeTerminal;
  getTarget?: () => EdgeTerminal;
  getSourceCellId?: () => string | number | null;
  getTargetCellId?: () => string | number | null;
};

type EdgeEvent = {
  edge: EdgeLike;
};

type RejectEdgeAttrs = Record<string, unknown> & {
  source?: { cell: string; port: string };
  target?: { cell: string; port: string };
  vertices?: { x: number; y: number }[];
};

type FitGraph = Graph & {
  zoomToFit?: (options: { padding: number; maxScale: number }) => void;
  centerContent?: () => void;
};

register({
  shape: "graph-node",
  width: 248,
  height: 132,
  component: GraphNode,
});

const props = defineProps<{
  nodes: WorkflowNode[];
  height?: number;
  readonly?: boolean;
  selectedNodeId?: number | null;
}>();

const emit = defineEmits<{
  (event: "node-select", node: WorkflowNode): void;
  (event: "node-edit", node: WorkflowNode): void;
  (event: "node-delete", node: WorkflowNode): void;
  (event: "node-reorder", nodeIds: number[]): void;
  (event: "reject-link-change", payload: RejectLinkPayload): void;
}>();

const container = ref<HTMLDivElement>();
const graph = shallowRef<Graph | null>(null);
let rendering = false;
let reorderTimer: ReturnType<typeof setTimeout> | null = null;

const nodeWidth = 248;
const nodeHeight = 132;
const gapX = 128;
const startX = 72;
const startY = 210;

onMounted(() => {
  initGraph();
  renderWorkflow();
  window.addEventListener("resize", resizeGraph);
});

onUnmounted(() => {
  window.removeEventListener("resize", resizeGraph);
  if (reorderTimer) {
    clearTimeout(reorderTimer);
  }
  graph.value?.dispose();
});

watch(
  () => props.nodes,
  () => nextTick(renderWorkflow),
  { deep: true }
);

watch(
  () => props.selectedNodeId,
  () => updateNodeSelection()
);

watch(
  () => props.readonly,
  () => nextTick(renderWorkflow)
);

function initGraph() {
  if (!container.value) return;

  graph.value = new Graph({
    container: container.value,
    width: container.value.clientWidth,
    height: props.height || container.value.clientHeight || 620,
    background: { color: "transparent" },
    grid: {
      size: 18,
      visible: true,
      type: "doubleMesh",
      args: [
        {
          color: "rgba(148, 163, 184, 0.20)",
          thickness: 1,
        },
        {
          color: "rgba(20, 127, 115, 0.10)",
          thickness: 1,
          factor: 5,
        },
      ],
    },
    translating: {
      restrict: false,
    },
    interacting: {
      nodeMovable: !props.readonly,
      edgeMovable: false,
      edgeLabelMovable: false,
    },
    panning: {
      enabled: true,
      eventTypes: ["leftMouseDown", "mouseWheel"],
    },
    mousewheel: {
      enabled: true,
      modifiers: ["ctrl", "meta"],
      minScale: 0.45,
      maxScale: 1.35,
    },
    connecting: {
      router: "manhattan",
      connector: {
        name: "rounded",
        args: { radius: 12 },
      },
      anchor: "center",
      connectionPoint: "boundary",
      allowBlank: false,
      allowLoop: false,
      allowNode: false,
      allowEdge: false,
      allowPort: true,
      allowMulti: false,
      createEdge() {
        return graph.value!.createEdge(rejectEdgeAttrs());
      },
      validateMagnet({ magnet }: MagnetValidationArgs) {
        return !props.readonly && magnet.getAttribute("port-group") === "rejectOut";
      },
      validateConnection({
        sourceCell,
        targetCell,
        sourcePort,
        targetPort,
      }: ConnectionValidationArgs) {
        if (props.readonly) return false;
        if (!sourceCell || !targetCell) return false;
        if (sourceCell.id === targetCell.id) return false;
        if (sourcePort !== "reject-out" || targetPort !== "reject-in") return false;

        const source = sourceCell.getData() as WorkflowNode;
        const target = targetCell.getData() as WorkflowNode;
        if (!source?.can_edit || source.node_type === "SUBMIT") return false;
        return target.sort_order < source.sort_order;
      },
    },
  });

  bindGraphEvents();
}

function bindGraphEvents() {
  const g = graph.value;
  if (!g) return;

  g.on("node:click", ({ node }: { node: Node }) => {
    emit("node-select", node.getData() as WorkflowNode);
  });

  g.on("node:dblclick", ({ node }: { node: Node }) => {
    emit("node-edit", node.getData() as WorkflowNode);
  });

  g.on("node:change:position", () => {
    if (rendering || props.readonly) return;
    scheduleReorder();
  });

  g.on("edge:connected", ({ edge }: EdgeEvent) => {
    const sourceId = parseCellNodeId(edge.getSourceCellId?.() ?? edge.getSource?.()?.cell);
    const targetId = parseCellNodeId(edge.getTargetCellId?.() ?? edge.getTarget?.()?.cell);
    edge.remove();
    if (!sourceId || !targetId) return;
    emit("reject-link-change", { sourceId, targetId });
  });

  g.on("edge:dblclick", ({ edge }: EdgeEvent) => {
    const data = edge.getData?.() as { kind?: string; sourceId?: number } | undefined;
    if (props.readonly || data?.kind !== "reject" || !data.sourceId) return;
    emit("reject-link-change", { sourceId: data.sourceId, targetId: null });
  });
}

function renderWorkflow() {
  const g = graph.value;
  if (!g) return;

  rendering = true;
  g.clearCells();

  const ordered = orderedNodes();
  ordered.forEach((node, index) => {
    g.addNode({
      id: cellNodeId(node.id),
      shape: "graph-node",
      x: startX + index * (nodeWidth + gapX),
      y: startY,
      width: nodeWidth,
      height: nodeHeight,
      data: toNodeData(node, index),
      ports: portConfig(node),
    });
  });

  ordered.forEach((node, index) => {
    if (index > 0) {
      g.addEdge(mainEdgeAttrs(ordered[index - 1].id, node.id));
    }

    const targetId = node.allowed_reject_to;
    const targetIndex = ordered.findIndex((item) => item.id === targetId);
    if (targetId && targetIndex >= 0 && targetIndex < index) {
      g.addEdge(rejectEdgeAttrs(node.id, targetId, index - targetIndex));
    }
  });

  rendering = false;
  updateNodeSelection();
  nextTick(() => fitGraph());
}

function orderedNodes() {
  return [...(props.nodes || [])].sort((a, b) => a.sort_order - b.sort_order || a.id - b.id);
}

function toNodeData(node: WorkflowNode, index: number): NodeData {
  return {
    ...node,
    selected: node.id === props.selectedNodeId,
    readonly: props.readonly,
    orderLabel: `${index + 1}`.padStart(2, "0"),
  };
}

function portConfig(node: WorkflowNode) {
  const editable = !props.readonly && node.can_edit && node.node_type !== "SUBMIT";
  return {
    groups: {
      rejectOut: {
        position: "top",
        attrs: {
          circle: {
            r: 7,
            magnet: editable,
            stroke: editable ? "#ef4444" : "transparent",
            strokeWidth: 2,
            fill: editable ? "#fff1f2" : "transparent",
            cursor: editable ? "crosshair" : "default",
          },
        },
      },
      rejectIn: {
        position: "top",
        attrs: {
          circle: {
            r: 7,
            magnet: !props.readonly,
            stroke: props.readonly ? "transparent" : "#f97316",
            strokeWidth: 2,
            fill: props.readonly ? "transparent" : "#fff7ed",
          },
        },
      },
    },
    items: [
      { id: "reject-out", group: "rejectOut", args: { dx: -46 } },
      { id: "reject-in", group: "rejectIn", args: { dx: 46 } },
    ],
  };
}

function mainEdgeAttrs(sourceId: number, targetId: number) {
  return {
    source: { cell: cellNodeId(sourceId), anchor: "right" },
    target: { cell: cellNodeId(targetId), anchor: "left" },
    router: { name: "manhattan" },
    connector: { name: "rounded", args: { radius: 16 } },
    attrs: {
      line: {
        stroke: "#64748b",
        strokeWidth: 2.8,
        strokeLinecap: "round",
        targetMarker: {
          name: "block",
          width: 12,
          height: 8,
          fill: "#64748b",
        },
      },
    },
    data: { kind: "main" },
    zIndex: 0,
    markup: [
      {
        tagName: "path",
        selector: "line",
      },
    ],
  };
}

function rejectEdgeAttrs(sourceId?: number, targetId?: number, distance = 1) {
  const edge: RejectEdgeAttrs = {
    router: { name: "manhattan" },
    connector: { name: "rounded", args: { radius: 18 } },
    attrs: {
      line: {
        stroke: "#ef4444",
        strokeWidth: 2,
        strokeDasharray: "7 7",
        strokeLinecap: "round",
        targetMarker: {
          name: "classic",
          size: 7,
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
            fontSize: 12,
            fontWeight: 700,
          },
          rect: {
            fill: "#fff",
            stroke: "#fecaca",
            strokeWidth: 1,
            rx: 8,
            ry: 8,
          },
        },
        position: 0.5,
      },
    ],
    data: { kind: "reject", sourceId, targetId },
    zIndex: 2,
  };

  if (sourceId && targetId) {
    const laneY = Math.max(42, startY - 58 - distance * 24);
    const sourceIndex = orderedNodes().findIndex((item) => item.id === sourceId);
    const targetIndex = orderedNodes().findIndex((item) => item.id === targetId);
    edge.source = { cell: cellNodeId(sourceId), port: "reject-out" };
    edge.target = { cell: cellNodeId(targetId), port: "reject-in" };
    if (sourceIndex >= 0 && targetIndex >= 0) {
      edge.vertices = [
        { x: startX + sourceIndex * (nodeWidth + gapX) + nodeWidth / 2, y: laneY },
        { x: startX + targetIndex * (nodeWidth + gapX) + nodeWidth / 2, y: laneY },
      ];
    }
  }

  return edge;
}

function scheduleReorder() {
  if (reorderTimer) clearTimeout(reorderTimer);
  reorderTimer = setTimeout(() => {
    emitOrderFromPositions();
  }, 320);
}

function emitOrderFromPositions() {
  const g = graph.value;
  if (!g || props.readonly) return;

  const currentOrder = orderedNodes().map((node) => node.id);
  const sorted = g
    .getNodes()
    .map((cell) => ({
      id: parseCellNodeId(cell.id),
      x: cell.getPosition().x,
      data: cell.getData() as WorkflowNode,
    }))
    .filter((item): item is { id: number; x: number; data: WorkflowNode } => Boolean(item.id))
    .sort((a, b) => {
      if (a.data.node_type === "SUBMIT") return -1;
      if (b.data.node_type === "SUBMIT") return 1;
      return a.x - b.x;
    })
    .map((item) => item.id);

  if (sorted.length !== currentOrder.length) return;
  if (sorted.every((id, index) => id === currentOrder[index])) return;
  emit("node-reorder", sorted);
}

function updateNodeSelection() {
  const g = graph.value;
  if (!g) return;
  g.getNodes().forEach((cell) => {
    const data = cell.getData() as WorkflowNode;
    cell.setData(
      {
        ...data,
        selected: data.id === props.selectedNodeId,
        readonly: props.readonly,
      },
      { overwrite: false }
    );
  });
}

function resizeGraph() {
  if (!container.value || !graph.value) return;
  graph.value.resize(container.value.clientWidth, props.height || 620);
  fitGraph();
}

function fitGraph() {
  const g = graph.value as FitGraph | null;
  if (!g || !props.nodes.length) return;
  g.zoomToFit?.({ padding: 36, maxScale: 1 });
  g.centerContent?.();
}

function cellNodeId(id: number) {
  return `workflow-node-${id}`;
}

function parseCellNodeId(id?: string | number | null) {
  if (!id) return null;
  const value = String(id).replace("workflow-node-", "");
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}
</script>

<style scoped lang="scss">
.workflow-graph-shell {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-width: 0;
}

.graph-hints {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;

  span {
    padding: 5px 10px;
    border: 1px solid rgba(20, 127, 115, 0.16);
    border-radius: 999px;
    background: rgba(240, 253, 250, 0.86);
    color: #147f73;
    font-size: 12px;
    font-weight: 700;
  }
}

.workflow-graph-container {
  position: relative;
  width: 100%;
  min-height: 460px;
  background:
    radial-gradient(circle at 0% 0%, rgba(20, 127, 115, 0.16), transparent 28%),
    radial-gradient(circle at 100% 10%, rgba(37, 99, 235, 0.14), transparent 30%),
    linear-gradient(145deg, #f8fbfd 0%, #eef6f5 48%, #f8fafc 100%);
  border: 1px solid rgba(148, 163, 184, 0.35);
  border-radius: 22px;
  overflow: hidden;
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.9),
    0 20px 50px rgba(15, 23, 42, 0.08);
  font-family: "IBM Plex Sans", "PingFang SC", "Hiragino Sans GB",
    "Microsoft YaHei", "Noto Sans CJK SC", sans-serif;

  &.is-readonly {
    cursor: grab;
  }

  :deep(.x6-graph) {
    position: relative;
    z-index: 1;
    width: 100%;
    height: 100%;
  }

  :deep(.x6-port-body) {
    transition: r 0.18s ease, stroke-width 0.18s ease, filter 0.18s ease;
  }

  :deep(.x6-port-body:hover) {
    r: 9;
    stroke-width: 3;
    filter: drop-shadow(0 0 8px rgba(239, 68, 68, 0.34));
  }

  :deep(.x6-edge:hover path[selector="line"]) {
    stroke-width: 3;
  }
}
</style>
