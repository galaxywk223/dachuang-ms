<template>
  <div class="expert-assignment-container">
    <el-card class="main-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="header-title">{{ pageTitle }}</span>
          </div>
          <div class="header-actions">
            <el-select
              v-model="selectedGroup"
              placeholder="选择专家组"
              style="width: 200px"
              class="mr-2"
            >
              <el-option
                v-for="group in groups"
                :key="group.id"
                :label="group.name"
                :value="group.id"
              />
            </el-select>
            <el-select
              v-model="reviewType"
              placeholder="审核类型"
              style="width: 150px"
              class="mr-2"
              @change="handleReviewTypeChange"
            >
              <el-option label="申报审核" value="APPLICATION" />
              <el-option label="中期审核" value="MID_TERM" />
              <el-option label="结题审核" value="CLOSURE" />
            </el-select>
            <el-button
              type="primary"
              @click="handleAssign"
              :disabled="!selectedGroup || selectedProjects.length === 0"
              :loading="assigning"
            >
              批量分配 ({{ selectedProjects.length }})
            </el-button>
          </div>
        </div>
      </template>

      <!-- Filters -->
      <div class="filter-container">
        <el-input
          v-model="searchQuery"
          placeholder="搜索项目名称/编号"
          style="width: 300px"
          clearable
          @clear="fetchProjects"
          @keyup.enter="fetchProjects"
        >
          <template #append>
            <el-button @click="fetchProjects"
              ><el-icon><Search /></el-icon
            ></el-button>
          </template>
        </el-input>

        <el-select
          v-model="statusFilter"
          placeholder="项目状态"
          class="ml-2"
          @change="fetchProjects"
          clearable
        >
          <el-option label="待提交" value="DRAFT" />
          <el-option label="已提交" value="SUBMITTED" />
          <el-option label="学院审核中" value="COLLEGE_AUDITING" />
          <el-option label="一级审核中" value="LEVEL1_AUDITING" />
          <el-option label="进行中" value="IN_PROGRESS" />
          <el-option label="中期审核中" value="MID_TERM_REVIEWING" />
          <el-option label="中期已提交" value="MID_TERM_SUBMITTED" />
          <el-option label="结题二级审核中" value="CLOSURE_LEVEL2_REVIEWING" />
          <el-option label="结题一级审核中" value="CLOSURE_LEVEL1_REVIEWING" />
        </el-select>
      </div>

      <el-table
        v-loading="loading"
        :data="projects"
        style="width: 100%"
        stripe
        border
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="project_no" label="项目编号" width="150" />
        <el-table-column
          prop="title"
          label="项目名称"
          min-width="200"
          show-overflow-tooltip
        />
        <el-table-column prop="leader_name" label="负责人" width="120" />
        <el-table-column prop="college" label="学院" width="150" />
        <el-table-column prop="level_display" label="级别" width="100" />
        <el-table-column prop="status_display" label="当前状态" width="120">
          <template #default="scope">
            <el-tag>{{ scope.row.status_display }}</el-tag>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container mt-4">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="fetchProjects"
          @current-change="fetchProjects"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useRoute } from "vue-router";
import { Search } from "@element-plus/icons-vue";
import { ElMessage, ElMessageBox } from "element-plus";
import { getPendingReviews, type PendingReview } from "@/api/reviews";
import request from "@/utils/request";

defineOptions({
  name: "ExpertAssignmentView",
});

type ProjectRow = {
  id: number;
  review_id?: number;
  workflow_node_id?: number | null;
  project_no?: string;
  title?: string;
  leader_name?: string;
  college?: string;
  level_display?: string;
  status_display?: string;
};

type ReviewListPayload = {
  results?: PendingReview[];
  count?: number;
  data?: {
    results?: PendingReview[];
    count?: number;
  };
};

type GroupRow = {
  id: number;
  name: string;
};

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null;

const resolveList = <T>(payload: unknown): T[] => {
  if (Array.isArray(payload)) return payload as T[];
  if (isRecord(payload) && Array.isArray(payload.results)) {
    return payload.results as T[];
  }
  if (
    isRecord(payload) &&
    isRecord(payload.data) &&
    Array.isArray(payload.data.results)
  ) {
    return payload.data.results as T[];
  }
  if (isRecord(payload) && Array.isArray(payload.data)) {
    return payload.data as T[];
  }
  return [];
};

const buildProjectRows = (reviews: PendingReview[]): ProjectRow[] =>
  reviews.map((review) => {
    const projectInfo = isRecord(review.project_info)
      ? (review.project_info as ProjectRow)
      : ({} as ProjectRow);
    const projectId =
      typeof projectInfo.id === "number" ? projectInfo.id : review.project;
    return {
      ...projectInfo,
      id: projectId,
      review_id: review.id,
      workflow_node_id: review.workflow_node ?? null,
    };
  });

const resolveReviewCount = (payload: ReviewListPayload) => {
  if (typeof payload.count === "number") return payload.count;
  if (isRecord(payload.data) && typeof payload.data.count === "number") {
    return payload.data.count;
  }
  return 0;
};

const getErrorMessage = (error: unknown, fallback: string) => {
  if (error instanceof Error) {
    return error.message || fallback;
  }
  if (typeof error === "string") {
    return error || fallback;
  }
  return fallback;
};

const loading = ref(false);
const assigning = ref(false);
const projects = ref<ProjectRow[]>([]);
const groups = ref<GroupRow[]>([]);
const total = ref(0);
const currentPage = ref(1);
const pageSize = ref(20);
const route = useRoute();
const pageTitle = computed(
  () => (route.meta.title as string) || "专家评审分配"
);
// Filters and Selections
const searchQuery = ref("");
const statusFilter = ref("");
const selectedGroup = ref<number | null>(null);
const reviewType = ref("APPLICATION");
const selectedProjects = ref<ProjectRow[]>([]);

const fetchGroups = async () => {
  try {
    const res = await request.get("/reviews/groups/");
    groups.value = resolveList<GroupRow>(res);
  } catch (error: unknown) {
    console.error(error);
  }
};

const fetchProjects = async () => {
  loading.value = true;
  try {
    const params: Record<string, string | number> = {
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchQuery.value,
      review_type: reviewType.value,
      exclude_expert_assigned: 1,
    };
    if (statusFilter.value) {
      params.project__status = statusFilter.value;
    }
    if (!params.search) delete params.search;
    const reviewRes = await getPendingReviews(params);
    const payload =
      isRecord(reviewRes) && "data" in reviewRes ? reviewRes.data : reviewRes;
    const reviewPayload = isRecord(payload)
      ? (payload as ReviewListPayload)
      : {};
    const reviews = resolveList<PendingReview>(reviewPayload);
    projects.value = buildProjectRows(reviews);
    total.value = resolveReviewCount(reviewPayload);
  } catch (error: unknown) {
    console.error(error);
    ElMessage.error("获取项目失败");
  } finally {
    loading.value = false;
  }
};

const handleReviewTypeChange = () => {
  statusFilter.value = "";
  selectedProjects.value = [];
  currentPage.value = 1;
  fetchProjects();
};

const handleSelectionChange = (val: ProjectRow[]) => {
  selectedProjects.value = val;
};

const handleAssign = () => {
  if (!selectedGroup.value || selectedProjects.value.length === 0) return;

  ElMessageBox.confirm(
    `确定将选中的 ${selectedProjects.value.length} 个项目分配给该专家组进行 "${reviewType.value}" 评审吗？`,
    "提示",
    { confirmButtonText: "确定", cancelButtonText: "取消", type: "warning" }
  ).then(async () => {
    assigning.value = true;
    try {
      const projectIds = selectedProjects.value.map((p) => p.id);
      const nodeIds = new Set(
        selectedProjects.value
          .map((p) => p.workflow_node_id)
          .filter((id): id is number => typeof id === "number")
      );
      const payload: Record<string, unknown> = {
        project_ids: projectIds,
        group_id: selectedGroup.value,
        review_type: reviewType.value,
      };
      if (nodeIds.size === 1) {
        payload.target_node_id = Array.from(nodeIds)[0];
      }
      const res = await request.post(
        "/reviews/assignments/assign_batch/",
        payload
      );
      const message = isRecord(res) ? res.message : null;
      const dataMessage =
        isRecord(res) && isRecord(res.data) ? res.data.message : null;
      ElMessage.success(message || dataMessage || "分配成功");
      selectedProjects.value = [];
      fetchProjects();
    } catch (error: unknown) {
      console.error(error);
      ElMessage.error(getErrorMessage(error, "分配失败"));
    } finally {
      assigning.value = false;
    }
  });
};

onMounted(() => {
  fetchGroups();
  const q = String(
    route.query.reviewType || route.query.review_type || ""
  ).toUpperCase();
  if (q && ["APPLICATION", "MID_TERM", "CLOSURE"].includes(q)) {
    reviewType.value = q;
  }
  statusFilter.value = "";
  fetchProjects();
});
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.expert-assignment-container {
  padding: 20px;
}

.main-card {
  border-radius: 8px;
  :deep(.el-card__header) {
    padding: 16px 20px;
    font-weight: 600;
    border-bottom: 1px solid $color-border-light;
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
  color: $slate-800;
}

.header-actions {
  display: flex;
  align-items: center;
}

.filter-container {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.mr-2 {
  margin-right: 10px;
}
.ml-2 {
  margin-left: 10px;
}
.mt-4 {
  margin-top: 16px;
}

.pagination-container {
  display: flex;
  justify-content: flex-end;
}
</style>
