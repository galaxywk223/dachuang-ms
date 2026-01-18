<template>
  <div class="project-list-page">
    <el-card class="main-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="header-title">异动管理</span>
        </div>
      </template>

      <el-table
        :data="tableData"
        v-loading="loading"
        stripe
        header-cell-class-name="table-header-cell"
        empty-text="暂无进行中的项目"
      >
        <el-table-column prop="project_no" label="项目编号" width="140" />
        <el-table-column prop="title" label="项目名称" min-width="200" />
        <el-table-column prop="leader_name" label="负责人" width="120" />
        <el-table-column
          prop="status_display"
          label="状态"
          width="140"
        />
        <el-table-column label="操作" width="120" align="center" fixed="right">
          <template #default="{ row }">
            <el-button
              type="primary"
              link
              size="small"
              @click="goToChangeRequests(row)"
            >
              进入
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container" v-if="pagination.total > pagination.pageSize">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
          background
          size="small"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { getProjects } from "@/api/projects";
import { useUserStore } from "@/stores/user";

defineOptions({
  name: "StudentChangeProjectsView",
});

type ProjectRow = {
  id: number;
  project_no?: string;
  title?: string;
  leader_name?: string;
  status?: string;
  status_display?: string;
};

type ProjectsResponse = {
  code?: number;
  message?: string;
  data?: {
    results?: ProjectRow[];
    count?: number;
  };
};

const ACTIVE_PROJECT_STATUSES = [
  "IN_PROGRESS",
  "MID_TERM_DRAFT",
  "MID_TERM_SUBMITTED",
  "MID_TERM_REVIEWING",
  "READY_FOR_CLOSURE",
  "MID_TERM_REJECTED",
  "MID_TERM_RETURNED",
  "CLOSURE_DRAFT",
  "CLOSURE_SUBMITTED",
  "CLOSURE_LEVEL2_REVIEWING",
  "CLOSURE_LEVEL2_APPROVED",
  "CLOSURE_LEVEL2_REJECTED",
  "CLOSURE_LEVEL1_REVIEWING",
  "CLOSURE_LEVEL1_APPROVED",
  "CLOSURE_LEVEL1_REJECTED",
  "CLOSURE_RETURNED",
];

const router = useRouter();
const userStore = useUserStore();
const leaderId = computed(() => userStore.user?.id);
const tableData = ref<ProjectRow[]>([]);
const loading = ref(false);

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0,
});

const fetchProjects = async () => {
  loading.value = true;
  try {
    const params: Record<string, string | number> = {
      page: pagination.page,
      page_size: pagination.pageSize,
      status_in: ACTIVE_PROJECT_STATUSES.join(","),
    };
    if (leaderId.value) {
      params.leader = leaderId.value;
    }
    const response = (await getProjects(params)) as ProjectsResponse;
    if (response.code === 200) {
      tableData.value = response.data?.results || [];
      pagination.total = response.data?.count || tableData.value.length;
      return;
    }
    ElMessage.error(response.message || "获取列表失败");
  } catch (error) {
    console.error(error);
    ElMessage.error("获取列表失败");
  } finally {
    loading.value = false;
  }
};

const handleSizeChange = (size: number) => {
  pagination.pageSize = size;
  fetchProjects();
};

const handleCurrentChange = (page: number) => {
  pagination.page = page;
  fetchProjects();
};

const goToChangeRequests = (row: ProjectRow) => {
  router.push(`/project/${row.id}/change-requests`);
};

onMounted(() => {
  fetchProjects();
});
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

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
  align-items: center;
  justify-content: space-between;
}

.pagination-container {
  padding-top: 24px;
  display: flex;
  justify-content: flex-end;
}
</style>
