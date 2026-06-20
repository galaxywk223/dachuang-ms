<template>
  <div class="data-center-page page-shell">
    <el-row :gutter="16" class="summary-row">
      <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="6">
        <MetricCard
          label="导入类型"
          :value="kinds.length"
          hint="统一模板入口"
          density="compact"
        />
      </el-col>
      <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="6">
        <MetricCard
          label="任务总数"
          :value="tasks.length"
          hint="当前可见任务"
          tone="info"
          density="compact"
        />
      </el-col>
      <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="6">
        <MetricCard
          label="成功任务"
          :value="successTasks"
          hint="已生成结果回执"
          tone="success"
          density="compact"
        />
      </el-col>
      <el-col :xs="24" :sm="12" :md="6" :lg="6" :xl="6">
        <MetricCard
          label="异常任务"
          :value="failedTasks"
          hint="需查看失败原因"
          tone="danger"
          density="compact"
        />
      </el-col>
    </el-row>

    <PanelCard title="数据导入中心" caption="统一管理模板下载、文件预校验和导入任务创建。">
      <template #actions>
        <el-button type="primary" @click="loadAll">刷新数据</el-button>
      </template>

      <div class="import-workbench">
        <div class="import-controls">
          <el-form label-position="top" class="import-form">
            <el-form-item label="导入类型">
              <el-select
                v-model="selectedKind"
                placeholder="选择导入类型"
                filterable
                @change="handleKindChange"
              >
                <el-option
                  v-for="kind in kinds"
                  :key="kind.kind"
                  :label="kind.title"
                  :value="kind.kind"
                />
              </el-select>
            </el-form-item>

            <div class="kind-summary" v-if="selectedKindInfo">
              <div class="kind-summary-title">{{ selectedKindInfo.title }}</div>
              <div class="kind-summary-fields">
                <el-tag
                  v-for="header in selectedKindInfo.headers"
                  :key="header"
                  size="small"
                  effect="plain"
                >
                  {{ header }}
                </el-tag>
              </div>
            </div>

            <div class="control-row">
              <el-button
                :disabled="!selectedKind"
                @click="downloadTemplate(selectedKind)"
              >
                下载模板
              </el-button>
              <el-button
                :disabled="!selectedFile"
                :loading="previewLoading"
                @click="runPreview"
              >
                预校验
              </el-button>
              <el-button
                type="primary"
                :disabled="!canImport"
                :loading="importLoading"
                @click="confirmImport"
              >
                确认导入
              </el-button>
            </div>
          </el-form>

          <el-upload
            ref="uploadRef"
            class="import-upload"
            drag
            action="#"
            :auto-upload="false"
            :limit="1"
            :disabled="!selectedKind || previewLoading || importLoading"
            accept=".xlsx,.xlsm,.xltx,.xltm"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">
              将文件拖到此处，或 <em>点击上传</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                {{ selectedKind ? "上传后自动执行预校验" : "先选择导入类型" }}
              </div>
            </template>
          </el-upload>
        </div>

        <div class="preview-panel">
          <div class="preview-heading">
            <span>预校验结果</span>
            <el-tag v-if="previewResult" :type="previewResult.valid ? 'success' : 'danger'">
              {{ previewResult.valid ? "可导入" : "不可导入" }}
            </el-tag>
          </div>

          <el-empty
            v-if="!previewResult"
            description="暂无预校验结果"
            :image-size="80"
          />
          <el-descriptions v-else :column="2" border size="small">
            <el-descriptions-item label="文件">
              {{ selectedFile?.name || "-" }}
            </el-descriptions-item>
            <el-descriptions-item label="总行数">
              {{ previewResult.total_rows ?? 0 }}
            </el-descriptions-item>
            <el-descriptions-item label="缺失字段" :span="2">
              <span v-if="!previewResult.missing_headers.length" class="muted">
                无
              </span>
              <div v-else class="tag-list">
                <el-tag
                  v-for="header in previewResult.missing_headers"
                  :key="header"
                  type="danger"
                  size="small"
                  effect="plain"
                >
                  {{ header }}
                </el-tag>
              </div>
            </el-descriptions-item>
            <el-descriptions-item label="表头" :span="2">
              <div class="tag-list" v-if="previewResult.headers.length">
                <el-tag
                  v-for="header in previewResult.headers"
                  :key="header"
                  size="small"
                  effect="plain"
                >
                  {{ header }}
                </el-tag>
              </div>
              <span v-else class="muted">-</span>
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
    </PanelCard>

    <PanelCard title="导入任务" caption="仅展示数据导入中心创建的导入任务。">
      <el-table :data="tasks" stripe v-loading="loading">
        <el-table-column prop="title" label="任务" min-width="190" />
        <el-table-column prop="task_type_display" label="类型" width="110" />
        <el-table-column label="状态" width="130">
          <template #default="{ row }">
            <StatusPill :status="row.status" :label="row.status_display || row.status" />
          </template>
        </el-table-column>
        <el-table-column label="进度" width="180">
          <template #default="{ row }">
            <el-progress :percentage="row.progress || 0" />
          </template>
        </el-table-column>
        <el-table-column prop="message" label="消息" min-width="180" show-overflow-tooltip />
        <el-table-column label="结果" min-width="220">
          <template #default="{ row }">
            <span class="result-text">{{ formatResult(row.result) }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
      </el-table>
    </PanelCard>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import type { UploadFile, UploadInstance, UploadRawFile } from "element-plus";
import { UploadFilled } from "@element-plus/icons-vue";
import MetricCard from "@/components/common/MetricCard.vue";
import PanelCard from "@/components/common/PanelCard.vue";
import StatusPill from "@/components/common/StatusPill.vue";
import {
  downloadImportTemplate,
  executeImport,
  getImportKinds,
  getTaskList,
  previewImport,
} from "@/api/operations";
import { saveBlob } from "@/utils/common";

type ApiResponse<T> = { data?: T; message?: string };
type ImportKind = { kind: string; title: string; headers: string[] };
type TaskRow = {
  title?: string;
  task_type?: string;
  task_type_display?: string;
  status?: string;
  status_display?: string;
  progress?: number;
  message?: string;
  result?: unknown;
  created_at?: string;
};
type PreviewResult = {
  headers: string[];
  total_rows: number;
  missing_headers: string[];
  valid: boolean;
};

const route = useRoute();
const router = useRouter();
const kinds = ref<ImportKind[]>([]);
const tasks = ref<TaskRow[]>([]);
const loading = ref(false);
const selectedKind = ref("");
const selectedFile = ref<UploadRawFile | null>(null);
const previewResult = ref<PreviewResult | null>(null);
const previewLoading = ref(false);
const importLoading = ref(false);
const uploadRef = ref<UploadInstance>();

const payload = <T,>(res: unknown): T | undefined => (res as ApiResponse<T>)?.data;

const successTasks = computed(() => tasks.value.filter((task) => task.status === "SUCCESS").length);
const failedTasks = computed(() => tasks.value.filter((task) => task.status === "FAILED").length);
const selectedKindInfo = computed(() =>
  kinds.value.find((kind) => kind.kind === selectedKind.value)
);
const canImport = computed(() =>
  Boolean(selectedKind.value && selectedFile.value && previewResult.value?.valid)
);

const getQueryKind = () => {
  const kind = route.query.kind;
  return Array.isArray(kind) ? kind[0] || "" : kind || "";
};

const applySelectedKind = (kind?: string) => {
  const nextKind = kind && kinds.value.some((item) => item.kind === kind)
    ? kind
    : kinds.value[0]?.kind || "";
  if (selectedKind.value === nextKind) return;
  selectedKind.value = nextKind;
  selectedFile.value = null;
  previewResult.value = null;
  uploadRef.value?.clearFiles();
};

const loadKinds = async () => {
  kinds.value = payload<ImportKind[]>(await getImportKinds()) ?? [];
  applySelectedKind(getQueryKind());
};

const loadTasks = async () => {
  loading.value = true;
  try {
    const data = payload<{ results?: TaskRow[] } | TaskRow[]>(
      await getTaskList({ task_type: "IMPORT" })
    );
    tasks.value = Array.isArray(data) ? data : data?.results ?? [];
  } finally {
    loading.value = false;
  }
};

const loadAll = async () => {
  await Promise.all([loadKinds(), loadTasks()]);
};

const downloadTemplate = async (kind: string) => {
  if (!kind) return;
  const blob = (await downloadImportTemplate(kind)) as Blob;
  saveBlob(blob, `${kind}_template.xlsx`);
};

const handleKindChange = (kind: string) => {
  selectedFile.value = null;
  previewResult.value = null;
  uploadRef.value?.clearFiles();
  void router.replace({
    query: {
      ...route.query,
      kind,
    },
  });
};

const handleFileChange = (file: UploadFile) => {
  selectedFile.value = file.raw ?? null;
  previewResult.value = null;
  void runPreview();
};

const handleFileRemove = () => {
  selectedFile.value = null;
  previewResult.value = null;
};

const buildImportFormData = () => {
  if (!selectedKind.value || !selectedFile.value) return null;
  const formData = new FormData();
  formData.append("kind", selectedKind.value);
  formData.append("file", selectedFile.value);
  return formData;
};

const runPreview = async () => {
  const formData = buildImportFormData();
  if (!formData) {
    ElMessage.warning("请选择导入类型并上传文件");
    return;
  }
  previewLoading.value = true;
  try {
    const preview = payload<PreviewResult>(await previewImport(formData));
    previewResult.value = {
      headers: preview?.headers ?? [],
      total_rows: preview?.total_rows ?? 0,
      missing_headers: preview?.missing_headers ?? [],
      valid: Boolean(preview?.valid),
    };
    if (!previewResult.value.valid) {
      ElMessage.error("预校验未通过，请检查缺失字段");
    }
  } finally {
    previewLoading.value = false;
  }
};

const confirmImport = async () => {
  if (!canImport.value) {
    ElMessage.warning("预校验通过后才能确认导入");
    return;
  }
  const formData = buildImportFormData();
  if (!formData) return;
  importLoading.value = true;
  try {
    await executeImport(formData);
    ElMessage.success(
      `已创建导入任务，共 ${previewResult.value?.total_rows ?? 0} 行`
    );
    selectedFile.value = null;
    previewResult.value = null;
    uploadRef.value?.clearFiles();
    await loadTasks();
  } finally {
    importLoading.value = false;
  }
};

const formatResult = (result?: Record<string, unknown>) => {
  if (!result || Object.keys(result).length === 0) return "-";
  const created = result.created;
  const updated = result.updated;
  const errors = Array.isArray(result.errors) ? result.errors.length : 0;
  return `新增 ${created ?? 0}，更新 ${updated ?? 0}，错误 ${errors}`;
};

watch(
  () => route.query.kind,
  () => {
    if (kinds.value.length) {
      applySelectedKind(getQueryKind());
    }
  }
);

onMounted(loadAll);
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.summary-row {
  row-gap: 12px;
}

.import-workbench {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(360px, 0.9fr);
  gap: 18px;
}

.import-controls {
  display: grid;
  gap: 16px;
}

.import-form {
  display: grid;
  gap: 14px;
}

.kind-summary {
  padding: 14px;
  border: 1px solid $slate-200;
  border-radius: $radius-lg;
  background: $slate-50;
}

.kind-summary-title {
  margin-bottom: 10px;
  color: $slate-900;
  font-size: 15px;
  font-weight: 800;
}

.kind-summary-fields,
.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.control-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.import-upload {
  :deep(.el-upload) {
    width: 100%;
  }

  :deep(.el-upload-dragger) {
    width: 100%;
  }
}

.preview-panel {
  min-width: 0;
  padding: 16px;
  border: 1px solid $slate-200;
  border-radius: $radius-lg;
  background: #ffffff;
}

.preview-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
  color: $slate-900;
  font-size: 15px;
  font-weight: 800;
}

.result-text {
  color: $slate-600;
  font-size: 13px;
}

.muted {
  color: $slate-400;
}

@media (max-width: 900px) {
  .import-workbench {
    grid-template-columns: 1fr;
  }
}
</style>
