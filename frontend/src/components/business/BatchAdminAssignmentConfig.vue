<template>
  <div class="batch-admin-assignment">
    <el-tabs v-model="activePhase" @tab-change="handlePhaseChange">
      <el-tab-pane label="立项流程" name="APPLICATION" />
      <el-tab-pane label="中期流程" name="MID_TERM" />
      <el-tab-pane label="结题流程" name="CLOSURE" />
    </el-tabs>

    <div v-if="loading" class="loading-container">
      <el-skeleton :rows="5" animated />
    </div>

    <template v-else>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-card shadow="never" class="panel-card">
            <template #header>
              <div class="card-header">数据范围维度</div>
            </template>
            <el-form label-width="110px">
              <el-form-item label="维度类型">
                <el-select
                  v-model="scopeType"
                  placeholder="选择维度"
                  style="width: 100%"
                >
                  <el-option label="学院" value="COLLEGE" />
                  <el-option label="项目类别" value="PROJECT_CATEGORY" />
                  <el-option label="项目级别" value="PROJECT_LEVEL" />
                  <el-option label="重点领域" value="KEY_FIELD" />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button
                  type="primary"
                  :loading="savingScope"
                  :disabled="!scopeType"
                  @click="handleSaveScope"
                >
                  保存维度
                </el-button>
              </el-form-item>
            </el-form>
            <div class="form-hint">
              每个阶段只能选择一个维度，用于管理员分配与权限解析。
            </div>
          </el-card>
        </el-col>

        <el-col :span="16">
          <el-card shadow="never" class="panel-card">
            <template #header>
              <div class="card-header">
                <span>管理员分配</span>
                <el-button
                  type="primary"
                  size="small"
                  :disabled="!scopeType || selectableNodes.length === 0"
                  @click="openAssignmentDialog"
                >
                  新增分配
                </el-button>
              </div>
            </template>

            <el-empty v-if="!scopeType" description="请先配置数据范围维度" />
            <el-empty
              v-else-if="selectableNodes.length === 0"
              description="请先配置该阶段工作流节点"
            />
            <el-table v-else :data="assignments" border stripe>
              <el-table-column
                prop="workflow_name"
                label="工作流节点"
                min-width="160"
              />
              <el-table-column label="维度值" width="160">
                <template #default="{ row }">
                  {{ getScopeLabel(row.scope_value) }}
                </template>
              </el-table-column>
              <el-table-column
                prop="admin_user_name"
                label="管理员"
                width="160"
              />
              <el-table-column label="操作" width="140" align="center">
                <template #default="{ row }">
                  <el-button
                    link
                    type="primary"
                    size="small"
                    @click="editAssignment(row)"
                  >
                    编辑
                  </el-button>
                  <el-button
                    link
                    type="danger"
                    size="small"
                    @click="removeAssignment(row)"
                  >
                    删除
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </el-col>
      </el-row>
    </template>

    <el-dialog
      v-model="assignmentDialogVisible"
      :title="editingAssignment ? '编辑分配' : '新增分配'"
      width="520px"
      destroy-on-close
    >
      <el-form :model="assignmentForm" label-width="110px">
        <el-form-item label="工作流节点" required>
          <el-select
            v-model="assignmentForm.workflow_node"
            placeholder="选择节点"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="node in selectableNodes"
              :key="node.id"
              :label="formatNodeLabel(node)"
              :value="node.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="维度值" required>
          <el-select
            v-model="assignmentForm.scope_value"
            placeholder="选择维度值"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="option in scopeOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="管理员" required>
          <el-select
            v-model="assignmentForm.admin_user"
            placeholder="选择管理员"
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="user in adminUsers"
              :key="user.id"
              :label="formatAdminLabel(user)"
              :value="user.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="assignmentDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :loading="savingAssignment"
          @click="saveAssignment"
        >
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { getRoles } from "@/api/users/roles";
import { getUsers } from "@/api/users/admin";
import {
  getBatchWorkflow,
  type WorkflowNode,
  type WorkflowConfig,
} from "@/api/system-settings/batch-workflow";
import {
  getPhaseScopes,
  createPhaseScope,
  updatePhaseScope,
  getAdminAssignments,
  createAdminAssignment,
  updateAdminAssignment,
  deleteAdminAssignment,
  type PhaseScopeConfig,
  type AdminAssignment,
} from "@/api/system-settings/admin-assignments";
import { useDictionary } from "@/composables/useDictionary";
import { DICT_CODES } from "@/api/dictionaries";

const props = defineProps<{
  batchId: number;
}>();

type Role = {
  id: number;
  code?: string;
  name?: string;
};

type AdminUser = {
  id: number;
  real_name?: string;
  employee_id?: string;
  role_info?: {
    code?: string;
    name?: string;
  } | null;
};

type ScopeOption = {
  value: string;
  label: string;
};

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null;

const resolveList = <T>(payload: unknown): T[] => {
  if (Array.isArray(payload)) return payload as T[];
  if (isRecord(payload) && Array.isArray(payload.results)) {
    return payload.results as T[];
  }
  if (isRecord(payload) && isRecord(payload.data)) {
    const data = payload.data as Record<string, unknown>;
    if (Array.isArray(data.results)) return data.results as T[];
  }
  return [];
};

const { loadDictionaries, getOptions } = useDictionary();

const activePhase = ref<"APPLICATION" | "MID_TERM" | "CLOSURE">("APPLICATION");
const loading = ref(false);
const savingScope = ref(false);
const savingAssignment = ref(false);

const scopeConfig = ref<PhaseScopeConfig | null>(null);
const scopeType = ref<string>("");

const workflowNodes = ref<WorkflowNode[]>([]);
const assignments = ref<AdminAssignment[]>([]);
const adminUsers = ref<AdminUser[]>([]);

const assignmentDialogVisible = ref(false);
const editingAssignment = ref<AdminAssignment | null>(null);
const assignmentForm = ref({
  id: null as number | null,
  workflow_node: null as number | null,
  scope_value: "",
  admin_user: null as number | null,
});

const selectableNodes = computed(() =>
  workflowNodes.value.filter((node) => node.node_type !== "SUBMIT")
);

const scopeOptions = computed<ScopeOption[]>(() => {
  switch (scopeType.value) {
    case "COLLEGE":
      return getOptions(DICT_CODES.COLLEGE).map((item) => ({
        value: item.value,
        label: item.label,
      }));
    case "PROJECT_CATEGORY":
      return getOptions(DICT_CODES.PROJECT_CATEGORY).map((item) => ({
        value: item.value,
        label: item.label,
      }));
    case "PROJECT_LEVEL":
      return getOptions(DICT_CODES.PROJECT_LEVEL).map((item) => ({
        value: item.value,
        label: item.label,
      }));
    case "KEY_FIELD":
      return [
        { value: "1", label: "是" },
        { value: "0", label: "否" },
      ];
    default:
      return [];
  }
});

const getScopeLabel = (value: string) => {
  const match = scopeOptions.value.find((option) => option.value === value);
  return match ? match.label : value || "-";
};

const formatNodeLabel = (node: WorkflowNode) => {
  const roleLabel =
    node.role_name || node.role_code || node.role || node.node_type;
  return `${node.name} (${roleLabel})`;
};

const formatAdminLabel = (user: AdminUser) => {
  const name = user.real_name || user.employee_id || "未知";
  const role = user.role_info?.name || user.role_info?.code || "";
  return role ? `${name} / ${role}` : name;
};

const loadPhaseScope = async () => {
  const res = await getPhaseScopes({
    batch_id: props.batchId,
    phase: activePhase.value,
  });
  const payload = isRecord(res) && "data" in res ? res.data : res;
  const list = resolveList<PhaseScopeConfig>(payload);
  scopeConfig.value = list[0] || null;
  scopeType.value = scopeConfig.value?.scope_type || "";
};

const loadWorkflowNodes = async () => {
  try {
    const res = await getBatchWorkflow(props.batchId, activePhase.value);
    const workflowConfig = res as unknown as WorkflowConfig;
    workflowNodes.value = workflowConfig.nodes || [];
  } catch (error: unknown) {
    const response = isRecord(error) ? error.response : null;
    const status = isRecord(response) ? response.status : null;
    if (status === 404) {
      workflowNodes.value = [];
      return;
    }
    throw error;
  }
};

const loadAssignments = async () => {
  const res = await getAdminAssignments({
    batch_id: props.batchId,
    phase: activePhase.value,
  });
  const payload = isRecord(res) && "data" in res ? res.data : res;
  assignments.value = resolveList<AdminAssignment>(payload);
};

const loadAdminUsers = async () => {
  const rolesRes = await getRoles();
  const rolePayload =
    isRecord(rolesRes) && "data" in rolesRes ? rolesRes.data : rolesRes;
  const roles = resolveList<Role>(rolePayload).filter(
    (role) => role.code && role.code.endsWith("_ADMIN")
  );

  const users: AdminUser[] = [];
  for (const role of roles) {
    const res = await getUsers({ page: 1, page_size: 200, role: role.code });
    const payload = isRecord(res) && "data" in res ? res.data : res;
    const list = resolveList<AdminUser>(payload);
    users.push(...list);
  }

  const map = new Map<number, AdminUser>();
  for (const user of users) {
    if (!map.has(user.id)) {
      map.set(user.id, user);
    }
  }
  adminUsers.value = Array.from(map.values());
};

const loadData = async () => {
  loading.value = true;
  try {
    await Promise.all([
      loadPhaseScope(),
      loadWorkflowNodes(),
      loadAssignments(),
    ]);
  } catch (error: unknown) {
    console.error(error);
    ElMessage.error("加载配置失败");
  } finally {
    loading.value = false;
  }
};

const handlePhaseChange = () => {
  loadData();
};

const handleSaveScope = async () => {
  if (!scopeType.value) return;
  savingScope.value = true;
  try {
    if (scopeConfig.value) {
      await updatePhaseScope(scopeConfig.value.id, {
        scope_type: scopeType.value,
      });
    } else {
      await createPhaseScope({
        batch: props.batchId,
        phase: activePhase.value,
        scope_type: scopeType.value,
      });
    }
    ElMessage.success("保存成功");
    await loadPhaseScope();
    await loadAssignments();
  } catch (error: unknown) {
    console.error(error);
    ElMessage.error("保存失败");
  } finally {
    savingScope.value = false;
  }
};

const openAssignmentDialog = () => {
  if (!scopeType.value) {
    ElMessage.warning("请先配置数据范围维度");
    return;
  }
  editingAssignment.value = null;
  assignmentForm.value = {
    id: null,
    workflow_node: selectableNodes.value[0]?.id || null,
    scope_value: "",
    admin_user: null,
  };
  assignmentDialogVisible.value = true;
};

const editAssignment = (row: AdminAssignment) => {
  editingAssignment.value = row;
  assignmentForm.value = {
    id: row.id,
    workflow_node: row.workflow_node,
    scope_value: row.scope_value,
    admin_user: row.admin_user,
  };
  assignmentDialogVisible.value = true;
};

const saveAssignment = async () => {
  if (
    !assignmentForm.value.workflow_node ||
    !assignmentForm.value.scope_value ||
    !assignmentForm.value.admin_user
  ) {
    ElMessage.warning("请完整填写分配信息");
    return;
  }
  savingAssignment.value = true;
  try {
    const payload = {
      batch: props.batchId,
      phase: activePhase.value,
      workflow_node: assignmentForm.value.workflow_node,
      scope_value: assignmentForm.value.scope_value,
      admin_user: assignmentForm.value.admin_user,
    };
    if (assignmentForm.value.id) {
      await updateAdminAssignment(assignmentForm.value.id, payload);
    } else {
      await createAdminAssignment(payload);
    }
    ElMessage.success("保存成功");
    assignmentDialogVisible.value = false;
    await loadAssignments();
  } catch (error: unknown) {
    console.error(error);
    ElMessage.error("保存失败");
  } finally {
    savingAssignment.value = false;
  }
};

const removeAssignment = async (row: AdminAssignment) => {
  try {
    await ElMessageBox.confirm("确认删除该分配？", "提示", { type: "warning" });
    await deleteAdminAssignment(row.id);
    ElMessage.success("已删除");
    await loadAssignments();
  } catch (error) {
    if (error !== "cancel") {
      ElMessage.error("删除失败");
    }
  }
};

onMounted(async () => {
  await loadDictionaries([
    DICT_CODES.COLLEGE,
    DICT_CODES.PROJECT_CATEGORY,
    DICT_CODES.PROJECT_LEVEL,
  ]);
  await Promise.all([loadAdminUsers(), loadData()]);
});
</script>

<style scoped lang="scss">
.batch-admin-assignment {
  .loading-container {
    padding: 20px;
  }

  .panel-card {
    border: 1px solid #e2e8f0;
    border-radius: 8px;

    :deep(.el-card__header) {
      padding: 12px 16px;
      background-color: #f8fafc;
      border-bottom: 1px solid #e2e8f0;
    }
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 600;
    color: #334155;
  }

  .form-hint {
    font-size: 12px;
    color: #94a3b8;
    line-height: 1.4;
  }
}
</style>
