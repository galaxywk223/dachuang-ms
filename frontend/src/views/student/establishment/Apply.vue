<template>
  <div class="apply-page">
    <el-card class="page-hero" shadow="hover">
      <div class="hero-text">
        <p class="eyebrow">项目申报</p>
        <h1>申请项目</h1>
        <p class="subtitle">
          请填写下方的分段式表单以完成申报。所有必填项 (*) 均需准确填写。
        </p>
      </div>
      <div class="hero-meta">
        <div class="meta-block">
          <span class="meta-label">负责人</span>
          <div class="meta-value">{{ currentUser.name }}</div>
          <div class="meta-sub">学号 {{ currentUser.student_id }}</div>
        </div>
        <div class="meta-block soft">
          <span class="meta-label">状态</span>
          <div class="meta-sub">
            <el-tag type="info" effect="dark" round>填写中</el-tag>
          </div>
        </div>
      </div>
    </el-card>

    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-position="top"
      class="stacked-form"
      status-icon
      hide-required-asterisk
    >
      <!-- 1. Basic Info -->
      <div class="form-section">
        <div class="section-header">
          <div class="icon-wrapper"><el-icon><InfoFilled /></el-icon></div>
          <div class="header-text">
            <h3>基本信息</h3>
            <p>选择项目来源、级别与重点领域归属</p>
          </div>
        </div>
        <el-card class="section-card" shadow="never">
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="项目来源" prop="source">
                <el-select v-model="formData.source" placeholder="请选择来源" class="full-width" size="large">
                  <el-option v-for="item in sourceOptions" :key="item.value" :label="item.label" :value="item.value" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="项目级别" prop="level">
                <el-select v-model="formData.level" placeholder="请选择级别" class="full-width" size="large">
                  <el-option v-for="item in levelOptions" :key="item.value" :label="item.label" :value="item.value" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="项目类别" prop="category">
                <el-select v-model="formData.category" placeholder="请选择类别" class="full-width" size="large">
                  <el-option v-for="item in categoryOptions" :key="item.value" :label="item.label" :value="item.value" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item prop="is_key_field">
                <template #label>
                  <span class="flex items-center gap-1">
                    重点领域项目
                    <el-tooltip content="是否属于国家重点支持的领域" placement="top">
                      <el-icon class="text-gray-400 cursor-pointer"><QuestionFilled /></el-icon>
                    </el-tooltip>
                  </span>
                </template>
                <el-select v-model="formData.is_key_field" placeholder="请选择" class="full-width" size="large">
                  <el-option v-for="item in specialTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
        </el-card>
      </div>

      <!-- 2. Project Details -->
      <div class="form-section">
        <div class="section-header">
          <div class="icon-wrapper"><el-icon><Document /></el-icon></div>
          <div class="header-text">
            <h3>项目详情</h3>
            <p>填写项目名称、归属学院与经费预算</p>
          </div>
        </div>
        <el-card class="section-card" shadow="never">
          <el-form-item label="项目名称" prop="title">
            <el-input v-model="formData.title" placeholder="请输入项目名称" size="large" />
          </el-form-item>
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="所属学院" prop="college">
                <el-select v-model="formData.college" placeholder="请选择学院" class="full-width" size="large">
                   <el-option v-for="item in collegeOptions" :key="item.value" :label="item.label" :value="item.value" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="所属专业" prop="major_code">
                <el-select v-model="formData.major_code" placeholder="请选择专业" class="full-width" filterable size="large">
                   <el-option v-for="item in majorOptions" :key="item.value" :label="item.label" :value="item.value" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="经费预算 (元)" prop="budget">
            <el-input-number v-model="formData.budget" :min="0" :step="100" class="full-width" size="large" controls-position="right" />
          </el-form-item>
        </el-card>
      </div>

      <!-- 3. Team Info -->
      <div class="form-section">
        <div class="section-header">
           <div class="icon-wrapper"><el-icon><UserFilled /></el-icon></div>
           <div class="header-text">
             <h3>团队组建</h3>
             <p>负责人信息、指导教师与成员列表</p>
           </div>
        </div>
        <el-card class="section-card" shadow="never">
          <el-row :gutter="24">
            <el-col :span="12">
              <el-form-item label="负责人姓名">
                <el-input v-model="currentUser.name" disabled size="large" class="is-disabled-soft" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="负责人学号">
                <el-input v-model="currentUser.student_id" disabled size="large" class="is-disabled-soft" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="联系电话" prop="leader_contact">
                <el-input v-model="formData.leader_contact" placeholder="请输入手机号" size="large" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="电子邮箱" prop="leader_email">
                <el-input v-model="formData.leader_email" placeholder="请输入邮箱" size="large" />
              </el-form-item>
            </el-col>
          </el-row>

          <el-divider content-position="left">指导教师</el-divider>
          
          <div v-for="(advisor, index) in formData.advisors" :key="index" class="dynamic-group">
            <el-row :gutter="16">
              <el-col :span="5">
                <el-input v-model="advisor.job_number" placeholder="工号" size="default" />
              </el-col>
              <el-col :span="5">
                <el-input v-model="advisor.name" placeholder="姓名" size="default" />
              </el-col>
              <el-col :span="5">
                <el-select v-model="advisor.title" placeholder="职称" size="default">
                   <el-option v-for="item in advisorTitleOptions" :key="item.value" :label="item.label" :value="item.value" />
                </el-select>
              </el-col>
              <el-col :span="5">
                <el-input v-model="advisor.contact" placeholder="电话" size="default" />
              </el-col>
              <el-col :span="4" class="flex items-center">
                 <el-button type="danger" link v-if="formData.advisors.length > 1" @click="removeAdvisor(index)">删除</el-button>
                 <el-button type="primary" link v-if="index === formData.advisors.length - 1" @click="addAdvisor">添加</el-button>
              </el-col>
            </el-row>
          </div>

          <el-divider content-position="left">项目成员</el-divider>
          
          <div v-for="(member, index) in formData.members" :key="'m'+index" class="dynamic-group">
            <el-row :gutter="16">
              <el-col :span="10">
                <el-input v-model="member.student_id" placeholder="成员学号" size="default" />
              </el-col>
              <el-col :span="10">
                <el-input v-model="member.name" placeholder="成员姓名" size="default" />
              </el-col>
              <el-col :span="4" class="flex items-center">
                 <el-button type="danger" link v-if="formData.members.length > 1" @click="removeMember(index)">删除</el-button>
                 <el-button type="primary" link v-if="index === formData.members.length - 1" @click="addMember">添加</el-button>
              </el-col>
            </el-row>
          </div>
        </el-card>
      </div>

       <!-- 4. Content -->
      <div class="form-section">
        <div class="section-header">
           <div class="icon-wrapper"><el-icon><EditPen /></el-icon></div>
           <div class="header-text">
             <h3>申报内容</h3>
             <p>简述项目简介与预期成果</p>
           </div>
        </div>
        <el-card class="section-card" shadow="never">
           <el-form-item label="立项预期成果" prop="expected_results">
             <el-input 
               v-model="formData.expected_results" 
               type="textarea" 
               :rows="3" 
               placeholder="调研报告/发表文章/申请专利/参加竞赛/实物/软件" 
               maxlength="200"
               show-word-limit
             />
           </el-form-item>
           <el-form-item label="项目简介 (200字内)" prop="description">
             <el-input 
               v-model="formData.description" 
               type="textarea" 
               :rows="5" 
               placeholder="请输入项目简介..." 
               maxlength="200"
               show-word-limit
             />
           </el-form-item>
        </el-card>
      </div>

       <!-- 5. Attachment -->
      <div class="form-section">
        <div class="section-header">
           <div class="icon-wrapper"><el-icon><UploadFilled /></el-icon></div>
           <div class="header-text">
             <h3>附件上传</h3>
             <p>下载模板并上传申请书</p>
           </div>
        </div>
        <el-card class="section-card" shadow="never">
          <div class="flex items-center gap-4 mb-4">
             <el-button type="success" plain :icon="Download">下载申请书模板</el-button>
             <span class="text-xs text-gray-500">学科竞赛类只需上传获奖证书或立项文件</span>
          </div>
          <el-form-item prop="attachment_file">
            <el-upload
              action="#"
              :auto-upload="false"
              :on-change="handleFileChange"
              :file-list="fileList"
              drag
              class="w-full"
            >
              <el-icon class="el-icon--upload"><upload-filled /></el-icon>
              <div class="el-upload__text">
                拖拽文件到此处或 <em>点击上传</em>
              </div>
              <template #tip>
                <div class="el-upload__tip">
                  支持 PDF 格式，大小不超过 2MB
                </div>
              </template>
            </el-upload>
          </el-form-item>
        </el-card>
      </div>
    </el-form>

    <!-- Floating Action Bar -->
    <div class="action-bar">
      <div class="action-container">
         <div class="status-hint">
           <div class="pulse-dot"></div>
           <span>自动保存草稿中...</span>
         </div>
         <div class="button-group">
            <el-button @click="handleReset">重置</el-button>
            <el-button type="success" plain @click="saveAsDraft">保存草稿</el-button>
            <el-button type="primary" @click="submitForm">提交申请</el-button>
         </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from "vue";
import { ElMessage, type FormInstance } from "element-plus";
import {
  QuestionFilled, UploadFilled, Download, InfoFilled, UserFilled, Document, EditPen
} from "@element-plus/icons-vue";
import { useDictionary } from "@/composables/useDictionary";
import { DICT_CODES } from "@/api/dictionary";
import { useUserStore } from "@/stores/user";

const userStore = useUserStore();
const router = useRouter();
const route = useRoute();
const { loadDictionaries, getOptions } = useDictionary();
const formRef = ref<FormInstance>();

// Import API
import { createProjectApplication, updateProjectApplication, getProjectDetail } from "@/api/project";
import { useRouter, useRoute } from "vue-router";

// Mock User
const currentUser = computed(() => ({
  name: userStore.user?.real_name || "学生用户",
  student_id: userStore.user?.username || "20230001"
}));

const formData = reactive({
  id: null as number | null,
  source: "",
  level: "",
  category: "",
  is_key_field: "NORMAL",
  college: "",
  budget: 0,
  major_code: "",
  leader_contact: "",
  leader_email: "",
  title: "",
  expected_results: "",
  description: "",
  advisors: [{ job_number: "", name: "", title: "", contact: "", email: "" }],
  members: [{ student_id: "", name: "" }],
  attachment_file: null as File | null
});

const fileList = ref([]);
const loading = ref(false);

const rules = {
  source: [{ required: true, message: "必选项", trigger: "change" }],
  level: [{ required: true, message: "必选项", trigger: "change" }],
  category: [{ required: true, message: "必选项", trigger: "change" }],
  title: [{ required: true, message: "必填项", trigger: "blur" }],
  leader_contact: [{ required: true, message: "必填项", trigger: "blur" }],
  leader_email: [{ required: true, message: "必填项", trigger: "blur" }]
};

// Dicts
const sourceOptions = computed(() => getOptions(DICT_CODES.PROJECT_SOURCE));
const collegeOptions = computed(() => getOptions(DICT_CODES.COLLEGE));
const specialTypeOptions = computed(() => getOptions(DICT_CODES.SPECIAL_PROJECT_TYPE));
const majorOptions = computed(() => getOptions(DICT_CODES.MAJOR_CATEGORY));
const advisorTitleOptions = computed(() => getOptions(DICT_CODES.ADVISOR_TITLE));
const levelOptions = computed(() => getOptions(DICT_CODES.PROJECT_LEVEL));
const categoryOptions = computed(() => getOptions(DICT_CODES.PROJECT_CATEGORY));

const addAdvisor = () => formData.advisors.push({ job_number: "", name: "", title: "", contact: "", email: "" });
const removeAdvisor = (i: number) => formData.advisors.splice(i, 1);
const addMember = () => formData.members.push({ student_id: "", name: "" });
const removeMember = (i: number) => formData.members.splice(i, 1);

const handleFileChange = (file: any) => {
  formData.attachment_file = file.raw;
};

// Common submit handler
const handleSaveOrSubmit = async (isDraft: boolean) => {
    if (!formRef.value) return;

    // For draft, we skip full validation or validate loosely if needed
    // For submission, we need full validation
    if (!isDraft) {
        await formRef.value.validate(async (valid) => {
            if (!valid) {
                 ElMessage.error("请完善必填信息");
                 return;
            }
            await processRequest(false);
        });
    } else {
        // Safe to save draft even if incomplete? 
        // Usually yes, but let's at least check title for existence if backend requires it.
        // Assuming backend handles partial data for drafts if valid=false on fields.
        await processRequest(true);
    }
};

const processRequest = async (isDraft: boolean) => {
    // Backend requires Title even for drafts
    if (!formData.title && isDraft) {
        ElMessage.warning("请填写项目名称（草稿必填）");
        return;
    }

    loading.value = true;
    try {
        // Sanitize Payload for Backend
        const payload: any = { 
            ...formData, 
            is_draft: isDraft 
        };

        // Fix Choice Fields (Backend requires valid choices)
        if (!payload.level) payload.level = 'SCHOOL'; 
        if (!payload.category) payload.category = 'INNOVATION_TRAINING';
        
        // Fix Boolean Fields
        // Assuming dictionary uses "YES"/"NO" or "KEY"/"NORMAL"
        // Model requires Boolean.
        // Let's assume if it is "KEY" or "TRUE" or true, it is true.
        // If it is "NORMAL" or "FALSE" or false or empty, it is false.
        const keyFieldVal = payload.is_key_field;
        payload.is_key_field = (keyFieldVal === true || keyFieldVal === 'TRUE' || keyFieldVal === 'YES' || keyFieldVal === 'KEY');

        // Remove Attachment File (handled separately if needed, but keeping for now as discussed)
        // If backend expects 'attachment_file' to be null if no file, ensuring it is null or file object
        if (!payload.attachment_file) payload.attachment_file = null; 
        
        // Ensure numbers
        payload.budget = Number(payload.budget) || 0;
        payload.self_funding = Number(payload.self_funding) || 0;
        // self_funding might be missing in formData, check template
        // Template doesn't show self_funding input? 
        // View requires it? View says: "self_funding": data.get("self_funding", 0) -> safe.

        let response: any;
        if (formData.id) {
            response = await updateProjectApplication(formData.id, payload);
        } else {
            response = await createProjectApplication(payload);
        }
        
        // Axios response wrapper usage
        if (response.code === 200 || response.status === 201) {
            ElMessage.success(isDraft ? "草稿已保存" : "申请已提交");
            if (!isDraft) {
                router.push('/establishment/my-projects');
            } else {
                // Update ID if created
                if (response.data && response.data.id) {
                    formData.id = response.data.id;
                    // Optional: update URL using replace
                     router.replace({ 
                        path: route.path,
                        query: { ...route.query, id: String(response.data.id) } 
                    });
                }
            }
        } else {
            console.error("API Error:", response);
            // Show detailed error if available
            const errorMsg = response.message || "操作失败";
            const details = response.errors ? JSON.stringify(response.errors) : "";
            ElMessage.error(`${errorMsg} ${details}`);
        }
    } catch (e: any) {
        ElMessage.error(e.message || "请求失败");
        console.error(e);
    } finally {
        loading.value = false;
    }
}

const submitForm = () => handleSaveOrSubmit(false);
const saveAsDraft = () => handleSaveOrSubmit(true);
const handleReset = () => formRef.value?.resetFields();

// Load Data if Edit Mode
const loadData = async (id: number) => {
    try {
        const res: any = await getProjectDetail(id);
        if (res.code === 200 && res.data) {
            Object.assign(formData, res.data);
            // Handle lists safety
            if (!formData.advisors || formData.advisors.length === 0) 
                 formData.advisors = [{ job_number: "", name: "", title: "", contact: "", email: "" }];
            if (!formData.members || formData.members.length === 0) 
                 formData.members = [{ student_id: "", name: "" }];
        }
    } catch(e) {
        ElMessage.error("加载项目详情失败");
    }
}

onMounted(() => {
  loadDictionaries([
    DICT_CODES.PROJECT_LEVEL, DICT_CODES.PROJECT_CATEGORY, DICT_CODES.PROJECT_SOURCE,
    DICT_CODES.COLLEGE, DICT_CODES.SPECIAL_PROJECT_TYPE, DICT_CODES.MAJOR_CATEGORY,
    DICT_CODES.ADVISOR_TITLE
  ]);
  
  const id = route.query.id;
  if (id) {
      loadData(Number(id));
  }
});
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.apply-page {
  max-width: 960px;
  margin: 0 auto;
  padding-bottom: 100px; // Space for action bar
}

.page-hero {
  border: none;
  background: linear-gradient(135deg, white 0%, $primary-50 100%);
  border-radius: $radius-lg;
  margin-bottom: 32px;
  
  :deep(.el-card__body) {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 32px;
  }
  
  .eyebrow {
    color: $primary-600;
    font-weight: 600;
    letter-spacing: 0.1em;
    font-size: $font-size-xs;
    text-transform: uppercase;
    margin-bottom: 8px;
  }
  
  h1 {
    font-size: $font-size-3xl;
    color: $slate-900;
    margin-bottom: 12px;
    letter-spacing: -0.5px;
  }
  
  .subtitle {
    color: $slate-500;
    max-width: 500px;
  }
}

.hero-meta {
  display: flex;
  gap: 24px;
  
  .meta-block {
    background: white;
    padding: 16px 24px;
    border-radius: $radius-md;
    box-shadow: $shadow-sm;
    min-width: 140px;
    
    &.soft {
      background: rgba(255,255,255,0.6);
      box-shadow: none;
      border: 1px solid $slate-200;
    }
  }
  
  .meta-label {
    font-size: $font-size-xs;
    color: $slate-400;
    text-transform: uppercase;
    margin-bottom: 4px;
    display: block;
  }
  
  .meta-value {
    font-size: $font-size-lg;
    font-weight: 600;
    color: $slate-800;
  }
  
  .meta-sub {
    font-size: $font-size-xs;
    color: $slate-500;
  }
}

.form-section {
  margin-bottom: 40px;
  
  .section-header {
    display: flex;
    gap: 16px;
    margin-bottom: 16px;
    
    .icon-wrapper {
      width: 48px;
      height: 48px;
      border-radius: 12px;
      background: $primary-50;
      color: $primary-600;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
    }
    
    .header-text h3 {
      font-size: $font-size-lg;
      font-weight: 600;
      color: $slate-900;
      margin-bottom: 4px;
    }
    
    .header-text p {
      color: $slate-500;
      font-size: $font-size-sm;
    }
  }
  
  .section-card {
    border-radius: $radius-lg;
    border: 1px solid $slate-200;
    
    :deep(.el-card__body) {
      padding: 32px;
    }
  }
}

.full-width {
  width: 100%;
}

.w-full {
  width: 100%;
}

.action-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(12px);
  border-top: 1px solid $slate-200;
  padding: 16px 0;
  z-index: 100;
  
  .action-container {
    max-width: 960px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 24px;
  }
}

.status-hint {
  display: flex;
  align-items: center;
  gap: 8px;
  color: $slate-500;
  font-size: $font-size-sm;
  
  .pulse-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: $success;
    box-shadow: 0 0 0 0 rgba($success, 0.7);
    animation: pulse 2s infinite;
  }
}

@keyframes pulse {
  0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba($success, 0.7); }
  70% { transform: scale(1); box-shadow: 0 0 0 6px rgba($success, 0); }
  100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba($success, 0); }
}

.is-disabled-soft :deep(.el-input__wrapper) {
  background-color: $slate-50;
  box-shadow: none !important;
  border: 1px solid transparent;
}

.dynamic-group {
  margin-bottom: 12px;
  padding: 12px;
  background: $slate-50;
  border-radius: $radius-md;
}

.text-gray-400 { color: $slate-400; }
.text-gray-500 { color: $slate-500; }
.text-xs { font-size: $font-size-xs; }
</style>
