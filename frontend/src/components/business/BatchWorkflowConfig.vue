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
                <el-table-column
                  prop="node_type"
                  label="类型"
                  width="100"
                  align="center"
                >
                  <template #default="{ row }">
                    <el-tag :type="getNodeTypeTag(row.node_type)" size="small">
                      {{ getNodeTypeName(row.node_type) }}
                    </el-tag>
                  </template>
                </el-table-column>
                <el-table-column
                  prop="role_name"
                  label="执行角色"
                  width="120"
                />
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
                      v-if="row.can_edit && !workflow.is_locked"
                      link
                      type="danger"
                      size="small"
                      @click="handleDeleteNode(row)"
                    >
                      删除
                    </el-button>
                    <span v-if="!row.can_edit" class="text-gray">不可编辑</span>
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
                </div>
              </template>

              <workflow-graph :nodes="nodes" :height="500" />

              <div class="legend">
                <span class="legend-item">
                  <span
                    class="legend-color"
                    style="background-color: #52c41a"
                  ></span>
                  提交
                </span>
                <span class="legend-item">
                  <span
                    class="legend-color"
                    style="background-color: #1890ff"
                  ></span>
                  审核
                </span>
                <span class="legend-item">
                  <span
                    class="legend-color"
                    style="background-color: #722ed1"
                  ></span>
                  专家评审
                </span>
                <span class="legend-item">
                  <span
                    class="legend-color"
                    style="background-color: #fa8c16"
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
        <el-form-item label="节点编码" prop="code">
          <el-input v-model="nodeForm.code" placeholder="如: TEACHER_REVIEW" />
        </el-form-item>
        <el-form-item label="节点名称" prop="name">
          <el-input v-model="nodeForm.name" placeholder="如: 导师审核" />
        </el-form-item>
        <el-form-item label="节点类型" prop="node_type">
          <el-select v-model="nodeForm.node_type" placeholder="选择类型">
            <el-option label="审核" value="REVIEW" />
            <el-option label="专家评审" value="EXPERT_REVIEW" />
            <el-option label="确认" value="APPROVAL" />
          </el-select>
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
        <el-form-item label="允许退回" prop="allowed_reject_to">
          <el-select
            v-model="nodeForm.allowed_reject_to"
            multiple
            placeholder="选择可退回的节点"
          >
            <el-option
              v-for="node in nodes"
              :key="node.id"
              :label="`${node.name} (${node.node_type})`"
              :value="node.id"
              :disabled="editingNode && node.id === editingNode.id"
            />
          </el-select>
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import {
  ElMessage,
  ElMessageBox,
  type FormInstance,
  type FormRules,
} from "element-plus";
import { Plus, CircleCheck } from "@element-plus/icons-vue";
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
  role_fk: 0,
  allowed_reject_to: [],
  notice: "",
  sort_order: 0,
});

const nodeRules: FormRules = {
  code: [{ required: true, message: "请输入节点编码", trigger: "blur" }],
  name: [{ required: true, message: "请输入节点名称", trigger: "blur" }],
  node_type: [{ required: true, message: "请选择节点类型", trigger: "change" }],
  role_fk: [{ required: true, message: "请选择执行角色", trigger: "change" }],
};

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
    const res = await getBatchWorkflow(props.batchId, activePhase.value);
    workflow.value = res.data;
    nodes.value = res.data.nodes || [];

    // 自动验证
    await handleValidate(false);
  } catch (error: unknown) {
    const response = isRecord(error) ? error.response : null;
    const status = isRecord(response) ? response.status : null;
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
      ElMessage.error("初始化失败");
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
    role_fk: 0,
    allowed_reject_to: [],
    notice: "",
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
    role_fk: node.role_fk || 0,
    allowed_reject_to: node.allowed_reject_to || [],
    notice: node.notice || "",
    sort_order: node.sort_order,
  };
  nodeDialogVisible.value = true;
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
    validationErrors.value = res.data.errors || [];

    if (res.data.valid && showSuccess) {
      ElMessage.success("流程配置验证通过");
    } else if (!res.data.valid) {
      ElMessage.warning("流程配置存在问题，请检查");
    }
  } catch {
    ElMessage.error("验证失败");
  }
}

function handleDialogClose() {
  nodeFormRef.value?.resetFields();
}

function getNodeTypeName(type: string) {
  const names: Record<string, string> = {
    SUBMIT: "提交",
    REVIEW: "审核",
    EXPERT_REVIEW: "专家评审",
    APPROVAL: "确认",
  };
  return names[type] || type;
}

function getNodeTypeTag(type: string) {
  const tags: Record<string, "" | "success" | "warning" | "danger"> = {
    SUBMIT: "success",
    REVIEW: "",
    EXPERT_REVIEW: "warning",
    APPROVAL: "danger",
  };
  return tags[type] || "";
}
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
      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
      }
    }

    .graph-card {
      .legend {
        display: flex;
        gap: 16px;
        margin-top: 16px;
        padding-top: 16px;
        border-top: 1px solid #e8e8e8;

        .legend-item {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 13px;

          .legend-color {
            width: 16px;
            height: 16px;
            border-radius: 3px;
          }
        }
      }
    }
  }

  .text-gray {
    color: #999;
  }
}
</style>
