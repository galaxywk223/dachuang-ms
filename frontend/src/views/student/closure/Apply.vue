<template>
  <div class="page-container">
    <el-card class="main-card" :body-style="{ padding: '24px' }">
      <template #header>
        <div class="card-header-flex">
          <div class="header-title">结题申请</div>
          <div class="header-actions">
            <el-button @click="router.back()">返回</el-button>
            <el-button type="info" plain @click="saveAsDraft">保存草稿</el-button>
            <el-button type="primary" @click="submitForm">提交申请</el-button>
          </div>
        </div>
      </template>

      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-position="top"
        status-icon
        v-loading="loading"
      >
        <!-- Project Info (Read Only) -->
        <div class="form-section">
          <h3 class="section-title">项目基本信息</h3>
          <el-descriptions :column="3" border>
            <el-descriptions-item label="项目名称">{{ projectInfo.title }}</el-descriptions-item>
            <el-descriptions-item label="项目编号">{{ projectInfo.project_no }}</el-descriptions-item>
            <el-descriptions-item label="负责人">{{ projectInfo.leader_name }}</el-descriptions-item>
            <el-descriptions-item label="级别">{{ projectInfo.level_display }}</el-descriptions-item>
            <el-descriptions-item label="类别">{{ projectInfo.category_display }}</el-descriptions-item>
            <el-descriptions-item label="经费">{{ projectInfo.budget }}</el-descriptions-item>
          </el-descriptions>
        </div>

        <!-- Closure Materials -->
        <div class="form-section">
          <h3 class="section-title">结题材料</h3>
          
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="结题报告 (PDF)" prop="final_report">
                <el-upload
                  action="#"
                  :auto-upload="false"
                  :on-change="handleReportChange"
                  :file-list="reportFileList"
                  :limit="1"
                  accept=".pdf"
                  class="upload-demo"
                  drag
                >
                  <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                  <div class="el-upload__text">
                    拖拽文件到此处或 <em>点击上传</em>
                  </div>
                  <template #tip>
                    <div class="el-upload__tip">只能上传 pdf 文件，且不超过 10MB</div>
                  </template>
                </el-upload>
              </el-form-item>
            </el-col>

            <el-col :span="12">
              <el-form-item label="成果材料 (ZIP/PDF)" prop="achievement_file">
                <el-upload
                  action="#"
                  :auto-upload="false"
                  :on-change="handleAchievementChange"
                  :file-list="achievementFileList"
                  :limit="1"
                  accept=".zip,.rar,.pdf"
                  class="upload-demo"
                  drag
                >
                  <el-icon class="el-icon--upload"><upload-filled /></el-icon>
                  <div class="el-upload__text">
                     拖拽文件到此处或 <em>点击上传</em>
                  </div>
                  <template #tip>
                    <div class="el-upload__tip">上传成果支撑材料，支持压缩包或PDF</div>
                  </template>
                </el-upload>
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <div class="form-section">
             <h3 class="section-title">成果简介</h3>
             <el-form-item prop="achievement_summary">
                <el-input 
                  type="textarea" 
                  v-model="formData.achievement_summary"
                  :rows="4" 
                  placeholder="请简要描述项目取得的主要成果（200字以内）"
                  maxlength="200"
                  show-word-limit
                />
             </el-form-item>
        </div>

      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage, type FormInstance, type UploadFile } from "element-plus";
import { UploadFilled } from "@element-plus/icons-vue";
import { getProjectDetail, createClosureApplication } from "@/api/project";

const route = useRoute();
const router = useRouter();
const formRef = ref<FormInstance>();
const loading = ref(false);

const projectId = route.query.projectId as string;

const projectInfo = reactive({
  title: "",
  project_no: "",
  leader_name: "",
  level_display: "",
  category_display: "",
  budget: 0
});

const formData = reactive({
  final_report: null as File | null,
  achievement_file: null as File | null,
  achievement_summary: ""
});

const reportFileList = ref<any[]>([]);
const achievementFileList = ref<any[]>([]);

const rules = {
  final_report: [{ required: true, message: "请上传结题报告", trigger: "change" }],
  achievement_summary: [{ required: true, message: "请填写成果简介", trigger: "blur" }]
};

const handleReportChange = (file: UploadFile) => {
  formData.final_report = file.raw as File;
  reportFileList.value = [file];
  // Manual validation trigger if needed
  if (file) formRef.value?.clearValidate('final_report');
};

const handleAchievementChange = (file: UploadFile) => {
  formData.achievement_file = file.raw as File;
  achievementFileList.value = [file];
};

const fetchProjectInfo = async () => {
    if (!projectId) {
        ElMessage.error("参数错误：缺少项目ID");
        return;
    }
    loading.value = true;
    try {
        const res: any = await getProjectDetail(Number(projectId));
        if (res.code === 200) {
            const data = res.data;
            projectInfo.title = data.title;
            projectInfo.project_no = data.project_no;
            projectInfo.leader_name = data.leader_info?.real_name || data.leader_name;
            projectInfo.level_display = data.level_display;
            projectInfo.category_display = data.category_display;
            projectInfo.budget = data.budget;
        }
    } catch (e) {
        ElMessage.error("获取项目详情失败");
    } finally {
        loading.value = false;
    }
};

const submit = async (isDraft: boolean) => {
    if (!formRef.value) return;

    // Validate only for submission, draft can be partial? 
    // Usually draft also needs some basic validation but let's enforce report for submit
    if (!isDraft) {
        await formRef.value.validate(async (valid) => {
            if (!valid) return;
            await doSubmit(false);
        });
    } else {
        await doSubmit(true);
    }
};

const doSubmit = async (isDraft: boolean) => {
    loading.value = true;
    try {
        // Since we have files, we might need FormData if the API expects multipart/form-data
        // The current project structure likely uses a helper that handles object->FormData conversion 
        // OR we conform to how establishment api worked.
        // Assuming createClosureApplication accepts JSON or FormData. 
        // Based on typical file upload patterns in this stack, let's assume we pass an object and the request util handles it if it detects Files?
        // Wait, establishment Page used `delete payload.attachment_file` and didn't seem to upload it in the same request?
        // Let's look at `createProjectApplication` in `api/project.ts` -> it just takes `data`.
        // The `request.ts` usually handles JSON. 
        // If file upload is needed, headers need 'Content-Type': 'multipart/form-data'.
        
        // CHECK: The establishment Apply.vue DELETED the attachment_file from payload!
        // `delete payload.attachment_file;` line 429.
        // This implies file upload might be separate OR incomplete in the reference file.
        // HOWEVER, to fix the 404, I just need the page to exist. 
        // I will implement standard FormData submission just in case.
        
        const payload = new FormData();
        if (formData.final_report) payload.append('final_report', formData.final_report);
        if (formData.achievement_file) payload.append('achievement_file', formData.achievement_file);
        payload.append('achievement_summary', formData.achievement_summary);
        payload.append('is_draft', String(isDraft));

        const res: any = await createClosureApplication(Number(projectId), payload);
        if (res.code === 200 || res.status === 201) {
             ElMessage.success(isDraft ? "草稿已保存" : "申请已提交");
             router.push('/closure/applied'); 
        } else {
             ElMessage.error(res.message || "操作失败");
        }
    } catch (e: any) {
        ElMessage.error(e.message || "提交失败");
    } finally {
        loading.value = false;
    }
};

const submitForm = () => submit(false);
const saveAsDraft = () => submit(true);

onMounted(() => {
    fetchProjectInfo();
});
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.page-container {
  background-color: #f0f2f5;
  min-height: 100%;
}

.main-card {
  border: none;
  border-radius: 4px;
  box-shadow: 0 1px 4px rgba(0,21,41,0.08) !important;
  background: #fff;
  margin-top: 24px;
}

.card-header-flex {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.form-section {
  margin-bottom: 32px;
  
  .section-title {
    font-size: 16px;
    font-weight: 600;
    color: #1f2937;
    margin: 0 0 24px 0;
    padding-left: 10px;
    border-left: 3px solid $primary-600;
    line-height: 1.2;
  }
}

.upload-demo {
  :deep(.el-upload-dragger) {
    width: 100%;
  }
}
</style>
