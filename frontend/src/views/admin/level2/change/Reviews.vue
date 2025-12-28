<template>
  <div class="change-review-page">
    <el-card class="main-card" shadow="never">
      <template #header>
        <div class="card-header">
           <div class="header-left">
             <span class="header-title">项目异动审核</span>
           </div>
        </div>
      </template>

      <el-table :data="requests" v-loading="loading" border stripe>
        <el-table-column prop="project_no" label="项目编号" width="140" />
        <el-table-column prop="project_title" label="项目名称" min-width="180" />
        <el-table-column prop="request_type_display" label="类型" width="120" />
        <el-table-column prop="leader_name" label="负责人" width="120" />
        <el-table-column prop="status_display" label="状态" width="140" />
        <el-table-column label="操作" width="180">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="openReview(row)">审核</el-button>
            <el-button v-if="row.attachment_url" size="small" @click="openAttachment(row.attachment_url)">附件</el-button>
          </template>
        </el-table-column>
      </el-table>
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
import { getChangeRequests, reviewChangeRequest } from "@/api/projects/change-requests";

defineOptions({ name: "Level2ChangeReviewsView" });

type ChangeRequestRow = {
  id: number;
  project_no?: string;
  project_title?: string;
  request_type_display?: string;
  leader_name?: string;
  status_display?: string;
  attachment_url?: string;
};

type ChangeRequestListResponse = {
  data?: {
    results?: ChangeRequestRow[];
  } | ChangeRequestRow[];
  results?: ChangeRequestRow[];
};

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null;

const getErrorMessage = (error: unknown, fallback: string) => {
  if (!isRecord(error)) return fallback;
  const response = error.response;
  if (isRecord(response) && isRecord(response.data) && typeof response.data.message === "string") {
    return response.data.message;
  }
  if (typeof error.message === "string") return error.message;
  return fallback;
};

const loading = ref(false);
const reviewing = ref(false);
const requests = ref<ChangeRequestRow[]>([]);
const dialogVisible = ref(false);
const currentId = ref<number | null>(null);
const comments = ref("");

const fetchRequests = async () => {
  loading.value = true;
  try {
    const res = (await getChangeRequests({ status: "LEVEL2_REVIEWING" })) as ChangeRequestListResponse;
    const payload = isRecord(res) && "data" in res ? res.data : res;
    const list = isRecord(payload) ? payload.results : payload;
    requests.value = Array.isArray(list) ? list : [];
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const openReview = (row: ChangeRequestRow) => {
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
  } catch (error) {
    ElMessage.error(getErrorMessage(error, "操作失败"));
  } finally {
    reviewing.value = false;
  }
};

const openAttachment = (url: string) => {
  window.open(url, "_blank");
};

onMounted(() => {
  fetchRequests();
});
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.change-review-page {
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
  align-items: center;
  justify-content: space-between;
}

.header-left {
    display: flex;
    align-items: center;
}

.header-title {
    font-size: 16px;
    color: $slate-800;
}
</style>
