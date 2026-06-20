<template>
  <div class="task-center-page page-shell">
    <el-row :gutter="16" class="summary-row">
      <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="6">
        <MetricCard
          label="后台任务"
          :value="tasks.length"
          hint="当前可见任务"
          density="compact"
        />
      </el-col>
      <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="6">
        <MetricCard
          label="执行成功"
          :value="successTasks"
          hint="可下载结果文件"
          tone="success"
          density="compact"
        />
      </el-col>
      <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="6">
        <MetricCard
          label="执行异常"
          :value="failedTasks"
          hint="需关注失败原因"
          tone="danger"
          density="compact"
        />
      </el-col>
      <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="6">
        <MetricCard
          label="审计记录"
          :value="logs.length"
          hint="关键操作留痕"
          tone="info"
          density="compact"
        />
      </el-col>
    </el-row>

    <PanelCard title="任务中心" caption="集中查看后台任务和关键操作审计记录。">
      <template #actions>
        <el-button v-if="showImportCenterLink" @click="goDataImportCenter">
          数据导入中心
        </el-button>
        <el-button type="primary" @click="loadAll">刷新</el-button>
      </template>
      <el-tabs v-model="activeTab" class="task-tabs">
        <el-tab-pane label="后台任务" name="tasks">
          <el-table :data="tasks" stripe v-loading="taskLoading">
            <el-table-column prop="title" label="任务名称" min-width="190" />
            <el-table-column prop="task_type_display" label="类型" width="110" />
            <el-table-column label="状态" width="130">
              <template #default="{ row }">
                <StatusPill :status="row.status" :label="row.status_display || row.status" />
              </template>
            </el-table-column>
            <el-table-column label="进度" width="170">
              <template #default="{ row }">
                <el-progress :percentage="row.progress || 0" />
              </template>
            </el-table-column>
            <el-table-column prop="message" label="消息" min-width="170" show-overflow-tooltip />
            <el-table-column label="结果文件" width="130">
              <template #default="{ row }">
                <el-button
                  v-if="row.result_file_url"
                  type="primary"
                  link
                  @click="downloadResultFile(row)"
                  :loading="downloadingTaskId === row.id"
                >
                  下载
                </el-button>
                <span v-else class="muted">-</span>
              </template>
            </el-table-column>
            <el-table-column prop="created_by_name" label="创建人" width="120" />
            <el-table-column prop="created_at" label="创建时间" width="180" />
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="操作日志" name="logs">
          <el-table :data="logs" stripe v-loading="logLoading">
            <el-table-column prop="module" label="模块" width="130" />
            <el-table-column prop="action" label="动作" width="160" />
            <el-table-column prop="target_name" label="对象" min-width="220" show-overflow-tooltip />
            <el-table-column label="状态" width="110">
              <template #default="{ row }">
                <StatusPill :status="row.status" :label="row.status_display || row.status" />
              </template>
            </el-table-column>
            <el-table-column prop="operator_name" label="操作人" width="120" />
            <el-table-column prop="ip_address" label="IP" width="130" />
            <el-table-column prop="created_at" label="操作时间" width="180" />
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </PanelCard>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import MetricCard from "@/components/common/MetricCard.vue";
import PanelCard from "@/components/common/PanelCard.vue";
import StatusPill from "@/components/common/StatusPill.vue";
import { downloadTaskResult, getOperationLogs, getTaskList } from "@/api/operations";
import { saveBlob } from "@/utils/common";

type ApiResponse<T> = { data?: T };
type TaskRow = {
  id: number;
  title?: string;
  task_type?: string;
  task_type_display?: string;
  status?: string;
  status_display?: string;
  progress?: number;
  message?: string;
  result_file_url?: string;
  result_file_name?: string;
  created_by_name?: string;
  created_at?: string;
};
type LogRow = {
  module?: string;
  action?: string;
  target_name?: string;
  status?: string;
  status_display?: string;
  operator_name?: string;
  ip_address?: string;
  created_at?: string;
};

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null;

const route = useRoute();
const router = useRouter();
const activeTab = ref("tasks");
const tasks = ref<TaskRow[]>([]);
const logs = ref<LogRow[]>([]);
const taskLoading = ref(false);
const logLoading = ref(false);
const downloadingTaskId = ref<number | null>(null);

const payload = <T,>(res: unknown): T | undefined => {
  if (isRecord(res) && "data" in res) {
    return (res as ApiResponse<T>).data;
  }
  return res as T;
};

const normalizeList = <T,>(data?: { results?: T[] } | T[]) => {
  if (Array.isArray(data)) return data;
  return Array.isArray(data?.results) ? data.results : [];
};

const successTasks = computed(() => tasks.value.filter((task) => task.status === "SUCCESS").length);
const failedTasks = computed(() => tasks.value.filter((task) => task.status === "FAILED").length);
const showImportCenterLink = computed(() => route.path.startsWith("/level1-admin"));

const downloadResultFile = async (row: TaskRow) => {
  if (!row.id) return;
  downloadingTaskId.value = row.id;
  try {
    const blob = (await downloadTaskResult(row.id)) as Blob;
    saveBlob(blob, row.result_file_name || row.title || "任务结果文件");
  } catch {
    ElMessage.error("下载任务结果失败");
  } finally {
    downloadingTaskId.value = null;
  }
};

const loadTasks = async () => {
  taskLoading.value = true;
  try {
    tasks.value = normalizeList<TaskRow>(
      payload<{ results?: TaskRow[] } | TaskRow[]>(await getTaskList({ page_size: 50 }))
    ).filter((task) => task.task_type !== "IMPORT");
  } finally {
    taskLoading.value = false;
  }
};

const loadLogs = async () => {
  logLoading.value = true;
  try {
    logs.value = normalizeList<LogRow>(
      payload<{ results?: LogRow[] } | LogRow[]>(await getOperationLogs({ page_size: 50 }))
    );
  } finally {
    logLoading.value = false;
  }
};

const loadAll = async () => {
  await Promise.all([loadTasks(), loadLogs()]);
};

const goDataImportCenter = () => {
  void router.push("/level1-admin/data-center");
};

onMounted(loadAll);
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.summary-row {
  row-gap: 12px;
}

.task-tabs {
  :deep(.el-tabs__content) {
    padding-top: 10px;
  }

  :deep(.el-tabs__header) {
    margin-bottom: 10px;
  }
}

.muted {
  color: $slate-400;
}
</style>
