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
        <el-table-column label="项目级别" min-width="120">
          <template #default="{ row }">
            {{ getProjectLevelLabel(row.project_level) }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status)" effect="light">
              {{ getStatusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="当前" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.status === 'active'" type="success" effect="light">
              进行中
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" min-width="160">
          <template #default="{ row }">
            {{ formatDate(row.updated_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right" align="center">
          <template #default="{ row }">
            <el-button type="primary" link @click="openSettings(row)">配置</el-button>
            <el-button
              type="warning"
              link
              :disabled="row.status === 'active'"
              @click="setRunning(row)"
            >
              设为进行中
            </el-button>
            <el-button
              v-if="row.status === 'archived' || row.is_deleted"
              type="success"
              link
              @click="restoreBatch(row)"
            >
              恢复
            </el-button>
            <el-button type="info" link @click="openStatusDialog(row)">更改状态</el-button>
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
        <el-form-item label="批次状态">
          <el-select v-model="batchForm.status" placeholder="选择状态" style="width: 100%">
            <el-option
              v-for="option in batchStatusOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="项目级别">
          <el-select v-model="batchForm.project_level" placeholder="选择项目级别" style="width: 100%">
            <el-option
              v-for="item in projectLevelOptions"
              :key="item.id"
              :label="item.label"
              :value="item.id"
            />
          </el-select>
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

    <el-dialog v-model="statusDialogVisible" title="更改状态" width="360px">
      <el-form label-width="90px">
        <el-form-item label="新状态">
          <el-select v-model="statusForm.status" placeholder="选择状态" style="width: 100%">
            <el-option
              v-for="option in batchStatusOptions"
              :key="option.value"
              :label="option.label"
              :value="option.value"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="statusDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="statusSaving" @click="submitStatusChange">
            确认
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
} from "@/api/project-batches";
import { getDictionaryByCode, DICT_CODES } from "@/api/dictionary";

const router = useRouter();
const batchLoading = ref(false);
const batches = ref<any[]>([]);
const statusFilter = ref("");
const showArchived = ref(false);
const projectLevelOptions = ref<any[]>([]);

const batchDialogVisible = ref(false);
const batchSaving = ref(false);
const batchForm = reactive({
  name: "",
  year: new Date().getFullYear(),
  code: "",
  status: "draft",
  project_level: null as number | null,
});

const statusDialogVisible = ref(false);
const statusSaving = ref(false);
const statusForm = reactive({
  id: 0,
  status: "draft",
});

const batchStatusOptions = [
  { value: "draft", label: "草稿" },
  { value: "active", label: "进行中" },
  { value: "reviewing", label: "评审中" },
  { value: "finished", label: "已结束" },
  { value: "archived", label: "已归档" },
];

const getStatusLabel = (status?: string) => {
  const match = batchStatusOptions.find((item) => item.value === status);
  return match ? match.label : "未知";
};

const getStatusTagType = (status?: string) => {
  switch (status) {
    case "active":
      return "success";
    case "reviewing":
      return "warning";
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

const getProjectLevelLabel = (value?: number | null) => {
  if (!value) return "-";
  const match = projectLevelOptions.value.find((item) => item.id === value);
  return match ? match.label : "-";
};

const loadBatches = async () => {
  batchLoading.value = true;
  try {
    const res: any = await listProjectBatches({
      include_archived: showArchived.value ? 1 : 0,
      include_deleted: showArchived.value ? 1 : 0,
    });
    const data = res.data || res;
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
  batchForm.project_level = null;
  batchDialogVisible.value = true;
};

const submitBatch = async () => {
  if (!batchForm.name || !batchForm.code) {
    ElMessage.warning("请填写批次名称和编码");
    return;
  }
  batchSaving.value = true;
  try {
    const res: any = await createProjectBatch({ ...batchForm });
    if (res.code === 200 || res.code === 201) {
      ElMessage.success("批次创建成功");
      batchDialogVisible.value = false;
      await loadBatches();
    }
  } catch (error) {
    console.error(error);
    ElMessage.error("批次创建失败");
  } finally {
    batchSaving.value = false;
  }
};

const openSettings = (row: any) => {
  router.push({ name: "level1-settings-batch-config", params: { id: row.id } });
};

const setRunning = async (row: any) => {
  try {
    await ElMessageBox.confirm("将该批次设为进行中会替换当前批次，是否继续？", "确认操作", {
      type: "warning",
      confirmButtonText: "继续",
      cancelButtonText: "取消",
    });
  } catch {
    return;
  }
  try {
    await updateProjectBatch(row.id, { status: "active" });
    ElMessage.success("已设为进行中");
    await loadBatches();
  } catch (error) {
    console.error(error);
    ElMessage.error("设置失败");
  }
};

const restoreBatch = async (row: any) => {
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
    ElMessage.error("恢复失败");
  }
};

const openStatusDialog = (row: any) => {
  statusForm.id = row.id;
  statusForm.status = row.status || "draft";
  statusDialogVisible.value = true;
};

const submitStatusChange = async () => {
  if (!statusForm.id) return;
  const status = statusForm.status;
  const shouldConfirm = status === "active" || status === "archived" || status === "finished";
  if (shouldConfirm) {
    try {
      const message =
        status === "active"
          ? "切换为进行中会变更当前批次，是否继续？"
          : status === "finished"
            ? "该操作将使批次进入只读状态，是否继续？"
            : "归档后该批次将进入只读状态，是否继续？";
      await ElMessageBox.confirm(message, "确认操作", {
        type: "warning",
        confirmButtonText: "继续",
        cancelButtonText: "取消",
      });
    } catch {
      return;
    }
  }
  statusSaving.value = true;
  try {
    await updateProjectBatch(statusForm.id, { status });
    ElMessage.success("状态已更新");
    statusDialogVisible.value = false;
    await loadBatches();
  } catch (error) {
    console.error(error);
    ElMessage.error("状态更新失败");
  } finally {
    statusSaving.value = false;
  }
};

onMounted(async () => {
  try {
    const res: any = await getDictionaryByCode(DICT_CODES.PROJECT_LEVEL);
    const data = res.data || res;
    projectLevelOptions.value = data?.items || [];
  } catch (error) {
    console.error(error);
  }
  await loadBatches();
});
</script>

<style scoped lang="scss">
@use "./Batches.scss";
</style>
