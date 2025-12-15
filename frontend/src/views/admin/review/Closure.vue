
<template>
  <div class="review-page">
     <!-- Filter Section -->
    <div class="filter-section">
      <el-form :inline="true" class="filter-form">
        <el-form-item label="项目名称">
            <el-input
            v-model="searchQuery"
            placeholder="搜索项目名称"
            style="width: 240px"
            clearable
            :prefix-icon="Search"
            @clear="handleSearch"
            @keyup.enter="handleSearch"
            />
        </el-form-item>
        <el-form-item>
            <el-button type="primary" @click="handleSearch" :icon="Search"> 查询 </el-button>
            <el-button @click="handleReset" :icon="RefreshLeft"> 重置 </el-button>
        </el-form-item>
      </el-form>
    </div>

     <!-- Table Section -->
    <div class="table-container">
       <div class="table-header">
        <div class="title-bar">
           <span class="title">结题审核列表</span>
           <el-tag type="info" size="small" effect="plain" round class="count-tag">共 {{ total }} 项</el-tag>
        </div>
      </div>

      <el-table 
        v-loading="loading" 
        :data="projects" 
        style="width: 100%"
        :header-cell-style="{ background: '#f8fafc', color: '#475569', fontWeight: '600', height: '48px' }"
        :cell-style="{ color: '#334155', height: '48px' }"
      >
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="project_no" label="项目编号" width="130" show-overflow-tooltip align="center" />
        <el-table-column prop="title" label="项目名称" min-width="220" show-overflow-tooltip>
             <template #default="{ row }">
                 <span class="project-title">{{ row.title }}</span>
             </template>
        </el-table-column>
        <el-table-column prop="category_display" label="类别" width="120" align="center">
            <template #default="{ row }">
                <el-tag effect="light" size="small" type="info">{{ row.category_display }}</el-tag>
            </template>
        </el-table-column>
        <el-table-column prop="level_display" label="级别" width="100" align="center">
             <template #default="{ row }">
                 <el-tag :type="getLevelType(row.level)" effect="plain" size="small">{{ row.level_display }}</el-tag>
            </template>
        </el-table-column>
        <el-table-column prop="leader_name" label="负责人" width="100" align="center" />
        <el-table-column label="状态" width="120" align="center">
            <template #default="{ row }">
                <div class="status-dot">
                    <span class="dot" :class="getStatusClass(row.status)"></span>
                    <span>{{ row.status_display }}</span>
                </div>
            </template>
        </el-table-column>
        <el-table-column prop="created_at" label="提交时间" width="160" align="center">
            <template #default="{ row }">
                <span class="date-text">{{ formatDate(row.created_at) }}</span>
            </template>
        </el-table-column>
        <el-table-column label="操作" width="180" align="center" fixed="right">
            <template #default="{ row }">
                <el-button link type="success" @click="handleApprove(row)">通过</el-button>
                <el-button link type="danger" @click="handleReject(row)">驳回</el-button>
            </template>
        </el-table-column>
     </el-table>

     <div class="pagination-footer">
        <el-pagination
            v-model:current-page="currentPage"
            v-model:page-size="pageSize"
            :page-sizes="[10, 20, 50]"
            :total="total"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
            background
            size="small"
            class="custom-pagination"
        />
     </div>
    </div>

    <!-- 审核对话框 -->
    <el-dialog
      v-model="reviewDialogVisible"
      :title="reviewType === 'approve' ? '审核通过' : '驳回申请'"
      width="480px"
      align-center
      destroy-on-close
    >
      <el-form :model="reviewForm" label-position="top">
        <el-form-item :label="reviewType === 'approve' ? '审核意见 (可选)' : '驳回原因 (必填)'">
          <el-input
            v-model="reviewForm.comment"
            type="textarea"
            :rows="4"
            :placeholder="reviewType === 'approve' ? '请输入...' : '请输入驳回的具体原因...'"
            resize="none"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
            <el-button @click="reviewDialogVisible = false">取消</el-button>
            <el-button
            :type="reviewType === 'approve' ? 'primary' : 'danger'"
            @click="confirmReview"
            >
            确认提交
            </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { Search, RefreshLeft } from "@element-plus/icons-vue";
import { getReviewProjects, approveProject, rejectProject } from "@/api/admin";

const loading = ref(false);
const projects = ref<any[]>([]);
const searchQuery = ref("");
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);

const reviewDialogVisible = ref(false);
const reviewType = ref<"approve" | "reject">("approve");
const reviewForm = ref({
  projectId: 0,
  comment: "",
});

const fetchProjects = async () => {
  loading.value = true;
  try {
    const response: any = await getReviewProjects({
      page: currentPage.value,
      page_size: pageSize.value,
      search: searchQuery.value,
      type: "closure",
    });

    if (response.code === 200) {
      projects.value = response.data.results;
      total.value = response.data.total;
    }
  } catch (error) {
    ElMessage.error("获取项目列表失败");
  } finally {
    loading.value = false;
  }
};

const handleSearch = () => {
  currentPage.value = 1;
  fetchProjects();
};

const handleReset = () => {
    searchQuery.value = "";
    handleSearch();
};

const handlePageChange = () => {
  fetchProjects();
};

const handleSizeChange = () => {
  currentPage.value = 1;
  fetchProjects();
};

const handleApprove = (row: any) => {
  reviewType.value = "approve";
  reviewForm.value.projectId = row.id;
  reviewForm.value.comment = "";
  reviewDialogVisible.value = true;
};

const handleReject = (row: any) => {
  reviewType.value = "reject";
  reviewForm.value.projectId = row.id;
  reviewForm.value.comment = "";
  reviewDialogVisible.value = true;
};

const confirmReview = async () => {
  if (reviewType.value === "reject" && !reviewForm.value.comment) {
    ElMessage.warning("请输入驳回原因");
    return;
  }

  try {
    const data = { comment: reviewForm.value.comment };

    let response: any;
    if (reviewType.value === "approve") {
      response = await approveProject(reviewForm.value.projectId, data);
    } else {
      response = await rejectProject(reviewForm.value.projectId, data);
    }
    
    if (response.code === 200) {
        ElMessage.success(reviewType.value === 'approve' ? "已通过" : "已驳回");
        reviewDialogVisible.value = false;
        fetchProjects();
    }
  } catch (error) {
    ElMessage.error("操作失败");
  }
};

const getLevelType = (level: string) => {
    if (level === 'NATIONAL') return 'danger';
    if (level === 'PROVINCIAL') return 'warning';
    return 'info';
};

const getStatusClass = (status: string) => {
    if (status.includes('APPROVED')) return 'dot-success';
    if (status.includes('REJECTED')) return 'dot-danger';
    if (status.includes('REVIEWING') || status === 'SUBMITTED') return 'dot-warning';
    return 'dot-info';
};

const formatDate = (date: string) => {
  if (!date) return "-";
  return new Date(date).toLocaleDateString();
};

onMounted(() => {
  fetchProjects();
});
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.review-page {
    padding: 24px;
    max-width: 1600px;
    margin: 0 auto;
}

.filter-section {
  background: white;
  padding: 20px 24px 0 24px;
  border-radius: $radius-lg;
  margin-bottom: 16px;
  box-shadow: $shadow-sm;
  border: 1px solid $color-border-light;
  
  .filter-form {
    display: flex;
    gap: 16px;
  }
}

.table-container {
  background: white;
  border-radius: $radius-lg;
  box-shadow: $shadow-sm;
  border: 1px solid $color-border-light;
  overflow: hidden;

  .table-header {
      padding: 16px 24px;
      border-bottom: 1px solid $slate-100;
      display: flex;
      align-items: center;
      justify-content: space-between;

      .title-bar {
          display: flex;
          align-items: center;
          gap: 12px;
          
          .title {
              font-size: 16px;
              font-weight: 600;
              color: $slate-800;
              position: relative;
              padding-left: 14px;
              
              &::before {
                  content: '';
                  position: absolute;
                  left: 0;
                  top: 50%;
                  transform: translateY(-50%);
                  width: 4px;
                  height: 16px;
                  background: $primary-600;
                  border-radius: 2px;
              }
          }
      }
  }
}

.pagination-footer {
    padding: 16px 24px;
    border-top: 1px solid $slate-100; // Consistent footer border
    display: flex;
    justify-content: flex-end;
}

.project-title {
    font-weight: 500;
    color: $slate-800;
    font-size: 14px;
}

.date-text {
    color: $slate-500;
    font-size: 13px;
}

.status-dot {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    font-size: 13px;
    
    .dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        
        &.dot-success { background: $success; box-shadow: 0 0 0 2px rgba($success, 0.2); }
        &.dot-warning { background: $warning; box-shadow: 0 0 0 2px rgba($warning, 0.2); }
        &.dot-danger { background: $danger; box-shadow: 0 0 0 2px rgba($danger, 0.2); }
        &.dot-info { background: $slate-400; }
    }
}
</style>
