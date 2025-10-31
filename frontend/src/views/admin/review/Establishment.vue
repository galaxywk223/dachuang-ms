<template>
  <div class="review-page">
    <div class="page-header">
      <h2>立项审核</h2>
      <div class="filter-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索项目名称"
          style="width: 300px"
          clearable
          @clear="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" @click="handleSearch">
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
      </div>
    </div>

    <el-table
      v-loading="loading"
      :data="projects"
      style="width: 100%"
      @expand-change="handleExpandChange"
    >
      <el-table-column type="expand">
        <template #default="{ row }">
          <div class="expand-content">
            <el-descriptions :column="2" border>
              <el-descriptions-item label="项目编号">{{
                row.project_no
              }}</el-descriptions-item>
              <el-descriptions-item label="项目类别">{{
                row.category_display
              }}</el-descriptions-item>
              <el-descriptions-item label="项目级别">{{
                row.level_display
              }}</el-descriptions-item>
              <el-descriptions-item label="项目负责人">{{
                row.leader_name
              }}</el-descriptions-item>
              <el-descriptions-item label="联系电话">{{
                row.leader_contact
              }}</el-descriptions-item>
              <el-descriptions-item label="电子邮箱">{{
                row.leader_email
              }}</el-descriptions-item>
              <el-descriptions-item label="指导老师" :span="2">
                <el-tag
                  v-for="advisor in row.advisors_info"
                  :key="advisor.id"
                  style="margin-right: 8px"
                >
                  {{ advisor.name }} ({{ advisor.title }})
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="项目简介" :span="2">
                {{ row.description || "暂无" }}
              </el-descriptions-item>
            </el-descriptions>

            <div class="review-actions">
              <el-button type="success" @click="handleApprove(row)">
                <el-icon><Check /></el-icon>
                通过
              </el-button>
              <el-button type="danger" @click="handleReject(row)">
                <el-icon><Close /></el-icon>
                驳回
              </el-button>
            </div>
          </div>
        </template>
      </el-table-column>

      <el-table-column type="index" label="序号" width="60" />
      <el-table-column prop="title" label="项目名称" min-width="200" />
      <el-table-column prop="category_display" label="项目类别" width="150" />
      <el-table-column prop="level_display" label="项目级别" width="120" />
      <el-table-column prop="leader_name" label="项目负责人" width="120" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag type="warning">{{ row.status_display }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="申请时间" width="180" />
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button text type="primary" @click="handleViewDetail(row)">
            查看详情
          </el-button>
          <el-button text type="success" @click="handleApprove(row)">
            通过
          </el-button>
          <el-button text type="danger" @click="handleReject(row)">
            驳回
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="pagination">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </div>

    <!-- 审核对话框 -->
    <el-dialog
      v-model="reviewDialogVisible"
      :title="reviewType === 'approve' ? '审核通过' : '驳回申请'"
      width="500px"
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
        <el-button @click="reviewDialogVisible = false">取消</el-button>
        <el-button
          :type="reviewType === 'approve' ? 'success' : 'danger'"
          @click="confirmReview"
        >
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { Search, Check, Close } from "@element-plus/icons-vue";
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

const handlePageChange = () => {
  fetchProjects();
};

const handleSizeChange = () => {
  currentPage.value = 1;
  fetchProjects();
};

const handleExpandChange = (row: any, expandedRows: any[]) => {
  // 展开行时的处理
  console.log("Expanded:", row, expandedRows);
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

    if (reviewType.value === "approve") {
      const response: any = await approveProject(
        reviewForm.value.projectId,
        data
      );
      if (response.code === 200) {
        ElMessage.success("审核通过");
      }
    } else {
      const response: any = await rejectProject(
        reviewForm.value.projectId,
        data
      );
      if (response.code === 200) {
        ElMessage.success("已驳回");
      }
    }

    reviewDialogVisible.value = false;
    fetchProjects();
  } catch (error) {
    ElMessage.error("操作失败");
  }
};

onMounted(() => {
  fetchProjects();
});
</script>

<style scoped lang="scss">
.review-page {
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    h2 {
      margin: 0;
      font-size: 20px;
      font-weight: 500;
    }

    .filter-bar {
      display: flex;
      gap: 10px;
    }
  }

  .expand-content {
    padding: 20px;
    background: #f5f7fa;

    .review-actions {
      margin-top: 20px;
      display: flex;
      justify-content: center;
      gap: 10px;
    }
  }

  .pagination {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
