<template>
  <div class="batch-page">
    <el-card class="main-card" shadow="never">
      <template #header>
        <div class="card-header">
           <div class="header-left">
             <span class="header-title">批次管理</span>
           </div>
           <div class="header-actions">
           <el-select
              v-model="statusFilter"
              placeholder="状态筛选"
              size="default"

              @change="handleFilterChange"
            >
              <el-option label="全部状态" value="" />
              <el-option
                v-for="option in batchStatusOptions"
                :key="option.value"
                :label="option.label"
                :value="option.value"
              />
            </el-select>
            <el-switch
              v-model="showArchived"
              active-text="显示归档/回收站"
              @change="handleFilterChange"
            />
            <el-button type="primary" @click="openBatchDialog">
              <el-icon class="mr-1"><Plus /></el-icon>新建批次
            </el-button>
           </div>
        </div>
      </template>

      <el-table 
        :data="filteredBatches" 
        v-loading="batchLoading" 
        border 
        stripe 
        style="width: 100%"
      >
        <el-table-column prop="name" label="批次名称" min-width="160" />
        <el-table-column prop="year" label="年度" width="100" />
        <el-table-column prop="code" label="编码" min-width="120" />
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" effect="light">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="当前" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.is_current" type="success" effect="light">
              当前
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" min-width="160">
          <template #default="{ row }">
            {{ formatDate(row.updated_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="280" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="primary" link @click="openSettings(row)">配置</el-button>
            <el-button
              v-if="row.status === 'draft'"
              type="success"
              link
              @click="startBatch(row)"
            >
              开始
            </el-button>
            <el-button
              v-if="row.status === 'active'"
              type="warning"
              link
              @click="finishBatch(row)"
            >
              结束
            </el-button>
            <el-button
              v-if="row.status === 'finished'"
              type="info"
              link
              @click="archiveBatch(row)"
            >
              归档
            </el-button>
            <el-button
              v-if="row.status === 'archived' || row.is_deleted"
              type="success"
              link
              @click="restoreBatch(row)"
            >
              恢复
            </el-button>
            <el-button
              v-if="canDelete(row)"
              type="danger"
              link
              @click="handleDelete(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="batchDialogVisible" title="新建批次" width="420px">
      <el-form :model="batchForm" label-width="90px">
        <el-form-item label="批次名称">
          <el-input v-model="batchForm.name" placeholder="如：2025年第一批" />
        </el-form-item>
        <el-form-item label="年度">
          <el-input-number v-model="batchForm.year" :min="2000" :max="2100" />
        </el-form-item>
        <el-form-item label="批次编码">
          <el-input v-model="batchForm.code" placeholder="如：2025-A" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="batchDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="batchSaving" @click="submitBatch">
            创建
          </el-button>
        </span>
      </template>
    </el-dialog>

  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { Plus } from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  listProjectBatches,
  createProjectBatch,
  updateProjectBatch,
  restoreProjectBatch,
  deleteProjectBatch,
} from "@/api/system-settings/batches";

defineOptions({ name: "Level1BatchesView" });

type BatchRow = {
  id: number;
  name?: string;
  year?: number;
  code?: string;
  status?: string;
  is_current?: boolean;
  is_deleted?: boolean;
  updated_at?: string;
};

type BatchListResponse = {
  data?: BatchRow[];
};

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null;

const getErrorMessage = (error: unknown, fallback: string) => {
  if (!isRecord(error)) return fallback;
  const response = error.response;
  if (isRecord(response) && isRecord(response.data) && typeof response.data.message === "string") {
    return response.data.message;
  }
  if (typeof error.message === "string") return error.message;
  return fallback;
};

const router = useRouter();
const batchLoading = ref(false);
const batches = ref<BatchRow[]>([]);
const statusFilter = ref("");
const showArchived = ref(false);

const batchDialogVisible = ref(false);
const batchSaving = ref(false);
const batchForm = reactive({
  name: "",
  year: new Date().getFullYear(),
  code: "",
  status: "draft",
});

const batchStatusOptions = [
  { value: "draft", label: "草稿" },
  { value: "active", label: "进行中" },
  { value: "finished", label: "已结束" },
  { value: "archived", label: "已归档" },
];

const canDelete = (row: BatchRow) => row.status === "draft" && !row.is_deleted;

const getStatusLabel = (status?: string) => {
  const match = batchStatusOptions.find((item) => item.value === status);
  return match ? match.label : "未知";
};

const getStatusTagType = (status?: string) => {
  switch (status) {
    case "active":
      return "success";
    case "finished":
      return "info";
    case "archived":
      return "info";
    default:
      return "";
  }
};

const filteredBatches = computed(() => {
  if (!statusFilter.value) return batches.value;
  return batches.value.filter((item) => item.status === statusFilter.value);
});

const formatDate = (value?: string) => {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  const yyyy = date.getFullYear();
  const mm = String(date.getMonth() + 1).padStart(2, "0");
  const dd = String(date.getDate()).padStart(2, "0");
  const hh = String(date.getHours()).padStart(2, "0");
  const min = String(date.getMinutes()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd} ${hh}:${min}`;
};

const loadBatches = async () => {
  batchLoading.value = true;
  try {
    const res = (await listProjectBatches({
      include_archived: showArchived.value ? 1 : 0,
      include_deleted: showArchived.value ? 1 : 0,
    })) as BatchListResponse | BatchRow[];
    const data = isRecord(res) && "data" in res ? res.data : res;
    batches.value = Array.isArray(data) ? data : [];
  } catch (error) {
    console.error(error);
    ElMessage.error("加载批次失败");
  } finally {
    batchLoading.value = false;
  }
};

const handleFilterChange = () => {
  loadBatches();
};

const openBatchDialog = () => {
  batchForm.name = "";
  batchForm.year = new Date().getFullYear();
  batchForm.code = "";
  batchForm.status = "draft";
  batchDialogVisible.value = true;
};

const submitBatch = async () => {
  if (!batchForm.name || !batchForm.code) {
    ElMessage.warning("请填写批次名称和编码");
    return;
  }
  batchSaving.value = true;
  try {
    const res = await createProjectBatch({ ...batchForm });
    if (isRecord(res) && (res.code === 200 || res.code === 201)) {
      ElMessage.success("批次创建成功");
      batchDialogVisible.value = false;
      await loadBatches();
    }
  } catch (error) {
    console.error(error);
    ElMessage.error(getErrorMessage(error, "批次创建失败"));
  } finally {
    batchSaving.value = false;
  }
};

const openSettings = (row: BatchRow) => {
  router.push({ name: "level1-settings-batch-config", params: { id: row.id } });
};

const startBatch = async (row: BatchRow) => {
  try {
    await ElMessageBox.confirm("开始该批次将替换当前批次，是否继续？", "确认操作", {
      type: "warning",
      confirmButtonText: "继续",
      cancelButtonText: "取消",
    });
  } catch {
    return;
  }
  try {
    await updateProjectBatch(row.id, { status: "active" });
    ElMessage.success("批次已开始");
    await loadBatches();
  } catch (error) {
    console.error(error);
    ElMessage.error(getErrorMessage(error, "开始失败"));
  }
};

const finishBatch = async (row: BatchRow) => {
  try {
    await ElMessageBox.confirm("结束后该批次将进入只读状态，是否继续？", "确认操作", {
      type: "warning",
      confirmButtonText: "继续",
      cancelButtonText: "取消",
    });
  } catch {
    return;
  }
  try {
    await updateProjectBatch(row.id, { status: "finished" });
    ElMessage.success("批次已结束");
    await loadBatches();
  } catch (error) {
    console.error(error);
    ElMessage.error(getErrorMessage(error, "结束失败"));
  }
};

const archiveBatch = async (row: BatchRow) => {
  try {
    await ElMessageBox.confirm("归档后该批次将进入只读状态，是否继续？", "确认操作", {
      type: "warning",
      confirmButtonText: "继续",
      cancelButtonText: "取消",
    });
  } catch {
    return;
  }
  try {
    await updateProjectBatch(row.id, { status: "archived" });
    ElMessage.success("批次已归档");
    await loadBatches();
  } catch (error) {
    console.error(error);
    ElMessage.error(getErrorMessage(error, "归档失败"));
  }
};

const restoreBatch = async (row: BatchRow) => {
  try {
    await ElMessageBox.confirm("确认恢复该批次并移出归档？", "确认操作", {
      type: "warning",
      confirmButtonText: "继续",
      cancelButtonText: "取消",
    });
  } catch {
    return;
  }
  try {
    await restoreProjectBatch(row.id);
    ElMessage.success("批次已恢复");
    await loadBatches();
  } catch (error) {
    console.error(error);
    ElMessage.error(getErrorMessage(error, "恢复失败"));
  }
};

const handleDelete = async (row: BatchRow) => {
  try {
    await ElMessageBox.confirm(
      "确定删除该批次？若该批次已有项目，将移入归档并可在回收站恢复。",
      "确认操作",
      {
        type: "warning",
        confirmButtonText: "继续",
        cancelButtonText: "取消",
      }
    );
  } catch {
    return;
  }
  try {
    const res = await deleteProjectBatch(row.id);
    if (isRecord(res) && (res.code === 200 || res.code === 204)) {
      ElMessage.success((typeof res.message === "string" && res.message) || "删除成功");
      await loadBatches();
    } else {
      ElMessage.error((isRecord(res) && typeof res.message === "string" && res.message) || "删除失败");
    }
  } catch (error) {
    console.error(error);
    ElMessage.error(getErrorMessage(error, "删除失败"));
  }
};

onMounted(async () => {
  await loadBatches();
});
</script>

<style scoped lang="scss">
@use "./Batches.scss";
</style>
