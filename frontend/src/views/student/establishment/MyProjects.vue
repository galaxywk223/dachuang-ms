<template>
  <div class="my-projects-page">
    <el-card class="main-card" shadow="never">
      <template #header>
        <div class="card-header">
          <span class="header-title">我的项目</span>
          <div class="header-actions">
            <el-button
              type="primary"
              @click="$router.push('/establishment/apply')"
            >
              <el-icon class="mr-1"><Plus /></el-icon> 申请新项目
            </el-button>
          </div>
        </div>
      </template>

      <!-- 筛选区域 -->
      <div class="filter-section">
        <el-form :inline="true" :model="filterForm" class="filter-form">
          <el-form-item label="名称">
            <el-input
              v-model="filterForm.title"
              placeholder="搜索名称"
              clearable
              :prefix-icon="SearchIcon"
              style="width: 200px"
              @keyup.enter="handleSearch"
            />
          </el-form-item>

          <el-form-item label="级别">
            <el-select
              v-model="filterForm.level"
              placeholder="全部"
              clearable
              style="width: 140px"
            >
              <el-option
                v-for="item in levelOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="类别">
            <el-select
              v-model="filterForm.category"
              placeholder="全部"
              clearable
              style="width: 160px"
            >
              <el-option
                v-for="item in categoryOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              />
            </el-select>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="handleSearch" :icon="SearchIcon"
              >查询</el-button
            >
            <el-button @click="handleReset" :icon="RefreshLeft">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <!-- 表格区域 -->
      <div class="table-section">
        <div class="table-info-bar">
          <el-alert type="info" :closable="false" show-icon class="mb-4">
            <template #default>
              共查询到 {{ pagination.total }} 个项目。
            </template>
          </el-alert>
        </div>

        <el-table
          v-loading="loading"
          :data="tableData"
          style="width: 100%"
          :header-cell-style="{
            background: '#f8fafc',
            color: '#475569',
            fontWeight: '600',
            fontSize: '13px',
            height: '48px',
          }"
          :cell-style="{ color: '#334155', fontSize: '14px', padding: '8px 0' }"
          stripe
        >
          <el-table-column
            prop="title"
            label="项目名称"
            min-width="200"
            show-overflow-tooltip
            fixed="left"
          >
            <template #default="{ row }">
              <span class="link-text" @click="handleEdit(row)">{{
                row.title
              }}</span>
            </template>
          </el-table-column>

          <el-table-column
            prop="level"
            label="项目级别"
            width="100"
            align="center"
          >
            <template #default="{ row }">
              <el-tag
                :type="getLevelType(row.level)"
                effect="plain"
                size="small"
                >{{
                  row.level_display || getLabel(levelOptions, row.level)
                }}</el-tag
              >
            </template>
          </el-table-column>

          <el-table-column
            prop="category"
            label="项目类别"
            width="120"
            align="center"
          >
            <template #default="{ row }">
              <el-tag effect="light" size="small" type="info">{{
                row.category_display || getLabel(categoryOptions, row.category)
              }}</el-tag>
            </template>
          </el-table-column>

          <el-table-column label="重点领域项目" width="110" align="center">
            <template #default="{ row }">
              <el-tag v-if="row.is_key_field" type="success" size="small"
                >是</el-tag
              >
              <span v-else>-</span>
            </template>
          </el-table-column>

          <el-table-column label="重点领域代码" width="110" align="center">
            <template #default="{ row }">
              <span>{{ row.key_domain_code || "-" }}</span>
            </template>
          </el-table-column>

          <el-table-column
            prop="leader_name"
            label="负责人姓名"
            width="100"
            align="center"
          >
            <template #default="{ row }">
              {{ row.leader_name || row.creator?.real_name || "-" }}
            </template>
          </el-table-column>

          <el-table-column
            prop="leader_student_id"
            label="负责人学号"
            width="120"
            align="center"
          >
            <template #default="{ row }">
              {{ row.leader_student_id || "-" }}
            </template>
          </el-table-column>

          <el-table-column
            prop="college"
            label="学院"
            width="140"
            show-overflow-tooltip
            align="center"
          >
            <template #default="{ row }">
              {{ row.college || "-" }}
            </template>
          </el-table-column>

          <el-table-column
            prop="leader_contact"
            label="联系电话"
            width="120"
            align="center"
          >
            <template #default="{ row }">
              {{ row.leader_contact || "-" }}
            </template>
          </el-table-column>

          <el-table-column
            prop="leader_email"
            label="邮箱"
            width="180"
            show-overflow-tooltip
            align="center"
          >
            <template #default="{ row }">
              {{ row.leader_email || "-" }}
            </template>
          </el-table-column>

          <el-table-column
            prop="budget"
            label="项目经费"
            width="100"
            align="center"
          >
            <template #default="{ row }">
              {{ row.budget }}
            </template>
          </el-table-column>

          <el-table-column
            label="审核节点"
            width="120"
            align="center"
            fixed="right"
          >
            <template #default="{ row }">
              <el-tag
                :type="getStatusColor(row.status)"
                size="small"
                effect="light"
                >{{ row.status_display || getStatusLabel(row.status) }}</el-tag
              >
            </template>
          </el-table-column>

          <el-table-column
            label="操作"
            width="220"
            align="center"
            fixed="right"
          >
            <template #default="{ row }">
              <!-- Draft Action -->
              <template v-if="row.status === 'DRAFT'">
                <template v-if="isLeader(row)">
                  <el-button
                    type="primary"
                    link
                    size="small"
                    @click="handleEdit(row)"
                    >编辑</el-button
                  >
                  <el-button
                    type="danger"
                    link
                    size="small"
                    @click="handleDelete(row)"
                    >删除</el-button
                  >
                </template>
                <el-button
                  v-else
                  type="primary"
                  link
                  size="small"
                  @click="handleEdit(row)"
                  >查看</el-button
                >
              </template>
              <!-- View Action -->
              <template v-else>
                <div class="action-wrap">
                  <el-button
                    type="primary"
                    link
                    size="small"
                    @click="handleEdit(row)"
                    >查看</el-button
                  >
                  <template v-if="isLeader(row)">
                    <el-dropdown trigger="click">
                      <el-button type="success" link size="small">
                        管理
                        <el-icon style="margin-left: 4px"><ArrowDown /></el-icon>
                      </el-button>
                      <template #dropdown>
                        <el-dropdown-item @click="goToChangeRequests(row)"
                          >项目异动</el-dropdown-item
                        >
                        <el-dropdown-item @click="goToFunds(row)"
                          >经费管理</el-dropdown-item
                        >
                      </template>
                    </el-dropdown>
                    <el-button
                      type="warning"
                      link
                      size="small"
                      @click="handleWithdraw(row)"
                      v-if="canWithdraw(row)"
                      >撤回</el-button
                    >
                    <el-button
                      type="danger"
                      link
                      size="small"
                      @click="handleDeleteSubmission(row)"
                      v-if="canDeleteSubmission(row)"
                      >删除提交</el-button
                    >
                  </template>
                </div>
              </template>
            </template>
          </el-table-column>
        </el-table>

        <!-- 分页 -->
        <div class="pagination-container">
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
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";
import {
  Search as SearchIcon,
  RefreshLeft,
  Plus,
  ArrowDown,
} from "@element-plus/icons-vue";
import {
  getMyProjects,
  deleteProject,
  withdrawProjectApplication,
  deleteProjectApplication,
} from "@/api/projects";
import { useRouter } from "vue-router";
import { useDictionary } from "@/composables/useDictionary";
import { DICT_CODES } from "@/api/dictionaries";
import { useUserStore } from "@/stores/user";

defineOptions({
  name: "StudentEstablishmentMyProjectsView",
});

type DictOption = {
  value: string;
  label: string;
};

type ProjectRow = {
  id: number;
  project_no?: string;
  title?: string;
  level?: string;
  category?: string;
  college?: string;
  leader?: number;
  leader_name?: string;
  leader_student_id?: string;
  leader_contact?: string;
  budget?: number;
  status?: string;
};

type ProjectsResponse = {
  code?: number;
  status?: number;
  data?: ProjectRow[];
  total?: number;
  message?: string;
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

const router = useRouter();
const { loadDictionaries, getOptions } = useDictionary();
const userStore = useUserStore();
const currentUserId = computed(() => userStore.user?.id);

// Dict Options
const levelOptions = computed(
  () => getOptions(DICT_CODES.PROJECT_LEVEL) as DictOption[]
);
const categoryOptions = computed(
  () => getOptions(DICT_CODES.PROJECT_CATEGORY) as DictOption[]
);
// Add status mapping if needed, or hardcode common statuses
const statusMap: Record<string, string> = {
  DRAFT: "草稿",
  SUBMITTED: "已提交",
  TEACHER_AUDITING: "导师审核中",
  TEACHER_APPROVED: "导师审核通过",
  TEACHER_REJECTED: "导师审核不通过",
  COLLEGE_AUDITING: "学院审核中",
  LEVEL1_AUDITING: "校级审核中",
  APPLICATION_RETURNED: "退回修改",
  IN_PROGRESS: "进行中",
};

const filterForm = reactive({
  title: "",
  level: "",
  category: "",
});

const tableData = ref<ProjectRow[]>([]);
const loading = ref(false);

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0,
});

onMounted(async () => {
  await loadDictionaries([
    DICT_CODES.PROJECT_LEVEL,
    DICT_CODES.PROJECT_CATEGORY,
    DICT_CODES.COLLEGE,
  ]);
  fetchProjects();
});

const fetchProjects = async () => {
  loading.value = true;
  try {
    const params: Record<string, string | number> = {
      page: pagination.page,
      page_size: pagination.pageSize,
      ...filterForm,
    };
    if (!params.title) delete params.title;
    if (!params.level) delete params.level;
    if (!params.category) delete params.category;

    const response = (await getMyProjects(params)) as ProjectsResponse;
    if (response.code === 200) {
      tableData.value = response.data || [];
      pagination.total = response.total || response.data?.length || 0;
    } else {
      ElMessage.error(response.message || "获取列表失败");
    }
  } catch (error: unknown) {
    ElMessage.error(getErrorMessage(error, "获取列表失败"));
  } finally {
    loading.value = false;
  }
};

const getLabel = (options: DictOption[], value: string) => {
  const found = options.find((opt) => opt.value === value);
  return found ? found.label : value;
};

const getStatusLabel = (status: string) => {
  return statusMap[status] || status;
};

const handleSearch = () => {
  pagination.page = 1;
  fetchProjects();
};

const handleReset = () => {
  filterForm.title = "";
  filterForm.level = "";
  filterForm.category = "";
  pagination.page = 1;
  fetchProjects();
};

const handleSizeChange = (size: number) => {
  pagination.pageSize = size;
  fetchProjects();
};

const handleCurrentChange = (page: number) => {
  pagination.page = page;
  fetchProjects();
};

const getLevelType = (level: string) => {
  if (level === "NATIONAL") return "danger";
  if (level === "PROVINCIAL") return "warning";
  return "info";
};

const getStatusColor = (status: string) => {
  if (status.includes("APPROVED")) return "success";
  if (status.includes("REJECTED")) return "danger";
  if (status.includes("REVIEWING") || status === "SUBMITTED") return "warning";
  return "info";
};

const handleEdit = (row: ProjectRow) => {
  router.push(`/establishment/apply?id=${row.id}`);
};

const isLeader = (row: ProjectRow) => row.leader === currentUserId.value;

const canWithdraw = (row: ProjectRow) => {
  // Only allow withdraw if submitted and not fully approved/rejected yet (logic varies by requirement)
  return ["SUBMITTED", "TEACHER_AUDITING"].includes(row.status || "");
};

const canDeleteSubmission = (row: ProjectRow) => {
  return [
    "SUBMITTED",
    "TEACHER_AUDITING",
    "TEACHER_REJECTED",
    "APPLICATION_RETURNED",
  ].includes(row.status || "");
};

const handleWithdraw = async (row: ProjectRow) => {
  try {
    await ElMessageBox.confirm(
      "确认撤回该项目申请吗？撤回后将进入草稿箱。",
      "提示",
      {
        type: "warning",
        confirmButtonText: "确认撤回",
        cancelButtonText: "取消",
      }
    );
    const response = (await withdrawProjectApplication(
      row.id
    )) as ProjectsResponse;
    if (response.code === 200) {
      ElMessage.success("撤回成功，已转入草稿箱");
      fetchProjects();
    }
  } catch {
    // cancel
  }
};

const handleDelete = async (row: ProjectRow) => {
  try {
    await ElMessageBox.confirm("确定删除吗？", "提示", { type: "warning" });
    const response = (await deleteProject(row.id)) as ProjectsResponse;
    if (response.code === 200 || response.status === 204) {
      ElMessage.success("删除成功");
      fetchProjects();
    }
  } catch {
    // ignore
  }
};

const handleDeleteSubmission = async (row: ProjectRow) => {
  try {
    await ElMessageBox.confirm(
      "确定删除该申报提交吗？删除后可在回收站恢复。",
      "提示",
      {
        type: "warning",
      }
    );
    const response = (await deleteProjectApplication(
      row.id
    )) as ProjectsResponse;
    if (response.code === 200) {
      ElMessage.success("已移入回收站");
      fetchProjects();
    } else {
      ElMessage.error(response.message || "删除失败");
    }
  } catch {
    // cancel
  }
};

const goToChangeRequests = (row: ProjectRow) => {
  router.push(`/project/${row.id}/change-requests`);
};

const goToFunds = (row: ProjectRow) => {
  router.push(`/project/${row.id}/funds`);
};
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.my-projects-page {
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

.header-title {
  font-size: 16px;
  color: $slate-800;
}

.filter-section {
  padding-bottom: 20px;
  border-bottom: 1px dashed $color-border-light;
  margin-bottom: 20px;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;

  :deep(.el-form-item) {
    margin-bottom: 0px;
    margin-right: 0;
  }
}

.link-text {
  color: $primary-600;
  cursor: pointer;
  text-decoration: none;
  font-weight: 500;

  &:hover {
    text-decoration: underline;
  }
}

.pagination-container {
  padding-top: 24px;
  display: flex;
  justify-content: flex-end;
}

.mb-4 {
  margin-bottom: 16px;
}
.mr-1 {
  margin-right: 4px;
}

.action-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
</style>
