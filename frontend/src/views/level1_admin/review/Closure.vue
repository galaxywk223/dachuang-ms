<template>
  <div class="review-page">
    <el-card class="main-card" shadow="never">
      <template #header>
        <div class="card-header">
           <div class="header-left">
             <span class="header-title">校级结题审核列表</span>
             <el-tag type="info" size="small" effect="plain" round class="ml-2">共 {{ total }} 项</el-tag>
           </div>
           <div class="header-actions">
           </div>
        </div>
      </template>

      <div class="filter-section mb-4">
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
            <el-button type="primary" @click="handleSearch">查询</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <div class="action-bar mb-4">
          <el-button type="primary" plain @click="openBatchDialog">批量审核</el-button>
          <el-button type="warning" plain :icon="Download" @click="handleBatchDownload">下载附件</el-button>
      </div>

      <el-table
        v-loading="loading"
        :data="projects"
        style="width: 100%"
        border
        stripe
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" align="center" />
        <el-table-column type="index" label="序号" width="60" align="center" />
        <el-table-column
          prop="title"
          label="项目名称"
          min-width="220"
          show-overflow-tooltip
        >
          <template #default="{ row }">
            <span class="project-title">{{ row.title }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="level_display" label="项目级别" width="100" align="center">
          <template #default="{ row }">
            <el-tag size="small" effect="plain">{{ row.level_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="category_display" label="项目类别" width="120" align="center">
          <template #default="{ row }">
            <el-tag effect="light" size="small" type="info">{{ row.category_display }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="重点领域项目" width="110" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.is_key_field" type="success" size="small">是</el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="重点领域代码" width="110" align="center">
          <template #default="{ row }">
            <span>{{ row.key_domain_code || "-" }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="leader_name" label="负责人姓名" width="100" align="center" />
        <el-table-column prop="leader_student_id" label="负责人学号" width="120" align="center" />
        <el-table-column prop="college" label="学院" width="140" show-overflow-tooltip align="center" />
        <el-table-column prop="leader_contact" label="联系电话" width="120" align="center" />
        <el-table-column prop="leader_email" label="邮箱" width="180" show-overflow-tooltip align="center" />
        <el-table-column prop="budget" label="项目经费" width="100" align="center">
          <template #default="{ row }">
            {{ row.budget }}
          </template>
        </el-table-column>

        <el-table-column label="审核节点" width="120" align="center">
          <template #default="{ row }">
            <div class="status-dot">
              <span class="dot" :class="getStatusClass(row.status)"></span>
              <span>{{ row.status_display }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" align="center" fixed="right">
          <template #default="{ row }">
            <el-button link type="success" @click="handleApprove(row)"
              >通过</el-button
            >
            <el-button link type="danger" @click="handleReject(row)"
              >驳回</el-button
            >
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

    <!-- 审核对话框 -->
    <el-dialog
      v-model="reviewDialogVisible"
      :title="reviewType === 'approve' ? '审核通过' : '驳回申请'"
      width="480px"
      align-center
      destroy-on-close
    >
      <el-form :model="reviewForm" label-position="top">
        <el-form-item v-if="reviewType === 'reject'" label="驳回去向">
          <el-radio-group v-model="reviewForm.reject_to">
            <el-radio label="student">退回学生</el-radio>
            <el-radio label="teacher">退回导师</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item
          :label="
            reviewType === 'approve' ? '审核意见 (可选)' : '驳回原因 (必填)'
          "
        >
          <el-input
            v-model="reviewForm.comment"
            type="textarea"
            :rows="4"
            :placeholder="
              reviewType === 'approve' ? '请输入...' : '请输入驳回的具体原因...'
            "
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

    <el-dialog v-model="batchDialogVisible" title="批量审核" width="520px">
      <el-form label-position="top">
        <el-form-item label="审核结果">
          <el-radio-group v-model="batchForm.action">
            <el-radio label="approve">通过</el-radio>
            <el-radio label="reject">驳回</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="batchForm.action === 'reject'" label="驳回去向">
          <el-radio-group v-model="batchForm.reject_to">
            <el-radio label="student">退回学生</el-radio>
            <el-radio label="teacher">退回导师</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="结题评价">
          <el-select v-model="batchForm.closure_rating" placeholder="请选择" style="width: 100%">
            <el-option v-for="item in closureRatingOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="审核意见">
          <el-input v-model="batchForm.comments" type="textarea" :rows="4" placeholder="请输入审核意见" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="batchDialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="batchSubmitting" @click="submitBatchReview">
            提交
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { ElMessage } from "element-plus";
import { Search, Download } from "@element-plus/icons-vue";
import {
  getReviewProjects,
  approveProject,
  rejectProject,
  batchDownloadAttachments,
} from "@/api/admin";
import request from "@/utils/request";
import { useDictionary } from "@/composables/useDictionary";
import { DICT_CODES } from "@/api/dictionary";

const loading = ref(false);
const projects = ref<any[]>([]);
const searchQuery = ref("");
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);
const selectedRows = ref<any[]>([]);

const reviewDialogVisible = ref(false);
const reviewType = ref<"approve" | "reject">("approve");
const reviewForm = ref({
  projectId: 0,
  comment: "",
  reject_to: "student",
});

const batchDialogVisible = ref(false);
const batchSubmitting = ref(false);
const batchForm = ref({
  action: "approve",
  comments: "",
  closure_rating: "",
  reject_to: "student",
});

const { loadDictionaries, getOptions } = useDictionary();
const closureRatingOptions = computed(() => getOptions(DICT_CODES.CLOSURE_RATING));

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
      selectedRows.value = [];
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
  reviewForm.value.reject_to = "student";
  reviewDialogVisible.value = true;
};

const handleReject = (row: any) => {
  reviewType.value = "reject";
  reviewForm.value.projectId = row.id;
  reviewForm.value.comment = "";
  reviewForm.value.reject_to = "student";
  reviewDialogVisible.value = true;
};

const confirmReview = async () => {
  if (reviewType.value === "reject" && !reviewForm.value.comment) {
    ElMessage.warning("请输入驳回原因");
    return;
  }

  try {
    const data: any = { comment: reviewForm.value.comment };
    if (reviewType.value === "reject") {
      data.reject_to = reviewForm.value.reject_to;
    }

    let response: any;
    if (reviewType.value === "approve") {
      response = await approveProject(reviewForm.value.projectId, data);
    } else {
      response = await rejectProject(reviewForm.value.projectId, data);
    }

    if (response.code === 200) {
      ElMessage.success(reviewType.value === "approve" ? "已通过" : "已驳回");
      reviewDialogVisible.value = false;
      fetchProjects();
    }
  } catch (error) {
    ElMessage.error("操作失败");
  }
};

const handleSelectionChange = (val: any[]) => {
  selectedRows.value = val;
};

const openBatchDialog = () => {
  if (selectedRows.value.length === 0) {
    ElMessage.warning("请先勾选要审核的项目");
    return;
  }
  batchForm.value = { action: "approve", comments: "", closure_rating: "", reject_to: "student" };
  batchDialogVisible.value = true;
};

const submitBatchReview = async () => {
  if (selectedRows.value.length === 0) return;
  batchSubmitting.value = true;
  try {
    const payload: any = {
      review_ids: selectedRows.value.map((row) => row.review_id),
      action: batchForm.value.action,
      comments: batchForm.value.comments,
    };
    if (batchForm.value.action === "reject") {
      payload.reject_to = batchForm.value.reject_to;
    }
    if (batchForm.value.closure_rating) {
      payload.closure_rating = batchForm.value.closure_rating;
    }
    const res: any = await request.post("/reviews/batch-review/", payload);
    if (res.code === 200) {
      ElMessage.success("批量审核完成");
      batchDialogVisible.value = false;
      selectedRows.value = [];
      fetchProjects();
    }
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || "批量审核失败");
  } finally {
    batchSubmitting.value = false;
  }
};

const handleBatchDownload = async () => {
  try {
    ElMessage.info("正在打包附件，请稍候...");
    const params: any = {};

    if (selectedRows.value.length > 0) {
      params.ids = selectedRows.value.map((row) => row.id).join(",");
    } else {
      // For review page, we implicitly filter by 'type=closure' and current search
      params.search = searchQuery.value;
      params.status = "CLOSURE_SUBMITTED"; // Or however getReviewProjects filters
      // Wait, getReviewProjects uses type='closure'.
      // batchDownloadAttachments expects project filters.
      // Admin Review List logic filters for closure statuses.
      // We should probably rely on IDs selection for safety in Review page, OR replicate filters.
      // Replicating filters:
      // The Review API finds projects with status__in=[CLOSURE_xxx].
      // The batch download API uses Project filters (status=?).
      // If we want to download ALL pending review projects, we need to pass a list of statuses.
      // But managing views doesn't easily support "list of statuses" via single 'status' param unless backend supports it.
      // Backend 'status' filter: `queryset.filter(status=project_status)`. Single status.
      // So downloading ALL without selection is tricky here unless we add 'type=closure' to export API.
      // I'll stick to: If selection, download selection. If no selection, warn user to select?
      // Or better, just support IDs for now to avoid complexity.
      // User manual says "Download Attachments". Usually implies selected.
    }

    if (!params.ids) {
      ElMessage.warning("请先勾选要下载的项目");
      return;
    }

    const res: any = await batchDownloadAttachments(params);
    if (res.type === "application/json") {
      const text = await res.text();
      const json = JSON.parse(text);
      ElMessage.error(json.message || "下载失败");
      return;
    }
    downloadFile(res, "校级结题审核附件.zip");
    ElMessage.success("下载成功");
  } catch (error) {
    ElMessage.error("下载失败");
  }
};

const downloadFile = (blob: Blob, filename: string) => {
  const url = window.URL.createObjectURL(new Blob([blob]));
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

const getStatusClass = (status: string) => {
  if (status.includes("APPROVED")) return "dot-success";
  if (status.includes("REJECTED")) return "dot-danger";
  if (status.includes("REVIEWING") || status === "SUBMITTED")
    return "dot-warning";
  return "dot-info";
};

onMounted(() => {
  loadDictionaries([DICT_CODES.CLOSURE_RATING]);
  fetchProjects();
});
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.review-page {
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

.action-bar {
    display: flex;
    justify-content: flex-end;
}

.pagination-container {
    display: flex;
    justify-content: flex-end;
}

.ml-2 { margin-left: 8px; }
.mb-4 { margin-bottom: 16px; }
.mt-4 { margin-top: 16px; }

.project-title {
  font-weight: 500;
  color: $slate-800;
  font-size: 14px;
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

    &.dot-success {
      background: $success;
      box-shadow: 0 0 0 2px rgba($success, 0.2);
    }
    &.dot-warning {
      background: $warning;
      box-shadow: 0 0 0 2px rgba($warning, 0.2);
    }
    &.dot-danger {
      background: $danger;
      box-shadow: 0 0 0 2px rgba($danger, 0.2);
    }
    &.dot-info {
      background: $slate-400;
    }
  }
}
</style>
