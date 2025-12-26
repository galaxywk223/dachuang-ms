<template>
  <div class="midterm-drafts-page">
    <el-card class="main-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="header-title">中期草稿箱</span>
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
            <el-tag type="info" size="small">
              {{ row.status_display || "中期草稿" }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" align="center" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link size="small" @click="handleEdit(row)">
              编辑报告
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
        description="暂无中期草稿"
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

const fetchDrafts = async () => {
  loading.value = true;
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize,
      status_in: "MID_TERM_DRAFT",
    };

    const res: any = await getProjects(params);
    if (res?.code === 200) {
      tableData.value = res.data?.results || [];
      pagination.total = res.data?.count || 0;
    } else {
      ElMessage.error(res?.message || "获取草稿列表失败");
    }
  } catch (error: any) {
    console.error("获取中期草稿失败:", error);
    ElMessage.error(error.message || "获取草稿列表失败");
  } finally {
    loading.value = false;
  }
};

const handleEdit = (row: any) => {
  router.push(`/midterm/apply?projectId=${row.id}`);
};

const handleSizeChange = (size: number) => {
  pagination.pageSize = size;
  pagination.page = 1;
  fetchDrafts();
};

const handleCurrentChange = (page: number) => {
  pagination.page = page;
  fetchDrafts();
};

onMounted(() => {
  fetchDrafts();
});
</script>

<style scoped lang="scss">
@use "./Drafts.scss";
</style>
