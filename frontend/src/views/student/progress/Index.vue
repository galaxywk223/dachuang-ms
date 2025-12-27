<template>
  <div class="progress-page">
    <el-card class="main-card" shadow="never">
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <span class="header-title">项目进度</span>
            <el-tag v-if="activeProject" size="small" effect="plain" class="ml-2">
              {{ activeProject.title }}
            </el-tag>
          </div>
          <div class="header-actions">
            <el-select
              v-model="activeProjectId"
              placeholder="选择项目"
              filterable
              clearable
              style="width: 260px"
              class="mr-2"
              @change="handleProjectChange"
            >
              <el-option
                v-for="item in projects"
                :key="item.id"
                :label="`${item.project_no || ''} ${item.title}`"
                :value="item.id"
              />
            </el-select>
            <el-button type="primary" :disabled="!activeProjectId" @click="openDialog">新增进度</el-button>
          </div>
        </div>
      </template>

      <div v-if="projects.length === 0" class="empty-container">
        <el-empty description="暂无可管理的项目" />
      </div>

      <div v-else>
        <div v-if="!activeProjectId" class="empty-container">
          <el-empty description="请选择项目" />
        </div>

        <div v-else>
          <el-table v-loading="loading" :data="progressList" stripe border style="width: 100%">
            <el-table-column prop="title" label="进度标题" min-width="200" show-overflow-tooltip />
            <el-table-column prop="content" label="进度内容" min-width="240" show-overflow-tooltip />
            <el-table-column prop="creator_name" label="提交人" width="120" />
            <el-table-column prop="created_at" label="提交时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="附件" width="120" align="center">
              <template #default="{ row }">
                <el-link v-if="row.attachment" :href="row.attachment" target="_blank" type="primary">查看</el-link>
                <span v-else>-</span>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120" align="center" fixed="right">
              <template #default="{ row }">
                <el-button link type="danger" size="small" @click="handleDelete(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>

          <el-empty
            v-if="!loading && progressList.length === 0"
            description="暂无进度记录"
            :image-size="160"
            class="mt-4"
          />
        </div>
      </div>
    </el-card>

    <el-dialog v-model="dialogVisible" title="新增进度" width="520px" @closed="resetForm">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="90px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入进度标题" />
        </el-form-item>
        <el-form-item label="内容" prop="content">
          <el-input v-model="form.content" type="textarea" :rows="4" placeholder="请输入进度内容" />
        </el-form-item>
        <el-form-item label="附件">
          <el-upload
            :auto-upload="false"
            :limit="1"
            :file-list="fileList"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
          >
            <el-button type="primary" plain>选择附件</el-button>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from "vue";
import { ElMessage, ElMessageBox, type FormInstance, type UploadUserFile } from "element-plus";
import dayjs from "dayjs";
import {
  addProjectProgress,
  getProjectProgress,
  getProjects,
  removeProjectProgress,
} from "@/api/projects";

const loading = ref(false);
const submitting = ref(false);
const dialogVisible = ref(false);
const projects = ref<any[]>([]);
const progressList = ref<any[]>([]);
const activeProjectId = ref<number | null>(null);
const fileList = ref<UploadUserFile[]>([]);
const formRef = ref<FormInstance>();

const form = reactive({
  title: "",
  content: "",
  attachment: null as File | null,
});

const rules = {
  title: [{ required: true, message: "请输入进度标题", trigger: "blur" }],
  content: [{ required: true, message: "请输入进度内容", trigger: "blur" }],
};

const activeProject = computed(
  () => projects.value.find((item) => item.id === activeProjectId.value) || null
);

const formatDate = (value?: string) => {
  if (!value) return "-";
  return dayjs(value).format("YYYY-MM-DD HH:mm");
};

const fetchProjects = async () => {
  try {
    const res: any = await getProjects({ page_size: 200 });
    projects.value = res?.data?.results || res?.data || res || [];
    if (!activeProjectId.value && projects.value.length > 0) {
      activeProjectId.value = projects.value[0].id;
    }
  } catch (error) {
    console.error(error);
  }
};

const fetchProgress = async () => {
  if (!activeProjectId.value) {
    progressList.value = [];
    return;
  }
  loading.value = true;
  try {
    const res: any = await getProjectProgress(activeProjectId.value);
    const payload = res?.data || res;
    progressList.value = payload?.data || payload || [];
  } catch (error: any) {
    ElMessage.error(error.message || "获取进度失败");
  } finally {
    loading.value = false;
  }
};

const handleProjectChange = () => {
  fetchProgress();
};

const openDialog = () => {
  if (!activeProjectId.value) {
    ElMessage.warning("请先选择项目");
    return;
  }
  dialogVisible.value = true;
};

const resetForm = () => {
  form.title = "";
  form.content = "";
  form.attachment = null;
  fileList.value = [];
  formRef.value?.clearValidate();
};

const handleFileChange = (file: UploadUserFile) => {
  if (file.raw) {
    form.attachment = file.raw;
  }
  fileList.value = [file];
};

const handleFileRemove = () => {
  form.attachment = null;
  fileList.value = [];
};

const handleSubmit = async () => {
  if (!formRef.value || !activeProjectId.value) return;
  await formRef.value.validate(async (valid) => {
    if (!valid) return;
    submitting.value = true;
    try {
      const payload = new FormData();
      payload.append("title", form.title);
      payload.append("content", form.content);
      if (form.attachment) payload.append("attachment", form.attachment);
      const res: any = await addProjectProgress(activeProjectId.value as number, payload);
      if (res?.code === 200) {
        ElMessage.success("进度已提交");
        dialogVisible.value = false;
        fetchProgress();
      } else {
        ElMessage.error(res?.message || "提交失败");
      }
    } catch (error: any) {
      ElMessage.error(error.message || "提交失败");
    } finally {
      submitting.value = false;
    }
  });
};

const handleDelete = async (row: any) => {
  if (!activeProjectId.value) return;
  try {
    await ElMessageBox.confirm("确定删除该进度记录吗？", "提示", { type: "warning" });
    const res: any = await removeProjectProgress(activeProjectId.value, row.id);
    if (res?.code === 200) {
      ElMessage.success("已移入回收站");
      fetchProgress();
    } else {
      ElMessage.error(res?.message || "删除失败");
    }
  } catch (error) {
    // cancel
  }
};

onMounted(async () => {
  await fetchProjects();
  fetchProgress();
});
</script>

<style scoped lang="scss">
.progress-page {
  .header-actions {
    display: flex;
    align-items: center;
    gap: 12px;
  }
}
</style>
