<template>
  <div class="change-review-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span class="title">项目异动审核</span>
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
import { getChangeRequests, reviewChangeRequest } from "@/api/change-requests";

const loading = ref(false);
const reviewing = ref(false);
const requests = ref<any[]>([]);
const dialogVisible = ref(false);
const currentId = ref<number | null>(null);
const comments = ref("");

const fetchRequests = async () => {
  loading.value = true;
  try {
    const res: any = await getChangeRequests({ status: "TEACHER_REVIEWING" });
    const payload = res.data || res;
    const list = payload.data || payload.results || payload;
    requests.value = Array.isArray(list) ? list : [];
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const openReview = (row: any) => {
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
