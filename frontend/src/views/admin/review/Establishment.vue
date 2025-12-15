<template>
  <div class="review-page">
    <!-- Filter Section -->
    <el-card class="filter-section" shadow="never">
      <el-form :inline="true" class="filter-form">
        <el-form-item label="项目名称">
            <el-input
            v-model="searchQuery"
            placeholder="搜索项目名称"
            style="width: 300px"
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
    </el-card>

    <!-- Table Section -->
    <el-card class="table-card" shadow="never">
      <template #header>
        <div class="card-header">
           <span class="title">立项审核列表</span>
        </div>
      </template>

      <el-table
        v-loading="loading"
        :data="projects"
        style="width: 100%"
        :header-cell-style="{ background: '#f8fafc', color: '#1e293b', fontWeight: '600', fontSize: '13px' }"
        :cell-style="{ color: '#334155', fontSize: '13px' }"
        border
        @expand-change="handleExpandChange"
      >
        <el-table-column type="expand" width="60" label="详情">
          <template #default="{ row }">
            <div class="expand-content">
              <el-descriptions title="项目详细信息" :column="2" border>
                <el-descriptions-item label="项目编号">{{ row.project_no }}</el-descriptions-item>
                <el-descriptions-item label="项目类别">{{ row.category_display }}</el-descriptions-item>
                <el-descriptions-item label="项目级别">{{ row.level_display }}</el-descriptions-item>
                <el-descriptions-item label="负责人">{{ row.leader_name }}</el-descriptions-item>
                <el-descriptions-item label="联系电话">{{ row.leader_contact }}</el-descriptions-item>
                <el-descriptions-item label="电子邮箱">{{ row.leader_email }}</el-descriptions-item>
                <el-descriptions-item label="指导老师" :span="2">
                  <el-tag
                    v-for="advisor in row.advisors_info"
                    :key="advisor.id"
                    style="margin-right: 8px"
                    size="small"
                  >
                    {{ advisor.name }} ({{ advisor.title }})
                  </el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="项目简介" :span="2">
                  {{ row.description || "暂无" }}
                </el-descriptions-item>
                 <el-descriptions-item label="预期成果" :span="2">
                  {{ row.expected_results || "暂无" }}
                </el-descriptions-item>
              </el-descriptions>

              <div class="review-actions">
                 <el-button type="success" :icon="Check" @click="handleApprove(row)">通过</el-button>
                 <el-button type="danger" :icon="Close" @click="handleReject(row)">驳回</el-button>
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column prop="title" label="项目名称" min-width="200" show-overflow-tooltip>
             <template #default="{ row }">
                 <span class="project-title">{{ row.title }}</span>
             </template>
        </el-table-column>
        <el-table-column prop="category_display" label="项目类别" width="150" align="center" />
        <el-table-column prop="level_display" label="项目级别" width="120" align="center">
            <template #default="{ row }">
                 <el-tag :type="getLevelType(row.level)" effect="plain" size="small">{{ row.level_display }}</el-tag>
            </template>
        </el-table-column>
        
        <el-table-column prop="leader_name" label="负责人" width="120" align="center" />
        
        <el-table-column label="状态" width="120" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusColor(row.status)" size="small">{{ row.status_display }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="申请时间" width="160" align="center">
             <template #default="{ row }">
                 {{ formatDate(row.created_at) }}
             </template>
        </el-table-column>
        
        <el-table-column label="操作" width="180" align="center" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="handleViewDetail(row)">查看详情</el-button>
            <el-button link type="success" @click="handleApprove(row)">通过</el-button>
            <el-button link type="danger" @click="handleReject(row)">驳回</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handlePageChange"
          background
          size="small"
        />
      </div>
    </el-card>

    <!-- 审核对话框 -->
    <el-dialog
      v-model="reviewDialogVisible"
      :title="reviewType === 'approve' ? '审核通过' : '驳回申请'"
      width="500px"
      append-to-body
    >
      <el-form :model="reviewForm" label-width="100px">
        <el-form-item label="审核意见">
          <el-input
            v-model="reviewForm.comment"
            type="textarea"
            :rows="4"
            :placeholder="
              reviewType === 'approve'
                ? '请输入审核意见（可选）'
                : '请输入驳回原因'
            "
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
            <el-button @click="reviewDialogVisible = false">取消</el-button>
            <el-button
            :type="reviewType === 'approve' ? 'success' : 'danger'"
            @click="confirmReview"
            >
            确定
            </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { Search, Check, Close, RefreshLeft } from "@element-plus/icons-vue";
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
      type: "establishment",
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

const handleExpandChange = (_row: any, _expandedRows: any[]) => {
  // 展开行时的处理
};

const handleViewDetail = (_row: any) => {
  ElMessage.info("查看详情功能开发中");
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
        ElMessage.success(reviewType.value === 'approve' ? "审核通过" : "已驳回");
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

const getStatusColor = (status: string) => {
    if (status.includes('APPROVED')) return 'success';
    if (status.includes('REJECTED')) return 'danger';
    if (status.includes('REVIEWING') || status === 'SUBMITTED') return 'warning';
    return 'info';
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



.filter-section {
  border: none;
  background: white;
  margin-bottom: 16px;
  border-radius: 4px;
  
  :deep(.el-card__body) {
    padding: 18px 24px;
    padding-bottom: 0;
  }
  
  .filter-form {
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
    
    :deep(.el-form-item) {
      margin-bottom: 18px;
      margin-right: 0;
    }
  }
}

.table-card {
  border: none;
  margin-bottom: 24px;
  border-radius: 4px;
  
   .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      
      .title {
          font-size: 16px;
          font-weight: 600;
          color: $slate-800;
          position: relative;
          padding-left: 12px;
          
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

  :deep(.el-card__header) {
      padding: 16px 24px;
      border-bottom: 1px solid $slate-100;
  }
  
  :deep(.el-card__body) {
    padding: 24px;
  }
}

.pagination-container {
  padding-top: 24px;
  display: flex;
  justify-content: flex-end;
}

.expand-content {
    padding: 20px;
    background: $slate-50; // Use slate-50 to match student
    border-radius: 4px;
    
    .review-actions {
        margin-top: 20px;
        display: flex;
        gap: 12px;
        justify-content: flex-end;
    }
}

.project-title {
    font-weight: 500;
    color: $slate-800;
}
</style>
