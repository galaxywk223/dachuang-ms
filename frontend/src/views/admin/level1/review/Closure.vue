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
            <ProjectStatusBadge :status="row.status" :label="row.status_display" />
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
import { ref, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { Search, Download } from "@element-plus/icons-vue";
import { batchDownloadAttachments } from "@/api/projects/admin";
import ProjectStatusBadge from "@/components/business/project/StatusBadge.vue";
import request from "@/utils/request";

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
});

const batchDialogVisible = ref(false);
const batchSubmitting = ref(false);
const batchForm = ref({
  action: "approve",
  comments: "",
});


const resolveList = (payload: any) => {
  if (Array.isArray(payload)) return payload;
  if (payload?.results) return payload.results;
  if (payload?.data?.results) return payload.data.results;
  return payload?.data || [];
};

const resolveCount = (payload: any) => {
  if (typeof payload?.total === "number") return payload.total;
  if (typeof payload?.count === "number") return payload.count;
  if (typeof payload?.data?.count === "number") return payload.data.count;
  if (typeof payload?.data?.total === "number") return payload.data.total;
  return 0;
};

const fetchProjects = async () => {
  loading.value = true;
  try {
    const projectRes: any = await request.get("/projects/", {
      params: {
        page: currentPage.value,
        page_size: pageSize.value,
        search: searchQuery.value,
        status: "CLOSURE_LEVEL1_REVIEWING",
        phase: "CLOSURE",
        phase_step: "SCHOOL_EXPERT_SCORING",
      },
    });

    const data = projectRes?.data ?? projectRes;
    projects.value = resolveList(data);
    total.value = resolveCount(data) || projects.value.length;
    selectedRows.value = [];
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
    if (reviewType.value === "approve") {
      const res: any = await request.post(
        `/projects/${reviewForm.value.projectId}/workflow/finalize-closure/`,
        { action: "approve" }
      );
      if (res?.code === 200) {
        ElMessage.success("结题已通过");
      } else {
        ElMessage.error(res?.message || "操作失败");
        return;
      }
    } else {
      const res: any = await request.post(
        `/projects/${reviewForm.value.projectId}/workflow/finalize-closure/`,
        { action: "return", reason: reviewForm.value.comment }
      );
      if (res?.code === 200) {
        ElMessage.success("已退回学生修改");
      } else {
        ElMessage.error(res?.message || "操作失败");
        return;
      }
    }

    reviewDialogVisible.value = false;
    fetchProjects();
  } catch (error: any) {
    ElMessage.error(error.response?.data?.message || error.message || "操作失败");
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
  batchForm.value = { action: "approve", comments: "" };
  batchDialogVisible.value = true;
};

const submitBatchReview = async () => {
  if (selectedRows.value.length === 0) return;
  if (batchForm.value.action === "reject" && !batchForm.value.comments) {
    ElMessage.warning("请输入驳回原因");
    return;
  }

  batchSubmitting.value = true;
  try {
    let okCount = 0;
    for (const row of selectedRows.value) {
      try {
        if (batchForm.value.action === "approve") {
          const res: any = await request.post(`/projects/${row.id}/workflow/finalize-closure/`, { action: 'approve' });
          if (res?.code === 200) okCount += 1;
        } else {
          const res: any = await request.post(`/projects/${row.id}/workflow/finalize-closure/`, {
            action: 'return',
            reason: batchForm.value.comments,
          });
          if (res?.code === 200) okCount += 1;
        }
      } catch {
        // continue
      }
    }

    ElMessage.success(`批量处理完成：成功 ${okCount}/${selectedRows.value.length}`);
    batchDialogVisible.value = false;
    selectedRows.value = [];
    fetchProjects();
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

onMounted(() => {
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

</style>
