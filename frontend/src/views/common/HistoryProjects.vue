<template>
  <div class="history-projects-page">
    <el-card class="main-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="header-title">历史项目</span>
            <span class="header-subtitle">仅展示已归档批次</span>
          </div>
          <div class="header-actions">
            <el-select
              v-model="selectedBatchId"
              placeholder="选择归档批次"
              :disabled="archivedBatches.length === 0"
              @change="handleBatchChange"
              style="width: 260px"
            >
              <el-option
                v-for="batch in archivedBatches"
                :key="batch.id"
                :label="formatBatchLabel(batch)"
                :value="batch.id"
              />
            </el-select>
            <el-button :loading="batchLoading" @click="reloadAll">刷新</el-button>
          </div>
        </div>
      </template>

      <el-empty
        v-if="archivedBatches.length === 0"
        description="暂无归档批次"
      />

      <template v-else>
        <div class="batch-summary">
          <div class="summary-item">
            <span class="summary-label">当前批次：</span>
            <span class="summary-value">{{ currentBatchLabel }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">批次编码：</span>
            <span class="summary-value">{{ currentBatch?.code || '-' }}</span>
          </div>
        </div>

        <el-table
          v-loading="projectLoading"
          :data="projects"
          border
          stripe
          style="width: 100%"
        >
          <el-table-column prop="project_no" label="项目编号" width="130" />
          <el-table-column prop="title" label="项目名称" min-width="220" />
          <el-table-column prop="leader_name" label="负责人" width="120" />
          <el-table-column prop="college" label="学院" width="140" />
          <el-table-column prop="level_display" label="级别" width="110" />
          <el-table-column prop="category_display" label="类别" width="120" />
          <el-table-column prop="status_display" label="状态" width="140" />
          <el-table-column label="创建时间" width="170">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-container">
          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :page-sizes="[10, 20, 50]"
            :total="pagination.total"
            layout="total, sizes, prev, pager, next"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </template>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { ElMessage } from "element-plus";
import { listProjectBatches } from "@/api/system-settings/batches";
import { getProjects } from "@/api/projects";

defineOptions({ name: "HistoryProjectsView" });

type BatchRow = {
  id: number;
  name?: string;
  year?: number;
  code?: string;
  status?: string;
};

type ProjectRow = {
  id: number;
  project_no?: string;
  title?: string;
  leader_name?: string;
  college?: string;
  level_display?: string;
  category_display?: string;
  status_display?: string;
  created_at?: string;
};

type ProjectListPayload = {
  results?: ProjectRow[];
  count?: number;
  data?: {
    results?: ProjectRow[];
    count?: number;
  };
};

const archivedBatches = ref<BatchRow[]>([]);
const selectedBatchId = ref<number | null>(null);
const batchLoading = ref(false);
const projectLoading = ref(false);
const projects = ref<ProjectRow[]>([]);

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0,
});

const currentBatch = computed(() =>
  archivedBatches.value.find((item) => item.id === selectedBatchId.value) || null
);

const currentBatchLabel = computed(() => {
  if (!currentBatch.value) return "-";
  return formatBatchLabel(currentBatch.value);
});

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null;

const resolveProjectList = (payload: ProjectListPayload | ProjectRow[]) => {
  if (Array.isArray(payload)) {
    return { results: payload, count: payload.length };
  }
  if (payload && "data" in payload && payload.data) {
    const data = payload.data;
    if (Array.isArray(data.results)) {
      return {
        results: data.results,
        count: data.count ?? data.results.length,
      };
    }
  }
  if (payload && Array.isArray(payload.results)) {
    return {
      results: payload.results,
      count: payload.count ?? payload.results.length,
    };
  }
  return { results: [], count: 0 };
};

const formatBatchLabel = (batch: BatchRow) =>
  `${batch.name || "未命名"} ${batch.year ? `(${batch.year})` : ""}`.trim();

const formatDate = (value?: string) => {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  const yyyy = date.getFullYear();
  const mm = String(date.getMonth() + 1).padStart(2, "0");
  const dd = String(date.getDate()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
};

const loadBatches = async () => {
  batchLoading.value = true;
  try {
    const res = await listProjectBatches({ include_archived: 1 });
    const data = isRecord(res) && "data" in res ? (res as { data?: BatchRow[] }).data : res;
    const list = Array.isArray(data) ? data : [];
    archivedBatches.value = list
      .filter((item) => item.status === "archived")
      .sort((a, b) => (b.year || 0) - (a.year || 0));
    if (archivedBatches.value.length > 0 && !selectedBatchId.value) {
      selectedBatchId.value = archivedBatches.value[0].id;
    }
  } catch (error) {
    console.error(error);
    ElMessage.error("加载归档批次失败");
  } finally {
    batchLoading.value = false;
  }
};

const loadProjects = async () => {
  if (!selectedBatchId.value) {
    projects.value = [];
    pagination.total = 0;
    return;
  }

  projectLoading.value = true;
  try {
    const res = (await getProjects({
      page: pagination.page,
      page_size: pagination.pageSize,
      history_batch_id: selectedBatchId.value,
    })) as ProjectListPayload | ProjectRow[];
    const normalized = resolveProjectList(res);
    projects.value = normalized.results;
    pagination.total = normalized.count;
  } catch (error) {
    console.error(error);
    ElMessage.error("加载历史项目失败");
  } finally {
    projectLoading.value = false;
  }
};

const handleBatchChange = () => {
  pagination.page = 1;
  loadProjects();
};

const handleSizeChange = (size: number) => {
  pagination.pageSize = size;
  pagination.page = 1;
  loadProjects();
};

const handleCurrentChange = (page: number) => {
  pagination.page = page;
  loadProjects();
};

const reloadAll = async () => {
  await loadBatches();
  await loadProjects();
};

onMounted(async () => {
  await loadBatches();
  await loadProjects();
});
</script>

<style scoped lang="scss">
.history-projects-page {
  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;

    .header-left {
      display: flex;
      align-items: baseline;
      gap: 12px;

      .header-title {
        font-size: 18px;
        font-weight: 600;
        color: #1f2937;
      }

      .header-subtitle {
        font-size: 13px;
        color: #6b7280;
      }
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 12px;
    }
  }

  .batch-summary {
    display: flex;
    gap: 24px;
    padding: 12px 16px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    margin-bottom: 16px;

    .summary-item {
      font-size: 13px;
      color: #475569;

      .summary-label {
        color: #64748b;
      }

      .summary-value {
        font-weight: 600;
        margin-left: 4px;
      }
    }
  }

  .pagination-container {
    display: flex;
    justify-content: flex-end;
    padding-top: 16px;
  }
}
</style>
