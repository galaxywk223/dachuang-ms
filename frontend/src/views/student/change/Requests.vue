<template>
  <div class="change-requests-page">
    <el-card class="main-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-left">
             <span class="header-title">项目异动申请</span>
          </div>
          <div class="header-actions">
             <el-button type="primary" @click="openDialog">新建申请</el-button>
          </div>
        </div>
      </template>

      <el-table :data="requests" v-loading="loading" border stripe>
        <el-table-column prop="project_no" label="项目编号" width="140" />
        <el-table-column prop="project_title" label="项目名称" min-width="180" />
        <el-table-column prop="request_type_display" label="类型" width="120" />
        <el-table-column prop="status_display" label="状态" width="140" />
        <el-table-column prop="submitted_at" label="提交时间" width="160" />
        <el-table-column label="操作" width="220">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'DRAFT'"
              size="small"
              type="primary"
              @click="editRequest(row)"
            >
              编辑
            </el-button>
            <el-button
              v-if="row.status === 'DRAFT'"
              size="small"
              type="success"
              @click="submitRequest(row)"
            >
              提交
            </el-button>
            <el-button
              v-if="row.attachment_url"
              size="small"
              @click="openAttachment(row.attachment_url)"
            >
              附件
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" title="项目异动申请" width="620px" destroy-on-close>
      <el-form :model="form" label-width="120px">
        <el-form-item label="项目" required>
          <el-select v-model="form.project" placeholder="请选择项目" style="width: 100%">
            <el-option v-for="item in projectOptions" :key="item.id" :label="item.title" :value="item.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="类型" required>
          <el-select v-model="form.request_type" placeholder="请选择类型" style="width: 100%">
            <el-option label="项目变更" value="CHANGE" />
            <el-option label="项目终止" value="TERMINATION" />
            <el-option label="项目延期" value="EXTENSION" />
          </el-select>
        </el-form-item>
        <el-form-item label="原因">
          <el-input v-model="form.reason" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item v-if="form.request_type === 'EXTENSION'" label="延期至" required>
          <el-date-picker v-model="form.requested_end_date" type="date" value-format="YYYY-MM-DD" style="width: 100%" />
        </el-form-item>
        <el-form-item v-if="form.request_type === 'CHANGE'" label="变更内容(JSON)">
          <el-input v-model="changeDataText" type="textarea" :rows="4" placeholder='{"title":"新名称"}' />
        </el-form-item>
        <el-form-item label="附件">
          <el-upload
            action="#"
            :auto-upload="false"
            :limit="1"
            :on-change="handleFileChange"
            :file-list="fileList"
          >
            <el-button type="primary" plain>选择文件</el-button>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" :loading="saving" @click="saveDraft">保存草稿</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { ElMessage, type UploadFile, type UploadUserFile } from "element-plus";
import { getChangeRequests, createChangeRequest, updateChangeRequest, submitChangeRequest } from "@/api/projects/change-requests";
import request from "@/utils/request";

defineOptions({
  name: "StudentChangeRequestsView",
});

type ProjectOption = {
  id: number;
  title: string;
};

type ChangeRequest = {
  id: number;
  project: number;
  project_no?: string;
  project_title?: string;
  request_type?: string;
  request_type_display?: string;
  status?: string;
  status_display?: string;
  submitted_at?: string;
  requested_end_date?: string;
  reason?: string;
  attachment_url?: string;
  change_data?: Record<string, unknown>;
};

type RequestForm = {
  id: number | null;
  project: number | null;
  request_type: string;
  reason: string;
  requested_end_date: string;
};

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null;

const resolveList = <T,>(payload: unknown): T[] => {
  if (Array.isArray(payload)) return payload as T[];
  if (isRecord(payload) && Array.isArray(payload.results)) {
    return payload.results as T[];
  }
  if (
    isRecord(payload) &&
    isRecord(payload.data) &&
    Array.isArray(payload.data.results)
  ) {
    return payload.data.results as T[];
  }
  if (isRecord(payload) && Array.isArray(payload.data)) {
    return payload.data as T[];
  }
  return [];
};

const getErrorMessage = (error: unknown, fallback: string) => {
  if (error instanceof Error) {
    return error.message || fallback;
  }
  if (typeof error === "string") {
    return error || fallback;
  }
  return fallback;
};

const loading = ref(false);
const saving = ref(false);
const dialogVisible = ref(false);
const requests = ref<ChangeRequest[]>([]);
const projectOptions = ref<ProjectOption[]>([]);
const fileList = ref<UploadUserFile[]>([]);
const attachmentFile = ref<File | null>(null);

const form = reactive<RequestForm>({
  id: null,
  project: null,
  request_type: "CHANGE",
  reason: "",
  requested_end_date: "",
});
const changeDataText = ref("{}");

const fetchRequests = async () => {
  loading.value = true;
  try {
    const res = await getChangeRequests();
    const payload = isRecord(res) && isRecord(res.data) ? res.data : res;
    requests.value = resolveList<ChangeRequest>(payload);
  } catch (error: unknown) {
    console.error(error);
  } finally {
    loading.value = false;
  }
};

const fetchProjects = async () => {
  const res = await request.get("/projects/", {
    params: {
      status_in:
        "IN_PROGRESS,MID_TERM_DRAFT,MID_TERM_SUBMITTED,MID_TERM_REVIEWING,MID_TERM_APPROVED",
    },
  });
  const payload = isRecord(res) && isRecord(res.data) ? res.data : res;
  projectOptions.value = resolveList<ProjectOption>(payload);
};

const openDialog = () => {
  form.id = null;
  form.project = null;
  form.request_type = "CHANGE";
  form.reason = "";
  form.requested_end_date = "";
  changeDataText.value = "{}";
  attachmentFile.value = null;
  fileList.value = [];
  dialogVisible.value = true;
};

const editRequest = (row: ChangeRequest) => {
  form.id = row.id;
  form.project = row.project;
  form.request_type = row.request_type ?? "";
  form.reason = row.reason || "";
  form.requested_end_date = row.requested_end_date || "";
  changeDataText.value = JSON.stringify(row.change_data || {}, null, 2);
  dialogVisible.value = true;
};

const handleFileChange = (file: UploadFile) => {
  attachmentFile.value = file.raw || null;
  fileList.value = file.raw ? [{ name: file.name, url: "" }] : [];
};

const saveDraft = async () => {
  saving.value = true;
  try {
    let changeData = {};
    try {
      changeData = JSON.parse(changeDataText.value || "{}");
    } catch {
      ElMessage.error("变更内容不是有效的JSON");
      saving.value = false;
      return;
    }

    const payload = new FormData();
    payload.append("project", String(form.project || ""));
    payload.append("request_type", form.request_type);
    payload.append("reason", form.reason || "");
    if (form.request_type === "EXTENSION" && form.requested_end_date) {
      payload.append("requested_end_date", form.requested_end_date);
    }
    if (form.request_type === "CHANGE") {
      payload.append("change_data", JSON.stringify(changeData));
    }
    if (attachmentFile.value) {
      payload.append("attachment", attachmentFile.value);
    }

    if (form.id) {
      await updateChangeRequest(form.id, payload);
    } else {
      await createChangeRequest(payload);
    }
    ElMessage.success("保存成功");
    dialogVisible.value = false;
    fetchRequests();
  } catch (error: unknown) {
    ElMessage.error(getErrorMessage(error, "保存失败"));
  } finally {
    saving.value = false;
  }
};

const submitRequest = async (row: ChangeRequest) => {
  try {
    await submitChangeRequest(row.id);
    ElMessage.success("提交成功");
    fetchRequests();
  } catch (error: unknown) {
    ElMessage.error(getErrorMessage(error, "提交失败"));
  }
};

const openAttachment = (url: string) => {
  window.open(url, "_blank");
};

onMounted(() => {
  fetchRequests();
  fetchProjects();
});
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.change-requests-page {
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

.header-actions {
    display: flex;
    gap: 12px;
}
</style>
