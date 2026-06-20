<template>
  <div class="publication-page page-shell">
    <el-row :gutter="16" class="summary-row">
      <el-col
        v-for="item in summaryCards"
        :key="item.key"
        :xs="24"
        :sm="12"
        :md="6"
        :lg="6"
        :xl="6"
      >
        <MetricCard
          :label="item.label"
          :value="item.value"
          :hint="item.hint"
          :tone="item.tone"
          density="compact"
        />
      </el-col>
    </el-row>

    <div class="toolbar-panel">
      <div class="filter-copy">
        <strong>项目筛选</strong>
        <span>支持按项目、编号、负责人和发布状态快速定位</span>
      </div>
      <div class="toolbar-actions">
        <el-input
          v-model="filters.search"
          placeholder="搜索项目 / 编号 / 负责人"
          clearable
          style="width: 260px"
          @keyup.enter="loadProjects"
        />
        <el-select
          v-model="filters.publish_status"
          placeholder="发布状态"
          clearable
          style="width: 180px"
          @change="loadProjects"
        >
          <el-option label="未进入发布" value="NOT_READY" />
          <el-option label="学院已推荐" value="RECOMMENDED" />
          <el-option label="学校已确认" value="CONFIRMED" />
          <el-option label="已发布" value="PUBLISHED" />
        </el-select>
        <el-button @click="loadProjects">查询</el-button>
      </div>
    </div>

    <PanelCard title="项目发布列表" :caption="panelCaption">
      <template #actions>
        <el-button @click="downloadPublication">生成导出任务</el-button>
        <el-button v-if="isSchoolAdminView" type="warning" @click="publishResults">发布公示</el-button>
        <el-button v-if="isSchoolAdminView" type="success" @click="confirmResults">确认结果</el-button>
        <el-button type="primary" @click="saveRecommendations">保存推荐</el-button>
      </template>
      <el-table
        v-loading="loading"
        :data="projects"
        stripe
        row-key="id"
        @selection-change="selectedRows = $event"
      >
        <el-table-column type="selection" width="48" />
        <el-table-column prop="project_no" label="项目编号" width="150" />
        <el-table-column prop="title" label="项目名称" min-width="240" show-overflow-tooltip />
        <el-table-column prop="leader_name" label="负责人" width="100" />
        <el-table-column prop="college" label="学院" width="150" show-overflow-tooltip />
        <el-table-column label="推荐排序" width="132">
          <template #default="{ row }">
            <el-input-number v-model="row.recommendation_rank" :min="1" size="small" />
          </template>
        </el-table-column>
        <el-table-column label="推荐级别" width="150">
          <template #default="{ row }">
            <el-select
              v-model="row.recommended_level"
              placeholder="推荐级别"
              clearable
              size="small"
            >
              <el-option
                v-for="item in levelOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="推荐经费" width="142">
          <template #default="{ row }">
            <el-input-number v-model="row.recommended_budget" :min="0" size="small" />
          </template>
        </el-table-column>
        <el-table-column label="最终级别" width="150">
          <template #default="{ row }">
            <el-select
              v-model="row.final_level"
              placeholder="最终级别"
              clearable
              size="small"
              :disabled="!isSchoolAdminView"
            >
              <el-option
                v-for="item in levelOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="最终经费" width="142">
          <template #default="{ row }">
            <el-input-number
              v-model="row.final_budget"
              :min="0"
              size="small"
              :disabled="!isSchoolAdminView"
            />
          </template>
        </el-table-column>
        <el-table-column label="发布状态" width="132">
          <template #default="{ row }">
            <StatusPill :status="row.publish_status" :label="row.publish_status_display || row.publish_status" />
          </template>
        </el-table-column>
        <el-table-column label="推荐意见" min-width="220">
          <template #default="{ row }">
            <el-input v-model="row.recommendation_comment" size="small" placeholder="填写推荐意见" />
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-line">
        <span>已选择 {{ selectedRows.length }} 个项目</span>
        <el-pagination
          v-model:current-page="filters.page"
          v-model:page-size="filters.page_size"
          layout="total, sizes, prev, pager, next"
          :total="total"
          @current-change="loadProjects"
          @size-change="loadProjects"
        />
      </div>
    </PanelCard>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { useRoute } from "vue-router";
import { ElMessage } from "element-plus";
import { DICT_CODES, type DictionaryItem } from "@/api/dictionaries";
import MetricCard from "@/components/common/MetricCard.vue";
import PanelCard from "@/components/common/PanelCard.vue";
import StatusPill from "@/components/common/StatusPill.vue";
import { useDictionary } from "@/composables/useDictionary";
import {
  confirmPublicationResults,
  exportPublicationResultsTask,
  getPublicationCenter,
  publishEstablishmentResults,
  savePublicationRecommendations,
} from "@/api/projects/admin";

type ApiResponse<T> = { code?: number; data?: T; message?: string };
type PublicationMutationResult = { updated?: number };
type MetricTone = "primary" | "success" | "warning" | "info" | "danger";
type ProjectRow = {
  id: number;
  project_no?: string;
  title?: string;
  leader_name?: string;
  college?: string;
  recommendation_rank?: number;
  recommended_level?: string;
  recommended_budget?: number | null;
  recommended_level_display?: string;
  final_level?: string;
  final_budget?: number | null;
  final_level_display?: string;
  publish_status?: string;
  publish_status_display?: string;
  recommendation_comment?: string;
  [key: string]: unknown;
};

const route = useRoute();
const { loadDictionaries, getOptions } = useDictionary();
const loading = ref(false);
const projects = ref<ProjectRow[]>([]);
const selectedRows = ref<ProjectRow[]>([]);
const total = ref(0);
const filters = reactive({
  search: "",
  publish_status: "",
  page: 1,
  page_size: 10,
});

const isSchoolAdminView = computed(() => route.path.startsWith("/level1-admin"));
const levelOptions = computed(
  () => getOptions(DICT_CODES.PROJECT_LEVEL) as DictionaryItem[]
);
const panelCaption = computed(() =>
  isSchoolAdminView.value
    ? "选中项目后可执行保存推荐、确认结果和发布公示；未选中时默认处理当前页。"
    : "选中项目后可维护学院推荐排序、推荐级别、推荐经费和推荐意见；未选中时默认处理当前页。"
);

const getPayload = <T,>(res: unknown): T | undefined => {
  const response = res as ApiResponse<T>;
  return response?.data;
};

const toNumberOrNull = (value: unknown) => {
  if (value === null || value === undefined || value === "") return null;
  const numericValue = Number(value);
  return Number.isFinite(numericValue) ? numericValue : null;
};

const normalizeRows = (rows: ProjectRow[]) =>
  rows.map((row) => ({
    ...row,
    recommended_level: row.recommended_level || "",
    recommended_budget: toNumberOrNull(row.recommended_budget),
    final_level: row.final_level || "",
    final_budget: toNumberOrNull(row.final_budget),
  }));

const normalizeSubmissionRows = (rows: ProjectRow[]) =>
  rows.map((row) => ({
    project_id: row.id,
    recommendation_rank: row.recommendation_rank,
    recommended_level: row.recommended_level || "",
    recommended_budget: row.recommended_budget ?? "",
    recommendation_comment: row.recommendation_comment || "",
    final_level: row.final_level || row.recommended_level || "",
    final_budget: row.final_budget ?? row.recommended_budget ?? "",
  }));

const summaryCards = computed<
  { key: string; label: string; value: number; hint: string; tone: MetricTone }[]
>(() => {
  const countByStatus = (status: string) =>
    projects.value.filter((item) => item.publish_status === status).length;
  return [
    { key: "total", label: "当前页项目", value: projects.value.length, hint: `共 ${total.value} 个候选项目`, tone: "primary" },
    { key: "recommended", label: "学院已推荐", value: countByStatus("RECOMMENDED"), hint: "等待学校确认", tone: "warning" },
    { key: "confirmed", label: "学校已确认", value: countByStatus("CONFIRMED"), hint: "可进入公示发布", tone: "info" },
    { key: "published", label: "已发布", value: countByStatus("PUBLISHED"), hint: "学生端可查看结果", tone: "success" },
  ];
});

const loadProjects = async () => {
  loading.value = true;
  try {
    const data = getPayload<{ results: ProjectRow[]; total: number }>(
      await getPublicationCenter(filters)
    );
    projects.value = normalizeRows(data?.results ?? []);
    total.value = data?.total ?? 0;
  } finally {
    loading.value = false;
  }
};

const selectedOrAll = () => (selectedRows.value.length ? selectedRows.value : projects.value);

const saveRecommendations = async () => {
  const rows = normalizeSubmissionRows(selectedOrAll());
  const data = getPayload<PublicationMutationResult>(
    await savePublicationRecommendations({ items: rows })
  );
  const updated = data?.updated ?? 0;
  if (updated === 0) {
    ElMessage.warning("当前项目未更新，请确认项目状态或管理范围");
  } else {
    ElMessage.success(`推荐信息已保存，共更新 ${updated} 个项目`);
  }
  await loadProjects();
};

const confirmResults = async () => {
  const rows = normalizeSubmissionRows(selectedOrAll());
  await confirmPublicationResults({ items: rows });
  ElMessage.success("最终结果已确认");
  await loadProjects();
};

const publishResults = async () => {
  const rows = selectedOrAll();
  if (!rows.length) {
    ElMessage.warning("请选择要发布的项目");
    return;
  }
  await publishEstablishmentResults({ project_ids: rows.map((row) => row.id) });
  ElMessage.success("立项结果已发布，公示公告已同步生成");
  await loadProjects();
};

const downloadPublication = async () => {
  await exportPublicationResultsTask();
  ElMessage.success("公示导出任务已生成，可在任务中心下载");
};

onMounted(async () => {
  await loadDictionaries([DICT_CODES.PROJECT_LEVEL]);
  await loadProjects();
});
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.summary-row {
  row-gap: 12px;
}

.filter-copy {
  display: flex;
  flex-direction: column;
  gap: 2px;

  strong {
    color: $slate-900;
    font-size: 15px;
  }

  span {
    color: $slate-500;
    font-size: 13px;
  }
}

.pagination-line {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-top: 18px;
  color: $slate-500;
  font-size: 13px;
}
</style>
