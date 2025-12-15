<template>
  <div class="apply-page-wrapper">
    <div class="apply-main-container">
      <!-- Main Single Card -->
      <div class="apply-card">
        <!-- Header Section -->
        <div class="form-header">
          <div class="header-main">
            <h1 class="page-title">项目申报</h1>
            <div class="header-meta">
              <span class="meta-item">负责人: {{ currentUser.name }}</span>
              <span class="meta-divider">|</span>
              <el-tag type="success" size="small" effect="plain" round>填写中</el-tag>
            </div>
          </div>
          <p class="header-desc">
            请基于事实准确填写以下申报信息。带 * 的条目为必填项。
          </p>
        </div>

        <el-divider class="header-divider" />

        <!-- Form Section -->
        <el-form
          ref="formRef"
          :model="formData"
          :rules="rules"
          label-position="top"
          class="clean-form"
          status-icon
          hide-required-asterisk
          size="large"
        >
          
          <!-- 1. Basic Information -->
          <div class="form-section">
            <h3 class="section-title">基本信息</h3>
            <el-row :gutter="40">
              <el-col :span="8">
                <el-form-item label="项目来源" prop="source">
                  <el-select v-model="formData.source" placeholder="请选择" class="w-full">
                    <el-option v-for="item in sourceOptions" :key="item.value" :label="item.label" :value="item.value" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="项目级别" prop="level">
                  <el-select v-model="formData.level" placeholder="请选择" class="w-full">
                    <el-option v-for="item in levelOptions" :key="item.value" :label="item.label" :value="item.value" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :span="8">
                <el-form-item label="项目类别" prop="category">
                  <el-select v-model="formData.category" placeholder="请选择" class="w-full">
                    <el-option v-for="item in categoryOptions" :key="item.value" :label="item.label" :value="item.value" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="40">
              <el-col :span="12">
                 <el-form-item prop="is_key_field" label="重点领域项目">
                    <el-select v-model="formData.is_key_field" placeholder="请选择" class="w-full">
                      <el-option v-for="item in specialTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
                    </el-select>
                 </el-form-item>
              </el-col>
               <el-col :span="12">
                <!-- Placeholder for symmetry or next field -->
              </el-col>
            </el-row>
          </div>

          <!-- 2. Project Details -->
          <div class="form-section">
            <h3 class="section-title">项目详情</h3>
             <el-form-item label="项目名称" prop="title">
                <el-input v-model="formData.title" placeholder="请输入准确的项目全称" />
             </el-form-item>
             
             <el-row :gutter="40">
               <el-col :span="8">
                 <el-form-item label="所属学院" prop="college">
                    <el-select v-model="formData.college" placeholder="请选择" class="w-full">
                       <el-option v-for="item in collegeOptions" :key="item.value" :label="item.label" :value="item.value" />
                    </el-select>
                 </el-form-item>
               </el-col>
               <el-col :span="8">
                 <el-form-item label="所属专业" prop="major_code">
                    <el-select v-model="formData.major_code" placeholder="请选择" class="w-full" filterable>
                       <el-option v-for="item in majorOptions" :key="item.value" :label="item.label" :value="item.value" />
                    </el-select>
                 </el-form-item>
               </el-col>
               <el-col :span="8">
                  <el-form-item label="经费预算 (元)" prop="budget">
                    <el-input-number v-model="formData.budget" :min="0" :step="100" class="w-full" controls-position="right" />
                  </el-form-item>
               </el-col>
             </el-row>
          </div>

          <!-- 3. Team Construction -->
          <div class="form-section">
            <h3 class="section-title">团队组建</h3>
            <!-- Leader Info -->
            <div class="subsection-label">负责人信息</div>
            <el-row :gutter="40">
              <el-col :span="6">
                <el-form-item label="姓名">
                  <el-input v-model="currentUser.name" disabled class="is-readonly" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="学号">
                  <el-input v-model="currentUser.student_id" disabled class="is-readonly" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="联系电话" prop="leader_contact">
                  <el-input v-model="formData.leader_contact" placeholder="填写手机号" />
                </el-form-item>
              </el-col>
              <el-col :span="6">
                <el-form-item label="电子邮箱" prop="leader_email">
                  <el-input v-model="formData.leader_email" placeholder="填写邮箱" />
                </el-form-item>
              </el-col>
            </el-row>

            <!-- Advisors -->
            <div class="dynamic-section">
              <div class="flex items-center justify-between mb-2">
                 <div class="subsection-label mb-0">指导教师</div>
              </div>
              
              <div v-for="(advisor, index) in formData.advisors" :key="'adv'+index" class="grid-row-group">
                <el-row :gutter="20">
                   <el-col :span="5">
                     <el-input v-model="advisor.job_number" placeholder="工号" />
                   </el-col>
                   <el-col :span="5">
                     <el-input v-model="advisor.name" placeholder="姓名" />
                   </el-col>
                   <el-col :span="5">
                     <el-select v-model="advisor.title" placeholder="职称">
                        <el-option v-for="item in advisorTitleOptions" :key="item.value" :label="item.label" :value="item.value" />
                     </el-select>
                   </el-col>
                    <el-col :span="5">
                     <el-input v-model="advisor.contact" placeholder="电话" />
                   </el-col>
                   <el-col :span="4" class="row-actions">
                      <el-button type="primary" link @click="addAdvisor" v-if="index === formData.advisors.length - 1">添加</el-button>
                      <el-button type="danger" link @click="removeAdvisor(index)" v-if="formData.advisors.length > 1">删除</el-button>
                   </el-col>
                </el-row>
              </div>
            </div>

            <!-- Members -->
            <div class="dynamic-section mt-6">
               <div class="subsection-label">项目成员</div>
               <div v-for="(member, index) in formData.members" :key="'mem'+index" class="grid-row-group">
                 <el-row :gutter="20">
                   <el-col :span="10">
                     <el-input v-model="member.student_id" placeholder="成员学号" />
                   </el-col>
                   <el-col :span="10">
                     <el-input v-model="member.name" placeholder="成员姓名" />
                   </el-col>
                   <el-col :span="4" class="row-actions">
                      <el-button type="primary" link @click="addMember" v-if="index === formData.members.length - 1">添加</el-button>
                      <el-button type="danger" link @click="removeMember(index)" v-if="formData.members.length > 1">删除</el-button>
                   </el-col>
                 </el-row>
               </div>
            </div>
          </div>

          <!-- 4. Declaration Content -->
          <div class="form-section">
            <h3 class="section-title">申报内容</h3>
            <el-form-item label="预期成果" prop="expected_results">
               <el-input 
                 v-model="formData.expected_results" 
                 type="textarea" 
                 :rows="3" 
                 placeholder="请简述项目的预期成果，如调研报告、发表论文等"
                 maxlength="200"
                 show-word-limit
               />
            </el-form-item>
            <el-form-item label="项目简介" prop="description">
               <el-input 
                 v-model="formData.description" 
                 type="textarea" 
                 :rows="6" 
                 placeholder="请简要介绍项目背景、研究内容及意义..."
                 maxlength="500"
                 show-word-limit
               />
            </el-form-item>
          </div>

          <!-- 5. Attachments -->
          <div class="form-section no-border">
             <h3 class="section-title">附件上传</h3>
             <div class="attachment-area">
                <el-form-item prop="attachment_file">
                  <el-upload
                    action="#"
                    :auto-upload="false"
                    :on-change="handleFileChange"
                    :file-list="fileList"
                    drag
                    class="upload-demo"
                  >
                    <div class="upload-content">
                        <el-icon class="upload-icon"><UploadFilled /></el-icon>
                        <div class="upload-text">
                           <strong>点击或拖拽文件到这里上传</strong>
                           <p>支持 PDF 格式，文件大小不超过 2MB</p>
                        </div>
                    </div>
                  </el-upload>
                </el-form-item>
                <div class="mt-4">
                  <el-button link type="primary" :icon="Download">下载《大创项目申请书模板》</el-button>
                </div>
             </div>
          </div>

        </el-form>
      </div>
    </div>

    <!-- Sticky Footer -->
    <div class="sticky-footer">
       <div class="footer-content">
          <div class="footer-left">
             <!-- Placeholder for draft status or validation hints -->
          </div>
          <div class="footer-actions">
             <el-button @click="handleReset" link class="secondary-link">重置</el-button>
             <el-button type="info" plain @click="saveAsDraft" class="btn-draft">保存草稿</el-button>
             <el-button type="primary" @click="submitForm" class="btn-submit">提交申请</el-button>
          </div>
       </div>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from "vue";
import { ElMessage, type FormInstance } from "element-plus";
import { UploadFilled, Download } from "@element-plus/icons-vue";
import { useDictionary } from "@/composables/useDictionary";
import { DICT_CODES } from "@/api/dictionary";
import { useUserStore } from "@/stores/user";
import { createProjectApplication, updateProjectApplication, getProjectDetail } from "@/api/project";
import { useRouter, useRoute } from "vue-router";

// --- Logic Reuse (Identical to original mainly) ---
const userStore = useUserStore();
const router = useRouter();
const route = useRoute();
const { loadDictionaries, getOptions } = useDictionary();
const formRef = ref<FormInstance>();

const currentUser = computed(() => ({
  name: userStore.user?.real_name || "学生用户",
  student_id: userStore.user?.username || "Unknown"
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

    if (!isDraft) {
        await formRef.value.validate(async (valid) => {
            if (!valid) {
                 ElMessage.error("请完善必填信息");
                 return;
            }
            await processRequest(false);
        });
    } else {
        await processRequest(true);
    }
};

const processRequest = async (isDraft: boolean) => {
    if (!formData.title && isDraft) {
        ElMessage.warning("请填写项目名称（草稿必填）");
        return;
    }

    loading.value = true;
    try {
        const payload: any = { 
            ...formData, 
            is_draft: isDraft 
        };

        const validLevels = ['NATIONAL', 'PROVINCIAL', 'SCHOOL'];
        if (payload.level === 'SCHOOL_KEY') payload.level = 'SCHOOL';
        if (!validLevels.includes(payload.level)) payload.level = 'SCHOOL';

        const validCategories = ['INNOVATION_TRAINING', 'ENTREPRENEURSHIP_TRAINING', 'ENTREPRENEURSHIP_PRACTICE'];
        if (payload.category === 'ENTREPRENEURSHIP') payload.category = 'ENTREPRENEURSHIP_PRACTICE';
        if (!validCategories.includes(payload.category)) payload.category = 'INNOVATION_TRAINING';
        
        const keyFieldVal = payload.is_key_field;
        payload.is_key_field = (keyFieldVal === true || keyFieldVal === 'TRUE' || keyFieldVal === 'YES' || keyFieldVal === 'KEY');

        delete payload.attachment_file; 
        
        if (!payload.leader_email || !/^\S+@\S+\.\S+$/.test(payload.leader_email)) {
            payload.leader_email = "";
        }
        
        payload.budget = Number(payload.budget) || 0;
        payload.self_funding = Number(payload.self_funding) || 0;

        let response: any;
        if (formData.id) {
            response = await updateProjectApplication(formData.id, payload);
        } else {
            response = await createProjectApplication(payload);
        }
        
        if (response.code === 200 || response.status === 201) {
            ElMessage.success(isDraft ? "草稿已保存" : "申请已提交");
            if (!isDraft) {
                router.push('/establishment/my-projects');
            } else {
                if (response.data && response.data.id) {
                    formData.id = response.data.id;
                     router.replace({ 
                        path: route.path,
                        query: { ...route.query, id: String(response.data.id) } 
                    });
                }
            }
        } else {
            let errorMsg = response.message || "操作失败";
            if (response.errors) {
                 const details = Object.entries(response.errors)
                    .map(([k, v]) => `${k}: ${v}`)
                    .join('; ');
                 errorMsg += ` (${details})`;
            }
            ElMessage.error(errorMsg);
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
    loading.value = true;
    try {
        const res: any = await getProjectDetail(id);
        const projectData = res.data || res;
        
        if (projectData && (projectData.id || res.code === 200)) {
            const data = projectData.id ? projectData : projectData.data;
            if (!data) throw new Error("No data found");

            formData.id = data.id;
            formData.title = data.title || "";
            formData.source = data.source || ""; 
            formData.level = data.level || "SCHOOL"; 
            formData.category = data.category || "INNOVATION_TRAINING"; 
            formData.college = data.college || "";
            formData.major_code = data.major_code || "";
            formData.budget = Number(data.budget || 0);
            formData.leader_contact = data.leader_contact || "";
            formData.leader_email = data.leader_email || "";
            formData.description = data.description || "";
            formData.expected_results = data.expected_results || "";
            
            if (typeof data.is_key_field === 'boolean') {
                 formData.is_key_field = data.is_key_field ? 'KEY' : 'NORMAL';
            } else {
                 formData.is_key_field = data.is_key_field || 'NORMAL';
            }

            if (Array.isArray(data.advisors_info) && data.advisors_info.length > 0) {
                formData.advisors = data.advisors_info.map((adh: any) => ({
                    job_number: "", 
                    name: adh.name || "",
                    title: adh.title || "",
                    contact: adh.contact || "",
                    email: adh.email || ""
                }));
            } else {
                formData.advisors = [{ job_number: "", name: "", title: "", contact: "", email: "" }];
            }

            if (Array.isArray(data.members_info) && data.members_info.length > 0) {
                 const otherMembers = data.members_info.filter((m: any) => m.role === 'MEMBER');
                 if (otherMembers.length > 0) {
                     formData.members = otherMembers.map((m: any) => ({
                         student_id: m.student_id || "",
                         name: m.user_name || m.name || ""
                     }));
                 } else {
                     formData.members = [{ student_id: "", name: "" }];
                 }
            } else {
                 formData.members = [{ student_id: "", name: "" }];
            }
            ElMessage.success("项目数据加载成功");
        }
    } catch(e: any) {
        ElMessage.error("加载详情失败");
    } finally {
        loading.value = false;
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

.apply-page-wrapper {
  background-color: $slate-50; /* Very light cool gray */
  min-height: 100vh;
  padding-bottom: 80px; /* Space for sticky footer */
}

.apply-main-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 32px 20px;
}

.apply-card {
  background: $color-bg-card;
  border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px -1px rgba(0, 0, 0, 0.02); /* Very subtle diffusion */
  padding: 48px; /* Generous padding */
}

.form-header {
  margin-bottom: 24px;
}

.header-main {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 12px;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: $slate-800;
  margin: 0;
  letter-spacing: -0.5px;
}

.header-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  background: $slate-100;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 13px;
  color: $slate-500;
}

.meta-divider {
  color: $slate-300;
  font-size: 12px;
}

.header-desc {
  font-size: 14px;
  color: $slate-400;
  margin: 0;
}

.header-divider {
  margin: 32px 0 40px 0;
  border-color: $slate-100;
}

.form-section {
  margin-bottom: 48px;
  border-bottom: 1px dashed $slate-100;
  padding-bottom: 40px;

  &:last-child, &.no-border {
    border-bottom: none;
    margin-bottom: 0;
    padding-bottom: 0;
  }
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: $slate-900;
  margin: 0 0 24px 0;
  display: flex;
  align-items: center;
  
  /* Decorative accent */
  &::before {
     content: '';
     display: block;
     width: 4px;
     height: 18px;
     background: $primary-500;
     margin-right: 12px;
     border-radius: 2px;
  }
}

.subsection-label {
  font-size: 14px;
  font-weight: 500;
  color: $slate-500; /* Slate 500 */
  margin-bottom: 16px;
}

/* Grid & Form Fixes */
.w-full { width: 100%; }

.el-row {
  margin-bottom: 8px; /* Slight gutter between rows */
}

:deep(.el-form-item__label) {
  font-weight: 500;
  color: $slate-600;
  padding-bottom: 8px;
  line-height: 1.3;
}

.is-readonly :deep(.el-input__wrapper) {
   background-color: $slate-50;
   box-shadow: none !important;
   border: 1px solid $slate-200;
}

/* Dynamic Sections */
.grid-row-group {
  margin-bottom: 12px;
  
  :deep(.el-input__wrapper), :deep(.el-select__wrapper) {
    box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05); /* Slight elevation for inputs */
  }
}

.row-actions {
  display: flex;
  align-items: center;
}

/* Attachment Area */
.attachment-area {
  background: $slate-50;
  border-radius: 12px;
  border: 1px dashed $slate-300;
  padding: 32px;
  text-align: center;
  transition: all 0.3s;

  &:hover {
    border-color: $primary-400;
    background: #f0f9ff;
  }
}

.upload-demo {
  :deep(.el-upload-dragger) {
    border: none;
    background: transparent;
    padding: 0;
    height: auto;
    
    &:hover { border: none; background: transparent; }
  }
}

.upload-icon {
  font-size: 40px;
  color: $slate-400;
  margin-bottom: 12px;
}

.upload-text strong {
  color: #475569;
  font-size: 15px;
}

.upload-text p {
  color: $slate-400;
  font-size: 13px;
  margin-top: 4px;
}

/* Sticky Footer */
.sticky-footer {
  position: fixed;
  bottom: 0;
  left: 0; /* Adjust if sidebar pushes this */
  right: 0;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-top: 1px solid $slate-200;
  z-index: 100;
  padding: 16px 0;
  box-shadow: 0 -4px 20px rgba(0,0,0,0.02);
}

.footer-content {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  justify-content: flex-end; /* Align right */
  align-items: center;
}

.footer-actions {
  display: flex;
  gap: 16px;
  align-items: center;
}

.secondary-link {
  color: $slate-500;
  &:hover { color: #334155; }
}

.btn-draft {
  min-width: 100px;
}

.btn-submit {
  min-width: 120px;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3); /* Premium shadow */
}
</style>
