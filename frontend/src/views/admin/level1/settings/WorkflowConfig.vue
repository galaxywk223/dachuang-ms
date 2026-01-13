<template>
  <div class="workflow-config-page">
    <el-card class="main-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="header-title">流程配置</span>
          </div>
          <div class="header-actions">
            <el-button type="primary" @click="openWorkflowDialog"
              >新建流程</el-button
            >
          </div>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="6">
          <el-card shadow="never" class="panel-card">
            <template #header>
              <div class="panel-header">流程列表</div>
            </template>
            <el-scrollbar height="540px">
              <div
                v-for="item in workflows"
                :key="item.id"
                class="list-item"
                :class="{ active: currentWorkflow?.id === item.id }"
                @click="selectWorkflow(item)"
              >
                <div class="item-title">{{ item.name }}</div>
                <div class="item-meta">
                  <el-tag size="small" effect="plain">{{
                    phaseLabel(item.phase)
                  }}</el-tag>
                  <el-tag
                    v-if="item.batch"
                    size="small"
                    effect="plain"
                    type="info"
                    >批次 {{ item.batch }}</el-tag
                  >
                </div>
              </div>
            </el-scrollbar>
          </el-card>
        </el-col>

        <el-col :span="18">
          <el-card shadow="never" class="panel-card">
            <template #header>
              <div class="panel-header">
                <span>节点配置</span>
                <div class="header-actions">
                  <el-button
                    type="primary"
                    plain
                    :disabled="!currentWorkflow"
                    @click="openNodeDialog"
                  >
                    新增节点
                  </el-button>
                </div>
              </div>
            </template>

            <div v-if="!currentWorkflow" class="empty-state">
              <el-empty description="请选择流程" />
            </div>

            <div v-else class="node-list">
              <div
                v-for="(node, index) in nodes"
                :key="node.id"
                class="node-item"
                draggable="true"
                @dragstart="handleDragStart(index)"
                @dragover.prevent
                @drop="handleDrop(index)"
              >
                <div class="node-handle">⋮⋮</div>
                <div class="node-content">
                  <div class="node-title">{{ node.name }}</div>
                  <div class="node-meta">
                    <el-tag size="small" effect="plain">{{
                      node.node_type
                    }}</el-tag>
                    <el-tag size="small" effect="plain" type="info">{{
                      node.role
                    }}</el-tag>
                    <el-tag
                      v-if="node.review_level"
                      size="small"
                      effect="plain"
                      type="success"
                      >{{ node.review_level }}</el-tag
                    >
                    <el-tag
                      v-if="node.scope"
                      size="small"
                      effect="plain"
                      type="warning"
                      >{{ node.scope }}</el-tag
                    >
                  </div>
                </div>
                <div class="node-actions">
                  <el-button link type="primary" @click="editNode(node)"
                    >编辑</el-button
                  >
                  <el-button link type="danger" @click="removeNode(node)"
                    >删除</el-button
                  >
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    <el-dialog
      v-model="workflowDialogVisible"
      title="流程配置"
      width="520px"
      destroy-on-close
    >
      <el-form :model="workflowForm" label-width="120px">
        <el-form-item label="流程名称">
          <el-input v-model="workflowForm.name" placeholder="请输入" />
        </el-form-item>
        <el-form-item label="流程阶段">
          <el-select v-model="workflowForm.phase" placeholder="请选择">
            <el-option
              v-for="item in phaseOptions"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="所属批次">
          <el-select v-model="workflowForm.batch" placeholder="可选" clearable>
            <el-option
              v-for="item in batches"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="说明">
          <el-input
            v-model="workflowForm.description"
            type="textarea"
            :rows="3"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="workflowDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveWorkflow"
          >保存</el-button
        >
      </template>
    </el-dialog>

    <el-dialog
      v-model="nodeDialogVisible"
      title="节点配置"
      width="600px"
      destroy-on-close
    >
      <el-form :model="nodeForm" label-width="120px">
        <el-form-item label="节点名称">
          <el-input v-model="nodeForm.name" placeholder="请输入" />
        </el-form-item>
        <el-form-item label="节点编码">
          <el-input v-model="nodeForm.code" placeholder="例如 TEACHER_REVIEW" />
        </el-form-item>
        <el-form-item label="节点类型">
          <el-select v-model="nodeForm.node_type" placeholder="请选择">
            <el-option label="审核" value="REVIEW" />
            <el-option label="专家评审" value="EXPERT_REVIEW" />
            <el-option label="管理员确认" value="APPROVAL" />
          </el-select>
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="nodeForm.role" placeholder="请选择">
            <el-option label="导师" value="TEACHER" />
            <el-option label="二级管理员" value="LEVEL2_ADMIN" />
            <el-option label="一级管理员" value="LEVEL1_ADMIN" />
            <el-option label="专家" value="EXPERT" />
          </el-select>
        </el-form-item>
        <el-form-item label="审核级别">
          <el-select v-model="nodeForm.review_level" placeholder="可选">
            <el-option label="导师" value="TEACHER" />
            <el-option label="二级" value="LEVEL2" />
            <el-option label="一级" value="LEVEL1" />
          </el-select>
        </el-form-item>
        <el-form-item label="专家范围">
          <el-select v-model="nodeForm.scope" placeholder="可选">
            <el-option label="院级" value="COLLEGE" />
            <el-option label="校级" value="SCHOOL" />
          </el-select>
        </el-form-item>
        <el-form-item label="退回规则">
          <el-select v-model="nodeForm.return_policy" placeholder="请选择">
            <el-option label="不允许退回" value="NONE" />
            <el-option label="退回学生" value="STUDENT" />
            <el-option label="退回导师" value="TEACHER" />
            <el-option label="退回上一级" value="PREVIOUS" />
          </el-select>
        </el-form-item>
        <el-form-item label="评审模板">
          <el-select
            v-model="nodeForm.review_template"
            placeholder="可选"
            clearable
          >
            <el-option
              v-for="item in templates"
              :key="item.id"
              :label="item.name"
              :value="item.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="注意事项">
          <el-input v-model="nodeForm.notice" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="nodeDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveNode"
          >保存</el-button
        >
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  getWorkflows,
  createWorkflow,
  updateWorkflow,
  getWorkflowNodes,
  createWorkflowNode,
  updateWorkflowNode,
  deleteWorkflowNode,
  reorderWorkflowNodes,
  getReviewTemplates,
} from "@/api/system-settings";
import { listProjectBatches } from "@/api/system-settings/batches";

defineOptions({ name: "Level1WorkflowConfigView" });

type Workflow = {
  id: number;
  name: string;
  phase: string;
  batch?: number | null;
  description?: string;
};

type WorkflowNode = {
  id: number;
  workflow: number | null;
  code: string;
  name: string;
  node_type: string;
  role: string;
  review_level: string;
  scope?: string;
  return_policy?: string;
  review_template?: number | null;
  notice?: string;
  sort_order?: number;
};

type ReviewTemplate = {
  id: number;
  name: string;
};

type BatchInfo = {
  id: number;
  name?: string;
};

type ListResponse<T> = {
  data?: T[] | { data?: T[]; results?: T[] };
  results?: T[];
};

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null;

const getErrorMessage = (error: unknown, fallback: string) => {
  if (!isRecord(error)) return fallback;
  const response = error.response;
  if (
    isRecord(response) &&
    isRecord(response.data) &&
    typeof response.data.message === "string"
  ) {
    return response.data.message;
  }
  if (typeof error.message === "string") return error.message;
  return fallback;
};

const resolveList = <T>(res: unknown): T[] => {
  const payload = isRecord(res) && "data" in res ? res.data : res;
  if (Array.isArray(payload)) return payload as T[];
  if (isRecord(payload)) {
    if (Array.isArray(payload.results)) return payload.results as T[];
    if (isRecord(payload.data) && Array.isArray(payload.data.results)) {
      return payload.data.results as T[];
    }
    if (Array.isArray(payload.data)) return payload.data as T[];
  }
  return [];
};

const workflows = ref<Workflow[]>([]);
const currentWorkflow = ref<Workflow | null>(null);
const nodes = ref<WorkflowNode[]>([]);
const templates = ref<ReviewTemplate[]>([]);
const batches = ref<BatchInfo[]>([]);
const saving = ref(false);
const dragIndex = ref<number | null>(null);

const workflowDialogVisible = ref(false);
const nodeDialogVisible = ref(false);
const workflowForm = ref({
  id: null as number | null,
  name: "",
  phase: "APPLICATION",
  batch: null as number | null,
  description: "",
});

const nodeForm = ref({
  id: null as number | null,
  workflow: null as number | null,
  code: "",
  name: "",
  node_type: "REVIEW",
  role: "TEACHER",
  review_level: "TEACHER",
  scope: "",
  return_policy: "STUDENT",
  review_template: null as number | null,
  notice: "",
});

const phaseOptions = [
  { label: "立项", value: "APPLICATION" },
  { label: "中期", value: "MID_TERM" },
  { label: "结题", value: "CLOSURE" },
];

const phaseLabel = (phase: string) => {
  const found = phaseOptions.find((item) => item.value === phase);
  return found ? found.label : phase;
};

const loadWorkflows = async () => {
  const res = (await getWorkflows()) as ListResponse<Workflow> | Workflow[];
  workflows.value = resolveList<Workflow>(res);
};

const loadNodes = async (workflowId: number) => {
  const res = (await getWorkflowNodes({ workflow: workflowId })) as
    | ListResponse<WorkflowNode>
    | WorkflowNode[];
  nodes.value = resolveList<WorkflowNode>(res);
};

const loadTemplates = async () => {
  const res = (await getReviewTemplates()) as
    | ListResponse<ReviewTemplate>
    | ReviewTemplate[];
  templates.value = resolveList<ReviewTemplate>(res);
};

const loadBatches = async () => {
  const res = (await listProjectBatches()) as
    | ListResponse<BatchInfo>
    | BatchInfo[];
  batches.value = resolveList<BatchInfo>(res);
};

const selectWorkflow = async (item: Workflow) => {
  currentWorkflow.value = item;
  await loadNodes(item.id);
};

const openWorkflowDialog = () => {
  workflowForm.value = {
    id: null,
    name: "",
    phase: "APPLICATION",
    batch: null,
    description: "",
  };
  workflowDialogVisible.value = true;
};

const saveWorkflow = async () => {
  saving.value = true;
  try {
    if (workflowForm.value.id) {
      await updateWorkflow(workflowForm.value.id, workflowForm.value);
    } else {
      await createWorkflow(workflowForm.value);
    }
    ElMessage.success("保存成功");
    workflowDialogVisible.value = false;
    await loadWorkflows();
  } catch (error) {
    ElMessage.error(getErrorMessage(error, "保存失败"));
  } finally {
    saving.value = false;
  }
};

const openNodeDialog = () => {
  nodeForm.value = {
    id: null,
    workflow: currentWorkflow.value?.id || null,
    code: "",
    name: "",
    node_type: "REVIEW",
    role: "TEACHER",
    review_level: "TEACHER",
    scope: "",
    return_policy: "STUDENT",
    review_template: null,
    notice: "",
  };
  nodeDialogVisible.value = true;
};

const editNode = (node: WorkflowNode) => {
  nodeForm.value = {
    ...node,
    scope: node.scope ?? "",
    return_policy: node.return_policy ?? "STUDENT",
    review_template: node.review_template ?? null,
    notice: node.notice ?? "",
  };
  nodeDialogVisible.value = true;
};

const saveNode = async () => {
  if (!currentWorkflow.value) return;
  saving.value = true;
  try {
    const payload = { ...nodeForm.value, workflow: currentWorkflow.value.id };
    if (payload.id) {
      await updateWorkflowNode(payload.id, payload);
    } else {
      await createWorkflowNode(payload);
    }
    ElMessage.success("保存成功");
    nodeDialogVisible.value = false;
    await loadNodes(currentWorkflow.value.id);
  } catch (error) {
    ElMessage.error(getErrorMessage(error, "保存失败"));
  } finally {
    saving.value = false;
  }
};

const removeNode = async (node: WorkflowNode) => {
  await ElMessageBox.confirm("确认删除该节点？", "提示", {
    type: "warning",
  });
  await deleteWorkflowNode(node.id);
  ElMessage.success("已删除");
  if (currentWorkflow.value) {
    await loadNodes(currentWorkflow.value.id);
  }
};

const handleDragStart = (index: number) => {
  dragIndex.value = index;
};

const handleDrop = async (index: number) => {
  if (dragIndex.value === null || dragIndex.value === index) return;
  const moving = nodes.value.splice(dragIndex.value, 1)[0];
  nodes.value.splice(index, 0, moving);
  dragIndex.value = null;
  const payload = nodes.value.map((item, idx) => ({
    id: item.id,
    sort_order: idx,
  }));
  await reorderWorkflowNodes(payload);
  if (currentWorkflow.value) {
    await loadNodes(currentWorkflow.value.id);
  }
};

onMounted(async () => {
  await Promise.all([loadWorkflows(), loadTemplates(), loadBatches()]);
});
</script>

<style scoped lang="scss">
.workflow-config-page {
  padding: 20px;
}

.main-card {
  border-radius: 8px;
  :deep(.el-card__header) {
    padding: 16px 20px;
    font-weight: 600;
    border-bottom: 1px solid #e2e8f0;
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-title {
  font-size: 16px;
  color: #1e293b;
}

.panel-card {
  min-height: 560px;
  border-radius: 8px;
  :deep(.el-card__header) {
    padding: 12px 16px;
    font-weight: 600;
    border-bottom: 1px solid #e2e8f0;
  }
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.list-item {
  padding: 12px 16px;
  border-bottom: 1px solid #f1f5f9;
  cursor: pointer;
  transition: background-color 0.2s;

  &:hover {
    background-color: #f8fafc;
  }

  &.active {
    background: #eff6ff;
  }

  .item-title {
    font-weight: 600;
    margin-bottom: 4px;
    color: #334155;
  }

  .item-meta {
    display: flex;
    gap: 6px;
  }
}

.node-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.node-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  background: #fff;
  transition: all 0.2s;

  &:hover {
    border-color: #cbd5e1;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  }
}

.node-handle {
  cursor: grab;
  color: #94a3b8;
  padding: 4px;

  &:active {
    cursor: grabbing;
  }
}

.node-content {
  flex: 1;
}

.node-title {
  font-weight: 600;
  color: #334155;
  margin-bottom: 4px;
}

.node-meta {
  display: flex;
  gap: 6px;
  margin-top: 6px;
  flex-wrap: wrap;
}

.node-actions {
  opacity: 0.6;
  transition: opacity 0.2s;

  .node-item:hover & {
    opacity: 1;
  }
}
</style>
