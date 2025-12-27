<template>
  <div class="midterm-list-page">
    <el-card class="main-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="header-title">中期检查项目</span>
            <el-tag type="info" size="small" effect="plain" round class="ml-2">
              {{ pagination.total }}
            </el-tag>
          </div>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="tableData"
        stripe
        border
        style="width: 100%"
      >
        <el-table-column prop="project_no" label="项目编号" min-width="160" />
        <el-table-column prop="title" label="项目名称" min-width="220" show-overflow-tooltip />
        <el-table-column prop="leader_name" label="负责人" width="120" align="center" />
        <el-table-column prop="college" label="学院" width="140" align="center" />
        <el-table-column label="状态" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" size="small">
              {{ row.status_display || getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleOpen(row)">
              {{ isEditable(row.status) ? "填写报告" : "查看报告" }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>

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

      <el-empty
        v-if="!loading && tableData.length === 0"
        description="暂无中期检查项目"
        :image-size="200"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { useRouter } from "vue-router";
import { getProjects } from "@/api/projects";

const router = useRouter();

const tableData = ref<any[]>([]);
const loading = ref(false);

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0,
});

const statusFilters = [
  "IN_PROGRESS",
  "MID_TERM_DRAFT",
  "MID_TERM_SUBMITTED",
  "MID_TERM_REVIEWING",
  "MID_TERM_APPROVED",
  "MID_TERM_REJECTED",
  "MID_TERM_RETURNED",
];

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    IN_PROGRESS: "进行中",
    MID_TERM_DRAFT: "中期草稿",
    MID_TERM_SUBMITTED: "已提交",
    MID_TERM_REVIEWING: "审核中",
    MID_TERM_APPROVED: "审核通过",
    MID_TERM_REJECTED: "审核不通过",
    MID_TERM_RETURNED: "退回修改",
  };
  return map[status] || status;
};

const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    IN_PROGRESS: "success",
    MID_TERM_DRAFT: "info",
    MID_TERM_SUBMITTED: "warning",
    MID_TERM_REVIEWING: "warning",
    MID_TERM_APPROVED: "success",
    MID_TERM_REJECTED: "danger",
    MID_TERM_RETURNED: "danger",
  };
  return map[status] || "info";
};

const isEditable = (status: string) =>
  ["IN_PROGRESS", "MID_TERM_DRAFT", "MID_TERM_REJECTED"].includes(status);

const fetchProjects = async () => {
  loading.value = true;
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      status_in: statusFilters.join(","),
    };

    const res: any = await getProjects(params);
    if (res?.code === 200) {
      tableData.value = res.data?.results || [];
      pagination.total = res.data?.count || 0;
    } else {
      ElMessage.error(res?.message || "获取项目列表失败");
    }
  } catch (error: any) {
    console.error("获取中期检查项目失败:", error);
    ElMessage.error(error.message || "获取项目列表失败");
  } finally {
    loading.value = false;
  }
};

const handleOpen = (row: any) => {
  router.push(`/midterm/apply?projectId=${row.id}`);
};

const handleSizeChange = (size: number) => {
  pagination.pageSize = size;
  pagination.page = 1;
  fetchProjects();
};

const handleCurrentChange = (page: number) => {
  pagination.page = page;
  fetchProjects();
};

onMounted(() => {
  fetchProjects();
});
</script>

<style scoped lang="scss">
@use "./Index.scss";
</style>
