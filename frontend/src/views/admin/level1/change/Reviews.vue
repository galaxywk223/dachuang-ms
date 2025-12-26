<template>
  <div class="change-review-page">
    <el-card class="main-card" shadow="never">
      <template #header>
        <div class="card-header">
           <div class="header-left">
             <span class="header-title">项目变更审核</span>
             <el-tag type="info" size="small" effect="plain" round class="ml-2">共 {{ total }} 项</el-tag>
           </div>
        </div>
      </template>

      <div class="filter-section mb-4">
        <el-form :inline="true" class="filter-form">
          <el-form-item label="变更类型">
             <el-select v-model="filters.changeType" placeholder="全部类型" clearable style="width: 150px">
                <el-option label="全部" value="" />
                <el-option label="成员变更" value="MEMBER" />
                <el-option label="导师变更" value="TEACHER" />
                <el-option label="经费变更" value="BUDGET" />
                <el-option label="延期变更" value="POSTPONE" />
                <el-option label="终止项目" value="TERMINATION" />
             </el-select>
          </el-form-item>
           <el-form-item label="项目名称">
            <el-input
              v-model="filters.search"
              placeholder="搜索项目名称"
              style="width: 200px"
              clearable
              @keyup.enter="handleSearch"
            >
               <template #prefix><el-icon><Search /></el-icon></template>
            </el-input>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="resetFilters">重置</el-button>
          </el-form-item>
        </el-form>
      </div>

      <el-table
        v-loading="loading"
        :data="changeRequests"
        style="width: 100%"
        border
        stripe
      >
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column
          prop="project_title"
          label="项目名称"
          min-width="200"
          show-overflow-tooltip
        >
             <template #default="{ row }">
                 <div class="font-medium">{{ row.project_title }}</div>
                 <div class="text-xs text-gray-500">项目编号: {{ row.project_no || '-' }}</div>
             </template>
        </el-table-column>
        <el-table-column prop="type_display" label="变更类型" width="120" align="center">
          <template #default="{ row }">
            <el-tag>{{ row.type_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="申请时间" width="160" align="center">
             <template #default="{ row }">
                 {{ formatDate(row.created_at) }}
             </template>
        </el-table-column>
        <el-table-column prop="status_display" label="状态" width="120" align="center">
           <template #default="{ row }">
               <el-tag :type="getStatusType(row.status)">{{ row.status_display }}</el-tag>
           </template>
        </el-table-column>
        
        <el-table-column label="操作" width="180" align="center" fixed="right">
          <template #default="{ row }">
              <el-button link type="primary" size="small" @click="handleReview(row)">审核</el-button>
              <el-button v-if="row.attachment_url" link type="primary" size="small" @click="openAttachment(row.attachment_url)">附件</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container mt-4">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" title="审核意见" width="480px">
      <el-form label-width="90px">
        <el-form-item label="审核意见">
          <el-input v-model="comments" type="textarea" :rows="4" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="danger" :loading="reviewing" @click="submitReview('reject')">驳回</el-button>
          <el-button type="primary" :loading="reviewing" @click="submitReview('approve')">通过</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { Search } from "@element-plus/icons-vue";
import { getChangeRequests, reviewChangeRequest } from "@/api/projects/change-requests";
import dayjs from "dayjs";

const loading = ref(false);
const reviewing = ref(false);
const changeRequests = ref<any[]>([]);
const total = ref(0);
const currentPage = ref(1);
const pageSize = ref(10);
const dialogVisible = ref(false);
const currentId = ref<number | null>(null);
const comments = ref("");

const filters = ref({
  changeType: "",
  search: "",
});

const fetchRequests = async () => {
  loading.value = true;
  try {
    const params: any = {
      page: currentPage.value,
      page_size: pageSize.value,
      status: "LEVEL1_REVIEWING", // Only show pending reviews
    };
    if (filters.value.changeType) params.type = filters.value.changeType;
    if (filters.value.search) params.search = filters.value.search;

    const res: any = await getChangeRequests(params);
    // Handle different API response structures if needed, but assuming standard pagination
    if (res.data && Array.isArray(res.data.results)) {
       changeRequests.value = res.data.results;
       total.value = res.data.total;
    } else if (res.data && Array.isArray(res.data)) {
        // Fallback or non-paginated?
        changeRequests.value = res.data;
        total.value = res.data.length;
    } else if (Array.isArray(res)) {
        changeRequests.value = res;
        total.value = res.length;
    } else {
        changeRequests.value = [];
        total.value = 0;
    }
  } catch (error) {
    console.error(error);
    ElMessage.error("获取数据失败");
  } finally {
    loading.value = false;
  }
};

const handleSearch = () => {
  currentPage.value = 1;
  fetchRequests();
};

const resetFilters = () => {
  filters.value.changeType = "";
  filters.value.search = "";
  handleSearch();
};

const handleSizeChange = (val: number) => {
  pageSize.value = val;
  fetchRequests();
};

const handlePageChange = (val: number) => {
  currentPage.value = val;
  fetchRequests();
};

const handleReview = (row: any) => {
  currentId.value = row.id;
  comments.value = "";
  dialogVisible.value = true;
};

const submitReview = async (action: "approve" | "reject") => {
  if (!currentId.value) return;
  reviewing.value = true;
  try {
    await reviewChangeRequest(currentId.value, { action, comments: comments.value });
    ElMessage.success("审核完成");
    dialogVisible.value = false;
    fetchRequests();
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || "操作失败");
  } finally {
    reviewing.value = false;
  }
};

const openAttachment = (url: string) => {
  window.open(url, "_blank");
};

const formatDate = (date: string) => {
  if (!date) return "-";
  return dayjs(date).format("YYYY-MM-DD HH:mm");
};

const getStatusType = (status: string) => {
  if (status === "APPROVED") return "success";
  if (status === "REJECTED") return "danger";
  return "warning";
};

onMounted(() => {
  fetchRequests();
});
</script>

<style scoped>
.change-review-page {
  padding: 20px;
}
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.title {
  font-size: 16px;
  font-weight: 600;
}
</style>
