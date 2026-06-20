<template>
  <div class="batch-workflow-config">
    <div class="workflow-topbar">
      <el-tabs v-model="activePhase" class="phase-tabs" @tab-change="handlePhaseChange">
        <el-tab-pane label="立项流程" name="APPLICATION" />
        <el-tab-pane label="中期流程" name="MID_TERM" />
        <el-tab-pane label="结题流程" name="CLOSURE" />
        <el-tab-pane label="经费流程" name="BUDGET" />
        <el-tab-pane label="异动流程" name="CHANGE" />
      </el-tabs>

      <div v-if="workflow" class="topbar-actions">
        <el-tag :type="workflow.is_locked ? 'info' : 'success'" effect="light">
          {{ workflow.is_locked ? "只读配置" : "可编辑配置" }}
        </el-tag>
        <el-tag :type="validationErrors.length ? 'warning' : 'success'" effect="light">
          {{ validationErrors.length ? `${validationErrors.length} 个问题` : "校验通过" }}
        </el-tag>
        <el-button @click="loadWorkflow">刷新</el-button>
        <el-button @click="handleValidate">
          <el-icon><CircleCheck /></el-icon>
          验证流程
        </el-button>
        <el-button @click="openFullscreenGraph">
          <el-icon><FullScreen /></el-icon>
          全屏画布
        </el-button>
        <el-button v-if="!workflow.is_locked" type="primary" @click="handleAddNode">
          <el-icon><Plus /></el-icon>
          添加节点
        </el-button>
      </div>
    </div>

    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="7" animated />
    </div>

    <template v-else>
      <el-empty
        v-if="!workflow"
        description="该阶段尚未配置工作流"
        class="workflow-empty"
      >
        <el-button type="primary" @click="handleInitWorkflow">
          初始化默认流程
        </el-button>
      </el-empty>

      <div v-else class="workflow-workbench">
        <div v-if="validationErrors.length" class="validation-panel">
          <div class="validation-title">流程配置存在问题</div>
          <ul>
            <li v-for="(error, index) in validationErrors" :key="index">
              {{ error }}
            </li>
          </ul>
        </div>

        <section class="canvas-panel">
          <div class="canvas-heading">
            <div>
              <span class="header-title">{{ workflow.name }}</span>
              <p>
                主流程按节点顺序推进；红色退回线表示审核驳回时可退回的前序节点。
              </p>
            </div>
            <div class="canvas-stats">
              <span>{{ nodes.length }} 个节点</span>
              <span>{{ rejectEdgeCount }} 条退回线</span>
            </div>
          </div>

          <WorkflowGraph
            :nodes="nodes"
            :height="620"
            :readonly="workflow.is_locked || savingGraph"
            :selected-node-id="selectedNodeId"
            @node-select="handleSelectNode"
            @node-edit="handleSelectNode"
            @node-delete="handleDeleteNode"
            @node-reorder="handleNodeReorder"
            @reject-link-change="handleRejectLinkChange"
          />

          <div class="legend">
            <span><i class="dot submit"></i>提交节点</span>
            <span><i class="dot review"></i>审核节点</span>
            <span><i class="dot approval"></i>确认节点</span>
            <span><i class="line reject"></i>退回线，双击可删除</span>
          </div>
        </section>

        <aside class="inspector-panel">
          <div class="inspector-card">
            <div class="inspector-title">
              <span>节点属性</span>
              <el-tag v-if="selectedNode" size="small" effect="plain">
                第 {{ selectedNode.sort_order + 1 }} 步
              </el-tag>
            </div>

            <el-empty
              v-if="!selectedNode"
              description="选择画布中的节点后编辑属性"
              class="inspector-empty"
            />

            <template v-else>
              <el-form
                ref="selectedFormRef"
                :model="selectedForm"
                :rules="nodeRules"
                label-position="top"
                class="node-form"
              >
                <el-form-item label="节点名称" prop="name">
                  <el-input
                    v-model="selectedForm.name"
                    :disabled="!canEditSelected"
                    placeholder="请输入节点名称"
                  />
                </el-form-item>
                <el-form-item label="执行角色" prop="role_fk">
                  <el-select
                    v-model="selectedForm.role_fk"
                    :disabled="!canEditSelected"
                    placeholder="选择角色"
                    filterable
                    class="w-full"
                  >
                    <el-option
                      v-for="role in availableRoles"
                      :key="role.id"
                      :label="role.name"
                      :value="role.id"
                      :disabled="role.code === 'STUDENT'"
                    />
                  </el-select>
                </el-form-item>
                <el-form-item label="专家评审">
                  <el-switch
                    v-model="selectedForm.require_expert_review"
                    :disabled="!canEditSelected || !canEnableSelectedExpertReview"
                  />
                  <div class="form-hint">仅管理员节点可开启专家评审。</div>
                </el-form-item>
                <el-form-item label="允许退回">
                  <el-select
                    v-model="selectedForm.allowed_reject_to"
                    :disabled="!canEditSelected"
                    placeholder="无退回目标"
                    clearable
                    class="w-full"
                  >
                    <el-option
                      v-for="node in selectedRejectTargets"
                      :key="node.id"
                      :label="node.name"
                      :value="node.id"
                    />
                  </el-select>
                </el-form-item>
                <el-form-item label="审核注意事项">
                  <el-input
                    v-model="selectedForm.notice"
                    :disabled="!canEditSelected"
                    type="textarea"
                    :rows="4"
                    placeholder="可填写该节点处理提示"
                  />
                </el-form-item>
              </el-form>

              <div class="inspector-actions">
                <el-button
                  type="primary"
                  :disabled="!canEditSelected"
                  :loading="savingNode"
                  @click="handleSaveSelectedNode"
                >
                  保存属性
                </el-button>
                <el-button
                  type="danger"
                  plain
                  :disabled="!canEditSelected"
                  @click="handleDeleteNode(selectedNode)"
                >
                  删除节点
                </el-button>
              </div>
            </template>
          </div>

          <div class="node-list-card">
            <div class="inspector-title">
              <span>节点清单</span>
              <span class="muted">按画布顺序推进</span>
            </div>
            <button
              v-for="node in sortedNodes"
              :key="node.id"
              type="button"
              class="node-list-item"
              :class="{ active: node.id === selectedNodeId }"
              @click="handleSelectNode(node)"
            >
              <span class="node-index">{{ node.sort_order + 1 }}</span>
              <span class="node-copy">
                <strong>{{ node.name }}</strong>
                <small>{{ node.role_name || roleLabel(node) }}</small>
              </span>
              <el-tag
                v-if="node.allowed_reject_to"
                type="danger"
                size="small"
                effect="plain"
              >
                可退回
              </el-tag>
            </button>
          </div>
        </aside>
      </div>
    </template>

    <el-dialog
      v-model="nodeDialogVisible"
      title="新增流程节点"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="nodeRules"
        label-width="120px"
      >
        <el-form-item label="节点名称" prop="name">
          <el-input v-model="createForm.name" placeholder="如：学院审核" />
        </el-form-item>
        <el-form-item label="执行角色" prop="role_fk">
          <el-select v-model="createForm.role_fk" placeholder="选择角色" filterable>
            <el-option
              v-for="role in availableRoles"
              :key="role.id"
              :label="role.name"
              :value="role.id"
              :disabled="role.code === 'STUDENT'"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="专家评审">
          <el-switch
            v-model="createForm.require_expert_review"
            :disabled="!canEnableCreateExpertReview"
          />
          <div class="form-hint">仅管理员节点可开启，开启后需先完成专家评审再终审。</div>
        </el-form-item>
        <el-form-item label="允许退回">
          <el-select
            v-model="createForm.allowed_reject_to"
            placeholder="选择可退回的节点"
            clearable
          >
            <el-option
              v-for="node in sortedNodes"
              :key="node.id"
              :label="node.name"
              :value="node.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="审核注意事项">
          <el-input
            v-model="createForm.notice"
            type="textarea"
            :rows="3"
            placeholder="可选"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="nodeDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="savingNode" @click="handleCreateNode">
          创建节点
        </el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="graphFullscreenVisible"
      title="流程画布"
      fullscreen
      append-to-body
      destroy-on-close
      class="graph-fullscreen-dialog"
      @opened="handleFullscreenOpened"
      @closed="handleFullscreenClosed"
    >
      <div v-if="fullscreenGraphReady" class="fullscreen-graph-container">
        <WorkflowGraph
          :nodes="nodes"
          :height="fullscreenHeight"
          :readonly="Boolean(workflow?.is_locked) || savingGraph"
          :selected-node-id="selectedNodeId"
          @node-select="handleSelectNode"
          @node-edit="handleSelectNode"
          @node-delete="handleDeleteNode"
          @node-reorder="handleNodeReorder"
          @reject-link-change="handleRejectLinkChange"
        />
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import {
  ElMessage,
  ElMessageBox,
  type FormInstance,
  type FormRules,
} from "element-plus";
import { CircleCheck, FullScreen, Plus } from "@element-plus/icons-vue";
import WorkflowGraph from "@/components/business/WorkflowGraph.vue";
import {
  createWorkflowNode,
  deleteWorkflowNode,
  getBatchWorkflow,
  initBatchWorkflow,
  reorderWorkflowNodes,
  updateWorkflowNode,
  validateBatchWorkflow,
  type WorkflowConfig,
  type WorkflowNode,
  type WorkflowNodeInput,
} from "@/api/system-settings/batch-workflow";
import { getRoles } from "@/api/users/roles";

const props = defineProps<{
  batchId: number;
}>();

type Phase = "APPLICATION" | "MID_TERM" | "CLOSURE" | "BUDGET" | "CHANGE";
type Role = {
  id: number;
  name: string;
  code?: string;
};
type ValidationResult = {
  valid: boolean;
  errors: string[];
};

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null;

const activePhase = ref<Phase>("APPLICATION");
const loading = ref(false);
const savingGraph = ref(false);
const savingNode = ref(false);
const workflow = ref<WorkflowConfig | null>(null);
const nodes = ref<WorkflowNode[]>([]);
const validationErrors = ref<string[]>([]);
const availableRoles = ref<Role[]>([]);
const selectedNodeId = ref<number | null>(null);

const nodeDialogVisible = ref(false);
const createFormRef = ref<FormInstance>();
const selectedFormRef = ref<FormInstance>();

const graphFullscreenVisible = ref(false);
const fullscreenGraphReady = ref(false);
const fullscreenHeight = ref(window.innerHeight - 120);

const emptyNodeForm = (): WorkflowNodeInput => ({
  code: "",
  name: "",
  node_type: "REVIEW",
  role_fk: undefined,
  require_expert_review: false,
  return_policy: "NONE",
  allowed_reject_to: null,
  notice: "",
  sort_order: nodes.value.length,
  is_active: true,
});

const createForm = ref<WorkflowNodeInput>(emptyNodeForm());
const selectedForm = ref<WorkflowNodeInput>(emptyNodeForm());

const nodeRules: FormRules = {
  name: [{ required: true, message: "请输入节点名称", trigger: "blur" }],
  role_fk: [{ required: true, message: "请选择执行角色", trigger: "change" }],
};

const roleMap = computed(() => {
  const map = new Map<number, Role>();
  availableRoles.value.forEach((role) => map.set(role.id, role));
  return map;
});

const sortedNodes = computed(() =>
  [...nodes.value].sort((a, b) => a.sort_order - b.sort_order || a.id - b.id)
);

const selectedNode = computed(() =>
  sortedNodes.value.find((node) => node.id === selectedNodeId.value) || null
);

const canEditSelected = computed(
  () => Boolean(selectedNode.value?.can_edit) && !workflow.value?.is_locked
);

const selectedRejectTargets = computed(() => {
  if (!selectedNode.value) return [];
  return sortedNodes.value.filter(
    (node) => node.sort_order < selectedNode.value!.sort_order
  );
});

const rejectEdgeCount = computed(
  () => sortedNodes.value.filter((node) => node.allowed_reject_to).length
);

const canEnableSelectedExpertReview = computed(() =>
  canEnableExpertReview(selectedForm.value.role_fk)
);

const canEnableCreateExpertReview = computed(() =>
  canEnableExpertReview(createForm.value.role_fk)
);

onMounted(() => {
  loadRoles();
  loadWorkflow();
});

watch(
  () => selectedNode.value,
  (node) => {
    if (node) {
      selectedForm.value = toNodeForm(node);
    }
  },
  { immediate: true }
);

watch(
  () => selectedForm.value.role_fk,
  () => {
    if (!canEnableSelectedExpertReview.value) {
      selectedForm.value.require_expert_review = false;
    }
  }
);

watch(
  () => createForm.value.role_fk,
  () => {
    if (!canEnableCreateExpertReview.value) {
      createForm.value.require_expert_review = false;
    }
  }
);

async function loadRoles() {
  try {
    const res = await getRoles();
    const payload = isRecord(res) && "data" in res ? res.data : res;
    if (isRecord(payload) && Array.isArray(payload.results)) {
      availableRoles.value = payload.results as Role[];
    } else if (Array.isArray(payload)) {
      availableRoles.value = payload as Role[];
    } else {
      availableRoles.value = [];
    }
  } catch {
    ElMessage.error("加载角色列表失败");
  }
}

async function loadWorkflow() {
  loading.value = true;
  try {
    const res = (await getBatchWorkflow(
      props.batchId,
      activePhase.value
    )) as unknown as WorkflowConfig;
    workflow.value = res;
    nodes.value = normalizeNodes(res.nodes || []);
    ensureSelectedNode();
    await handleValidate(false);
  } catch (error: unknown) {
    const response = isRecord(error) ? error.response : null;
    const status = isRecord(response) ? response.status : null;
    if (status === 404) {
      workflow.value = null;
      nodes.value = [];
      selectedNodeId.value = null;
      validationErrors.value = [];
    } else {
      ElMessage.error("加载工作流失败");
    }
  } finally {
    loading.value = false;
  }
}

function handlePhaseChange() {
  selectedNodeId.value = null;
  loadWorkflow();
}

async function handleInitWorkflow() {
  try {
    await ElMessageBox.confirm(
      "将为该阶段初始化默认工作流配置，是否继续？",
      "确认初始化",
      { type: "warning" }
    );

    loading.value = true;
    await initBatchWorkflow(props.batchId, activePhase.value);
    ElMessage.success("初始化成功");
    await loadWorkflow();
  } catch (error: unknown) {
    if (error !== "cancel") {
      const response = isRecord(error) ? error.response : null;
      const data = isRecord(response) ? response.data : null;
      const detail =
        isRecord(data) && typeof data.detail === "string"
          ? data.detail
          : "初始化失败";
      ElMessage.error(detail);
    }
  } finally {
    loading.value = false;
  }
}

function handleSelectNode(node: WorkflowNode) {
  selectedNodeId.value = node.id;
}

function handleAddNode() {
  createForm.value = {
    ...emptyNodeForm(),
    sort_order: sortedNodes.value.length,
  };
  nodeDialogVisible.value = true;
}

async function handleCreateNode() {
  if (!createFormRef.value) return;
  await createFormRef.value.validate();

  savingNode.value = true;
  try {
    const timestamp = Date.now().toString().slice(-6);
    const created = (await createWorkflowNode(props.batchId, activePhase.value, {
      ...createForm.value,
      code: `REVIEW_${timestamp}`,
      sort_order: sortedNodes.value.length,
      allowed_reject_to: createForm.value.allowed_reject_to ?? null,
    })) as unknown as WorkflowNode;
    nodeDialogVisible.value = false;
    ElMessage.success("创建成功");
    await loadWorkflow();
    selectedNodeId.value = created.id;
  } catch {
    ElMessage.error("创建失败");
  } finally {
    savingNode.value = false;
  }
}

async function handleSaveSelectedNode() {
  if (!selectedNode.value || !selectedFormRef.value || !canEditSelected.value) return;
  await selectedFormRef.value.validate();

  savingNode.value = true;
  try {
    await updateWorkflowNode(
      props.batchId,
      activePhase.value,
      selectedNode.value.id,
      {
        ...selectedForm.value,
        allowed_reject_to: selectedForm.value.allowed_reject_to ?? null,
      }
    );
    ElMessage.success("节点属性已保存");
    const id = selectedNode.value.id;
    await loadWorkflow();
    selectedNodeId.value = id;
  } catch {
    ElMessage.error("保存失败");
  } finally {
    savingNode.value = false;
  }
}

async function handleDeleteNode(node?: WorkflowNode) {
  const target = node || selectedNode.value;
  if (!target || !target.can_edit || workflow.value?.is_locked) return;

  try {
    await ElMessageBox.confirm(`确定要删除节点"${target.name}"吗？`, "确认删除", {
      type: "warning",
    });
    await deleteWorkflowNode(props.batchId, activePhase.value, target.id);
    ElMessage.success("删除成功");
    selectedNodeId.value = null;
    await loadWorkflow();
  } catch (error: unknown) {
    if (error !== "cancel") {
      ElMessage.error("删除失败");
    }
  }
}

async function handleNodeReorder(nodeIds: number[]) {
  if (workflow.value?.is_locked || savingGraph.value) return;
  const currentIds = sortedNodes.value.map((node) => node.id);
  if (sameIds(nodeIds, currentIds)) return;

  savingGraph.value = true;
  const before = nodes.value;
  nodes.value = applyLocalOrder(nodeIds);
  try {
    const res = (await reorderWorkflowNodes(
      props.batchId,
      activePhase.value,
      nodeIds
    )) as unknown as WorkflowNode[];
    nodes.value = normalizeNodes(res);
    ElMessage.success("流程顺序已保存");
    await handleValidate(false);
  } catch (error: unknown) {
    nodes.value = before;
    await loadWorkflow();
    showBackendError(error, "排序保存失败，已恢复原顺序");
  } finally {
    savingGraph.value = false;
  }
}

async function handleRejectLinkChange(payload: {
  sourceId: number;
  targetId: number | null;
}) {
  if (workflow.value?.is_locked || savingGraph.value) return;

  const source = sortedNodes.value.find((node) => node.id === payload.sourceId);
  const target = sortedNodes.value.find((node) => node.id === payload.targetId);
  if (!source || !source.can_edit || source.node_type === "SUBMIT") {
    ElMessage.warning("该节点不能设置退回线");
    return;
  }
  if (target && target.sort_order >= source.sort_order) {
    ElMessage.warning("退回目标必须是前序节点");
    return;
  }

  savingGraph.value = true;
  try {
    await updateWorkflowNode(props.batchId, activePhase.value, source.id, {
      allowed_reject_to: payload.targetId,
    });
    selectedNodeId.value = source.id;
    ElMessage.success(payload.targetId ? "退回线已保存" : "退回线已删除");
    await loadWorkflow();
  } catch (error: unknown) {
    await loadWorkflow();
    showBackendError(error, "退回线保存失败");
  } finally {
    savingGraph.value = false;
  }
}

async function handleValidate(showSuccess = true) {
  try {
    const res = (await validateBatchWorkflow(
      props.batchId,
      activePhase.value
    )) as unknown as ValidationResult;
    validationErrors.value = res.errors || [];

    if (res.valid && showSuccess) {
      ElMessage.success("流程配置验证通过");
    } else if (!res.valid && showSuccess) {
      ElMessage.warning("流程配置存在问题，请检查");
    }
  } catch {
    if (showSuccess) {
      ElMessage.error("验证失败");
    }
    validationErrors.value = [];
  }
}

function openFullscreenGraph() {
  fullscreenHeight.value = window.innerHeight - 120;
  fullscreenGraphReady.value = false;
  graphFullscreenVisible.value = true;
}

function handleFullscreenOpened() {
  fullscreenGraphReady.value = true;
}

function handleFullscreenClosed() {
  fullscreenGraphReady.value = false;
}

function handleDialogClose() {
  createFormRef.value?.resetFields();
}

function normalizeNodes(list: WorkflowNode[]) {
  return [...list]
    .sort((a, b) => a.sort_order - b.sort_order || a.id - b.id)
    .map((node, index) => ({ ...node, sort_order: index }));
}

function applyLocalOrder(ids: number[]) {
  const map = new Map(nodes.value.map((node) => [node.id, node]));
  return ids
    .map((id, index) => {
      const node = map.get(id);
      return node ? { ...node, sort_order: index } : null;
    })
    .filter((node): node is WorkflowNode => Boolean(node));
}

function ensureSelectedNode() {
  if (
    selectedNodeId.value &&
    sortedNodes.value.some((node) => node.id === selectedNodeId.value)
  ) {
    return;
  }
  selectedNodeId.value = sortedNodes.value[0]?.id ?? null;
}

function toNodeForm(node: WorkflowNode): WorkflowNodeInput {
  return {
    code: node.code,
    name: node.name,
    node_type: node.node_type,
    role_fk: node.role_fk || undefined,
    require_expert_review: node.require_expert_review || false,
    return_policy: node.return_policy || "NONE",
    allowed_reject_to: node.allowed_reject_to || null,
    notice: node.notice || "",
    sort_order: node.sort_order,
    is_active: node.is_active,
  };
}

function canEnableExpertReview(roleId?: number) {
  if (!roleId) return false;
  const role = roleMap.value.get(roleId);
  return Boolean(role?.code && role.code.endsWith("_ADMIN"));
}

function roleLabel(node: WorkflowNode) {
  if (node.node_type === "SUBMIT" || node.code === "STUDENT_SUBMIT") return "学生";
  return node.role_code || "未配置角色";
}

function sameIds(left: number[], right: number[]) {
  return left.length === right.length && left.every((id, index) => id === right[index]);
}

function showBackendError(error: unknown, fallback: string) {
  const response = isRecord(error) ? error.response : null;
  const data = isRecord(response) ? response.data : null;
  const detail =
    isRecord(data) && typeof data.detail === "string" ? data.detail : fallback;
  ElMessage.error(detail);
}
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.batch-workflow-config {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.workflow-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 0 2px 12px;
  border-bottom: 1px solid $slate-100;
}

.phase-tabs {
  flex: 1;
  min-width: 360px;

  :deep(.el-tabs__header) {
    margin-bottom: 0;
  }
}

.topbar-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 8px;
}

.loading-container {
  padding: 24px;
}

.workflow-empty {
  min-height: 360px;
}

.workflow-workbench {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 340px;
  gap: 18px;
  align-items: start;
}

.validation-panel {
  grid-column: 1 / -1;
  padding: 14px 16px;
  border: 1px solid rgba(245, 158, 11, 0.24);
  border-radius: 16px;
  background: linear-gradient(135deg, #fff7ed 0%, #ffffff 100%);
  color: #92400e;

  .validation-title {
    margin-bottom: 6px;
    font-weight: 800;
  }

  ul {
    margin: 0;
    padding-left: 18px;
  }
}

.canvas-panel,
.inspector-card,
.node-list-card {
  border: 1px solid rgba($slate-200, 0.95);
  border-radius: $radius-xl;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: $shadow-md;
}

.canvas-panel {
  min-width: 0;
  padding: 18px;
}

.canvas-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 14px;

  p {
    margin: 6px 0 0;
    color: $slate-500;
    font-size: 13px;
  }
}

.canvas-stats {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;

  span {
    padding: 6px 10px;
    border: 1px solid $slate-200;
    border-radius: 999px;
    background: $slate-50;
    color: $slate-600;
    font-size: 12px;
    font-weight: 700;
  }
}

.legend {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 14px;

  span {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 6px 10px;
    border: 1px solid $slate-200;
    border-radius: 999px;
    background: #fff;
    color: $slate-600;
    font-size: 12px;
    font-weight: 700;
  }

  .dot {
    width: 10px;
    height: 10px;
    border-radius: 4px;
  }

  .submit {
    background: #16a34a;
  }

  .review {
    background: #2563eb;
  }

  .approval {
    background: #f59e0b;
  }

  .line {
    width: 18px;
    height: 0;
    border-top: 2px dashed #ef4444;
  }
}

.inspector-panel {
  display: flex;
  flex-direction: column;
  gap: 14px;
  min-width: 0;
}

.inspector-card,
.node-list-card {
  padding: 16px;
}

.inspector-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
  color: $slate-900;
  font-weight: 800;
}

.inspector-empty {
  padding: 34px 0;
}

.node-form {
  :deep(.el-form-item) {
    margin-bottom: 16px;
  }
}

.form-hint {
  margin-top: 6px;
  color: $slate-400;
  font-size: 12px;
  line-height: 1.4;
}

.inspector-actions {
  display: flex;
  gap: 10px;

  .el-button {
    flex: 1;
  }
}

.node-list-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.node-list-item {
  display: flex;
  align-items: center;
  width: 100%;
  gap: 10px;
  padding: 10px;
  border: 1px solid transparent;
  border-radius: 14px;
  background: $slate-50;
  color: inherit;
  cursor: pointer;
  text-align: left;
  transition: all 0.18s ease;

  &:hover,
  &.active {
    border-color: rgba($primary-500, 0.35);
    background: rgba($primary-50, 0.9);
  }
}

.node-index {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 10px;
  background: #fff;
  color: $primary-700;
  font-size: 12px;
  font-weight: 900;
}

.node-copy {
  flex: 1;
  min-width: 0;

  strong,
  small {
    display: block;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  strong {
    color: $slate-800;
    font-size: 13px;
  }

  small {
    color: $slate-500;
    font-size: 12px;
  }
}

.muted {
  color: $slate-400;
  font-size: 12px;
  font-weight: 500;
}

.w-full {
  width: 100%;
}

.fullscreen-graph-container {
  height: 100%;
  padding: 20px;
  background: #f5f7fa;
  box-sizing: border-box;
}

@media (max-width: 1180px) {
  .workflow-topbar,
  .canvas-heading {
    align-items: stretch;
    flex-direction: column;
  }

  .topbar-actions,
  .canvas-stats {
    justify-content: flex-start;
  }

  .workflow-workbench {
    grid-template-columns: 1fr;
  }
}
</style>
