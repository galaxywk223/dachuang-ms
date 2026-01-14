<template>
  <div class="batch-workflow-config">
    <el-tabs v-model="activePhase" @tab-change="handlePhaseChange">
      <el-tab-pane label="立项流程" name="APPLICATION" />
      <el-tab-pane label="中期流程" name="MID_TERM" />
      <el-tab-pane label="结题流程" name="CLOSURE" />
    </el-tabs>

    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="5" animated />
    </div>

    <template v-else>
      <!-- 未初始化状态 -->
      <el-empty
        v-if="!workflow"
        description="该阶段尚未配置工作流"
        class="workflow-empty"
      >
        <el-button type="primary" @click="handleInitWorkflow">
          初始化默认流程
        </el-button>
      </el-empty>

      <!-- 已配置状态 -->
      <div v-else class="workflow-content">
        <!-- 验证警告 -->
        <el-alert
          v-if="validationErrors.length > 0"
          title="流程配置存在问题"
          type="warning"
          :closable="false"
          class="validation-alert"
        >
          <ul>
            <li v-for="(error, index) in validationErrors" :key="index">
              {{ error }}
            </li>
          </ul>
        </el-alert>

        <el-row :gutter="20">
          <!-- 左侧：节点列表 -->
          <el-col :span="12">
            <el-card shadow="never" class="nodes-card">
              <template #header>
                <div class="card-header">
                  <span>流程节点配置</span>
                  <el-button
                    v-if="!workflow.is_locked"
                    type="primary"
                    size="small"
                    @click="handleAddNode"
                  >
                    <el-icon><Plus /></el-icon>
                    添加节点
                  </el-button>
                </div>
              </template>

              <el-table :data="nodes" border stripe>
                <el-table-column
                  type="index"
                  label="顺序"
                  width="60"
                  align="center"
                />
                <el-table-column prop="name" label="节点名称" min-width="120" />
                <el-table-column label="执行角色" width="120" align="center">
                  <template #default="{ row }">
                    {{
                      row.role_name ||
                      (row.code === "STUDENT_SUBMIT" ||
                      row.name.includes("学生提交")
                        ? "学生"
                        : "-")
                    }}
                  </template>
                </el-table-column>
                <el-table-column label="日期范围" width="180" align="center">
                  <template #default="{ row }">
                    <div
                      v-if="row.start_date || row.end_date"
                      class="date-range"
                    >
                      <div v-if="row.start_date" class="date-item">
                        开始: {{ row.start_date }}
                      </div>
                      <div v-if="row.end_date" class="date-item">
                        结束: {{ row.end_date }}
                      </div>
                    </div>
                    <span v-else class="text-gray">未设置</span>
                  </template>
                </el-table-column>
                <el-table-column
                  prop="require_expert_review"
                  label="专家评审"
                  width="100"
                  align="center"
                >
                  <template #default="{ row }">
                    <el-tag
                      v-if="row.require_expert_review"
                      type="warning"
                      size="small"
                    >
                      需要
                    </el-tag>
                    <span v-else class="text-gray">否</span>
                  </template>
                </el-table-column>
                <el-table-column label="退回设置" width="100" align="center">
                  <template #default="{ row }">
                    <el-tag
                      v-if="
                        row.allowed_reject_to &&
                        row.allowed_reject_to.length > 0
                      "
                      type="danger"
                      size="small"
                    >
                      {{ row.allowed_reject_to.length }} 个节点
                    </el-tag>
                    <span v-else class="text-gray">无</span>
                  </template>
                </el-table-column>
                <el-table-column
                  label="操作"
                  width="150"
                  align="center"
                  fixed="right"
                >
                  <template #default="{ row }">
                    <el-button
                      v-if="row.can_edit && !workflow.is_locked"
                      link
                      type="primary"
                      size="small"
                      @click="handleEditNode(row)"
                    >
                      编辑
                    </el-button>
                    <el-button
                      v-if="!row.can_edit && !workflow.is_locked"
                      link
                      type="primary"
                      size="small"
                      @click="handleEditNodeDates(row)"
                    >
                      配置日期
                    </el-button>
                    <el-button
                      v-if="row.can_edit && !workflow.is_locked"
                      link
                      type="danger"
                      size="small"
                      @click="handleDeleteNode(row)"
                    >
                      删除
                    </el-button>
                    <span
                      v-if="!row.can_edit && workflow.is_locked"
                      class="text-gray"
                      >不可编辑</span
                    >
                  </template>
                </el-table-column>
              </el-table>
            </el-card>
          </el-col>

          <!-- 右侧：流程图 -->
          <el-col :span="12">
            <el-card shadow="never" class="graph-card">
              <template #header>
                <div class="card-header">
                  <span>流程可视化</span>
                  <el-button size="small" @click="handleValidate">
                    <el-icon><CircleCheck /></el-icon>
                    验证流程
                  </el-button>
                  <el-button
                    size="small"
                    @click="openFullscreenGraph"
                    title="全屏查看"
                    style="margin-left: 8px"
                  >
                    <el-icon><FullScreen /></el-icon>
                  </el-button>
                </div>
              </template>

              <workflow-graph :nodes="nodes" :height="500" />

              <div class="legend">
                <span class="legend-item">
                  <span
                    class="legend-color"
                    style="background-color: #10b981"
                  ></span>
                  提交
                </span>
                <span class="legend-item">
                  <span
                    class="legend-color"
                    style="background-color: #3b82f6"
                  ></span>
                  审核
                </span>
                <span class="legend-item">
                  <span
                    class="legend-color"
                    style="background-color: #f59e0b"
                  ></span>
                  确认
                </span>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </template>

    <!-- 节点编辑对话框 -->
    <el-dialog
      v-model="nodeDialogVisible"
      :title="editingNode ? '编辑节点' : '新增节点'"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form
        ref="nodeFormRef"
        :model="nodeForm"
        :rules="nodeRules"
        label-width="120px"
      >
        <el-form-item label="节点名称" prop="name">
          <el-input v-model="nodeForm.name" placeholder="如: 导师审核" />
        </el-form-item>
        <el-form-item label="执行角色" prop="role_fk">
          <el-select
            v-model="nodeForm.role_fk"
            placeholder="选择角色"
            filterable
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
            v-model="nodeForm.require_expert_review"
            :disabled="!canEnableExpertReview"
          />
          <div class="form-hint">
            仅管理员节点可开启，开启后需先完成专家评审再终审。
          </div>
        </el-form-item>
        <el-form-item label="允许退回" prop="allowed_reject_to">
          <el-select
            v-model="nodeForm.allowed_reject_to"
            placeholder="选择可退回的节点"
          >
            <el-option
              v-for="node in rejectTargetOptions"
              :key="node.id"
              :label="node.name"
              :value="node.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="开始日期">
          <el-date-picker
            v-model="nodeForm.start_date"
            type="date"
            placeholder="请选择开始日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker
            v-model="nodeForm.end_date"
            type="date"
            placeholder="请选择结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="审核注意事项">
          <el-input
            v-model="nodeForm.notice"
            type="textarea"
            :rows="3"
            placeholder="可选"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="nodeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveNode">确定</el-button>
      </template>
    </el-dialog>

    <!-- 日期配置对话框 -->
    <el-dialog
      v-model="dateDialogVisible"
      :title="`配置日期 - ${editingNode?.name || ''}`"
      width="500px"
    >
      <el-form :model="dateForm" label-width="100px">
        <el-form-item label="开始日期">
          <el-date-picker
            v-model="dateForm.start_date"
            type="date"
            placeholder="请选择开始日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker
            v-model="dateForm.end_date"
            type="date"
            placeholder="请选择结束日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dateDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveDates">确定</el-button>
      </template>
    </el-dialog>

    <!-- 全屏图表对话框 -->
    <el-dialog
      v-model="graphFullscreenVisible"
      title="流程可视化（全屏）"
      fullscreen
      append-to-body
      destroy-on-close
      class="graph-fullscreen-dialog"
      @opened="handleFullscreenOpened"
      @closed="handleFullscreenClosed"
    >
      <div class="fullscreen-graph-container" v-if="fullscreenGraphReady">
        <workflow-graph :nodes="nodes" :height="fullscreenHeight" />
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from "vue";
import {
  ElMessage,
  ElMessageBox,
  type FormInstance,
  type FormRules,
} from "element-plus";
import { Plus, CircleCheck, FullScreen } from "@element-plus/icons-vue";
import WorkflowGraph from "@/components/business/WorkflowGraph.vue";
import {
  getBatchWorkflow,
  initBatchWorkflow,
  createWorkflowNode,
  updateWorkflowNode,
  deleteWorkflowNode,
  validateBatchWorkflow,
  type WorkflowConfig,
  type WorkflowNode,
  type WorkflowNodeInput,
} from "@/api/system-settings/batch-workflow";
import { getRoles } from "@/api/users/roles";

const props = defineProps<{
  batchId: number;
}>();

type Role = {
  id: number;
  name: string;
  code?: string;
};

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null;

const activePhase = ref<"APPLICATION" | "MID_TERM" | "CLOSURE">("APPLICATION");
const loading = ref(false);
const workflow = ref<WorkflowConfig | null>(null);
const nodes = ref<WorkflowNode[]>([]);
const validationErrors = ref<string[]>([]);
const availableRoles = ref<Role[]>([]);

const nodeDialogVisible = ref(false);
const nodeFormRef = ref<FormInstance>();
const editingNode = ref<WorkflowNode | null>(null);
const nodeForm = ref<WorkflowNodeInput>({
  code: "",
  name: "",
  node_type: "REVIEW",
  role_fk: undefined,
  require_expert_review: false,
  allowed_reject_to: null,
  notice: "",
  start_date: undefined,
  end_date: undefined,
  sort_order: 0,
});

const nodeRules: FormRules = {
  name: [{ required: true, message: "请输入节点名称", trigger: "blur" }],
  role_fk: [{ required: true, message: "请选择执行角色", trigger: "change" }],
};

// 日期配置对话框
const dateDialogVisible = ref(false);
const dateForm = ref<{
  start_date?: string;
  end_date?: string;
}>({
  start_date: undefined,
  end_date: undefined,
});

// 全屏图表
const graphFullscreenVisible = ref(false);
const fullscreenGraphReady = ref(false);
const fullscreenHeight = ref(window.innerHeight - 100);

function openFullscreenGraph() {
  fullscreenHeight.value = window.innerHeight - 100;
  graphFullscreenVisible.value = true;
  // Reset ready state, wait for opened event
  fullscreenGraphReady.value = false;
}

function handleFullscreenOpened() {
  fullscreenGraphReady.value = true;
}

function handleFullscreenClosed() {
  fullscreenGraphReady.value = false;
}

const roleMap = computed(() => {
  const map = new Map<number, Role>();
  for (const role of availableRoles.value) {
    map.set(role.id, role);
  }
  return map;
});

const canEnableExpertReview = computed(() => {
  if (!nodeForm.value.role_fk) return false;
  const role = roleMap.value.get(nodeForm.value.role_fk);
  return Boolean(role?.code && role.code.endsWith("_ADMIN"));
});

const rejectTargetOptions = computed(() => {
  const sorted = [...nodes.value].sort((a, b) => a.sort_order - b.sort_order);
  if (!editingNode.value) return sorted;
  return sorted.filter(
    (node) => node.sort_order < editingNode.value!.sort_order
  );
});

onMounted(() => {
  loadRoles();
  loadWorkflow();
});

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
    console.log(
      `[BatchWorkflowConfig] 加载工作流: batchId=${props.batchId}, phase=${activePhase.value}`
    );
    const res = await getBatchWorkflow(props.batchId, activePhase.value);
    console.log("[BatchWorkflowConfig] 工作流加载成功:", res);
    // 后端直接返回工作流对象，不是包装在 data 里
    workflow.value = res as unknown as WorkflowConfig;
    nodes.value = (res as unknown as WorkflowConfig).nodes || [];

    // 自动验证
    await handleValidate(false);
  } catch (error: unknown) {
    console.error("[BatchWorkflowConfig] 工作流加载失败:", error);
    const response = isRecord(error) ? error.response : null;
    const status = isRecord(response) ? response.status : null;
    const data = isRecord(response) ? response.data : null;
    console.log(
      `[BatchWorkflowConfig] 错误详情: status=${status}, data=`,
      data
    );

    if (status === 404) {
      workflow.value = null;
      nodes.value = [];
    } else {
      ElMessage.error("加载工作流失败");
    }
  } finally {
    loading.value = false;
  }
}

function handlePhaseChange() {
  loadWorkflow();
}

async function handleInitWorkflow() {
  try {
    await ElMessageBox.confirm(
      "将为该阶段初始化默认工作流配置，是否继续？",
      "确认初始化",
      {
        type: "warning",
      }
    );

    loading.value = true;
    await initBatchWorkflow(props.batchId, activePhase.value);
    ElMessage.success("初始化成功");
    await loadWorkflow();
  } catch (error: unknown) {
    if (error !== "cancel") {
      // 提取后端返回的详细错误信息
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

function handleAddNode() {
  editingNode.value = null;
  nodeForm.value = {
    code: "",
    name: "",
    node_type: "REVIEW",
    role_fk: undefined,
    require_expert_review: false,
    allowed_reject_to: null,
    notice: "",
    start_date: undefined,
    end_date: undefined,
    sort_order: nodes.value.length,
  };
  nodeDialogVisible.value = true;
}

function handleEditNode(node: WorkflowNode) {
  editingNode.value = node;
  nodeForm.value = {
    code: node.code,
    name: node.name,
    node_type: node.node_type,
    role_fk: node.role_fk || undefined,
    require_expert_review: node.require_expert_review || false,
    allowed_reject_to: node.allowed_reject_to || null,
    notice: node.notice || "",
    start_date: node.start_date || undefined,
    end_date: node.end_date || undefined,
    sort_order: node.sort_order,
  };
  nodeDialogVisible.value = true;
}

function handleEditNodeDates(node: WorkflowNode) {
  editingNode.value = node;
  dateForm.value = {
    start_date: node.start_date || undefined,
    end_date: node.end_date || undefined,
  };
  dateDialogVisible.value = true;
}

async function handleSaveDates() {
  if (!editingNode.value) return;

  try {
    await updateWorkflowNode(
      props.batchId,
      activePhase.value,
      editingNode.value.id,
      {
        start_date: dateForm.value.start_date,
        end_date: dateForm.value.end_date,
      }
    );
    ElMessage.success("日期配置成功");
    dateDialogVisible.value = false;
    await loadWorkflow();
  } catch {
    ElMessage.error("配置失败");
  }
}

async function handleSaveNode() {
  if (!nodeFormRef.value) return;

  await nodeFormRef.value.validate();

  try {
    if (editingNode.value) {
      await updateWorkflowNode(
        props.batchId,
        activePhase.value,
        editingNode.value.id,
        nodeForm.value
      );
      ElMessage.success("更新成功");
    } else {
      // 新增节点时自动生成节点编码
      const timestamp = Date.now().toString().slice(-6);
      nodeForm.value.code = `REVIEW_${timestamp}`;

      await createWorkflowNode(
        props.batchId,
        activePhase.value,
        nodeForm.value
      );
      ElMessage.success("创建成功");
    }

    nodeDialogVisible.value = false;
    await loadWorkflow();
  } catch {
    ElMessage.error("保存失败");
  }
}

async function handleDeleteNode(node: WorkflowNode) {
  try {
    await ElMessageBox.confirm(`确定要删除节点"${node.name}"吗？`, "确认删除", {
      type: "warning",
    });

    await deleteWorkflowNode(props.batchId, activePhase.value, node.id);
    ElMessage.success("删除成功");
    await loadWorkflow();
  } catch (error: unknown) {
    if (error !== "cancel") {
      ElMessage.error("删除失败");
    }
  }
}

async function handleValidate(showSuccess = true) {
  try {
    const res = await validateBatchWorkflow(props.batchId, activePhase.value);
    // 后端直接返回验证结果，不是包装在 data 里
    const result = res as unknown as { valid: boolean; errors: string[] };
    validationErrors.value = result.errors || [];

    if (result.valid && showSuccess) {
      ElMessage.success("流程配置验证通过");
    } else if (!result.valid) {
      ElMessage.warning("流程配置存在问题，请检查");
    }
  } catch {
    // 只在用户主动验证时显示错误，自动验证时静默失败
    if (showSuccess) {
      ElMessage.error("验证失败");
    }
    // 清空验证错误，避免显示过期的错误信息
    validationErrors.value = [];
  }
}

function handleDialogClose() {
  nodeFormRef.value?.resetFields();
}

watch(
  () => nodeForm.value.role_fk,
  () => {
    if (!canEnableExpertReview.value) {
      nodeForm.value.require_expert_review = false;
    }
  }
);
</script>

<style scoped lang="scss">
.batch-workflow-config {
  .loading-container {
    padding: 20px;
  }

  .workflow-empty {
    margin-top: 40px;
  }

  .workflow-content {
    .validation-alert {
      margin-bottom: 20px;

      ul {
        margin: 8px 0 0;
        padding-left: 20px;

        li {
          margin: 4px 0;
        }
      }
    }

    .nodes-card,
    .graph-card {
      border: 1px solid #e2e8f0;
      border-radius: 8px;

      :deep(.el-card__header) {
        padding: 12px 16px;
        background-color: #f8fafc;
        border-bottom: 1px solid #e2e8f0;
      }

      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-weight: 600;
        color: #334155;
      }
    }

    .graph-card {
      .legend {
        display: flex;
        gap: 16px;
        margin-top: 16px;
        padding-top: 16px;
        border-top: 1px solid #e2e8f0;

        .legend-item {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 13px;
          color: #475569;

          .legend-color {
            width: 12px;
            height: 12px;
            border-radius: 3px;
          }
        }
      }
    }
  }

  .text-gray {
    color: #94a3b8;
  }

  .form-hint {
    font-size: 12px;
    color: #94a3b8;
    line-height: 1.4;
    margin-top: 6px;
  }

  .date-range {
    font-size: 12px;
    line-height: 1.5;

    .date-item {
      color: #475569;
    }
  }

  .fullscreen-graph-container {
    padding: 20px;
    height: 100%;
    width: 100%;
    background: #f5f7fa;
    box-sizing: border-box;
    display: flex;
    justify-content: center;
  }
}
</style>
