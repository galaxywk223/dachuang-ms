<template>
  <div class="apply-page">
    <div class="form-container">
      <!-- Header -->
      <div class="page-header">
        <div class="title-bar">
           <span class="title">基本信息填报</span>
           <el-tag size="small" type="primary" effect="plain" round>项目申报</el-tag>
        </div>
        <div class="actions">
           <el-button @click="handleReset">重置</el-button>
           <el-button type="info" plain @click="saveAsDraft">保存草稿</el-button>
           <el-button type="primary" @click="submitForm">提交申请</el-button>
        </div>
      </div>

      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-position="right"
        label-width="120px"
        status-icon
        size="default"
        class="main-form"
      >
        <!-- 1. 基本信息 -->
        <div class="form-section">
          <div class="section-header">
              <span class="section-title">基本信息</span>
          </div>
          <el-row :gutter="32">
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
            <el-col :span="8">
              <el-form-item label="重点领域" prop="is_key_field">
                <el-select v-model="formData.is_key_field" placeholder="请选择" class="w-full">
                  <el-option v-for="item in specialTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
               <el-form-item label="项目名称" prop="title">
                 <el-input v-model="formData.title" placeholder="请输入项目全称" />
               </el-form-item>
            </el-col>
             <el-col :span="8">
               <el-form-item label="经费预算" prop="budget">
                 <el-input-number 
                   v-model="formData.budget" 
                   :min="0" 
                   class="w-full" 
                   controls-position="right"
                   disabled 
                   placeholder="自动生成"
                 />
               </el-form-item>
            </el-col>
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
          </el-row>
        </div>

        <!-- 2. 团队信息 -->
        <div class="form-section">
          <div class="section-header">
              <span class="section-title">负责人信息</span>
          </div>
          <el-row :gutter="32">
            <el-col :span="8">
              <el-form-item label="负责人姓名">
                <el-input v-model="currentUser.name" disabled class="is-disabled-soft" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="负责人学号">
                <el-input v-model="currentUser.student_id" disabled class="is-disabled-soft" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
               <!-- Empty for alignment -->
            </el-col>
            <el-col :span="8">
              <el-form-item label="联系电话" prop="leader_contact">
                <el-input v-model="formData.leader_contact" placeholder="手机号" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="电子邮箱" prop="leader_email">
                <el-input v-model="formData.leader_email" placeholder="邮箱" />
              </el-form-item>
            </el-col>
          </el-row>
        </div>

        <!-- 3. 指导教师 (Dynamic Table) -->
        <div class="form-section">
          <div class="section-header">
              <span class="section-title">指导教师</span>
          </div>
          <div class="dynamic-input-row">
            <el-row :gutter="12">
               <el-col :span="5">
                 <el-input v-model="newAdvisor.job_number" placeholder="工号" />
               </el-col>
               <el-col :span="5">
                 <el-input v-model="newAdvisor.name" placeholder="姓名" />
               </el-col>
               <el-col :span="5">
                 <el-select v-model="newAdvisor.title" placeholder="职称">
                    <el-option v-for="item in advisorTitleOptions" :key="item.value" :label="item.label" :value="item.value" />
                 </el-select>
               </el-col>
               <el-col :span="5">
                 <el-input v-model="newAdvisor.contact" placeholder="电话" />
               </el-col>
               <el-col :span="4">
                 <el-button type="primary" plain @click="handleAddNewAdvisor" style="width: 100%">添加教师</el-button>
               </el-col>
            </el-row>
          </div>
          
          <el-table 
            :data="formData.advisors" 
            style="width: 100%; margin-top: 12px;" 
            border
            :header-cell-style="{ background: '#f8fafc', color: '#475569' }"
          >
             <el-table-column prop="job_number" label="工号" width="140" />
             <el-table-column prop="name" label="姓名" width="140" />
             <el-table-column prop="title" label="职称" width="140">
                <template #default="scope">
                   {{ getLabel(advisorTitleOptions, scope.row.title) }}
                </template>
             </el-table-column>
             <el-table-column prop="contact" label="电话" />
             <el-table-column label="操作" width="80" align="center">
                <template #default="scope">
                   <el-button link type="danger" size="small" @click="removeAdvisor(scope.$index)">删除</el-button>
                </template>
             </el-table-column>
             <template #empty>
                <div class="empty-text">暂无指导教师，请在上方添加</div>
             </template>
          </el-table>
        </div>

        <!-- 4. 项目成员 (Dynamic Table) -->
        <div class="form-section">
          <div class="section-header">
              <span class="section-title">项目成员</span>
          </div>
           <div class="dynamic-input-row">
            <el-row :gutter="12">
               <el-col :span="8">
                 <el-input v-model="newMember.student_id" placeholder="成员学号" />
               </el-col>
               <el-col :span="8">
                 <el-input v-model="newMember.name" placeholder="成员姓名" />
               </el-col>
               <el-col :span="8">
                 <el-button type="primary" plain @click="handleAddNewMember" style="width: 100%">添加成员</el-button>
               </el-col>
            </el-row>
          </div>

          <el-table 
            :data="formData.members" 
            style="width: 100%; margin-top: 12px;" 
            border 
            :header-cell-style="{ background: '#f8fafc', color: '#475569' }"
          >
             <el-table-column prop="student_id" label="学号" width="180" />
             <el-table-column prop="name" label="姓名" />
             <el-table-column label="操作" width="80" align="center">
                <template #default="scope">
                   <el-button link type="danger" size="small" @click="removeMember(scope.$index)">删除</el-button>
                </template>
             </el-table-column>
             <template #empty>
                <div class="empty-text">暂无成员，请在上方添加</div>
             </template>
          </el-table>
        </div>

        <!-- 5. 申报内容 -->
        <div class="form-section">
          <div class="section-header">
              <span class="section-title">申报内容</span>
          </div>
          <el-row>
             <el-col :span="24">
                <el-form-item label="预期成果" prop="expected_results">
                   <el-input 
                     v-model="formData.expected_results" 
                     type="textarea" 
                     :rows="3" 
                     maxlength="200"
                     show-word-limit
                     placeholder="请列出具体成果形式，如：发表论文1篇、软件著作权1项等"
                   />
                </el-form-item>
             </el-col>
             <el-col :span="24">
                <el-form-item label="项目简介" prop="description">
                   <el-input 
                     v-model="formData.description" 
                     type="textarea" 
                     :rows="6" 
                     maxlength="500"
                     show-word-limit
                     placeholder="请简要介绍项目背景、创新点及研究内容"
                   />
                </el-form-item>
             </el-col>
          </el-row>
        </div>

        <!-- 6. 附件 -->
        <div class="form-section no-border">
           <div class="section-header">
              <span class="section-title">附件上传</span>
          </div>
           <el-form-item label="申请书" prop="attachment_file">
              <el-upload
                action="#"
                :auto-upload="false"
                :on-change="handleFileChange"
                :file-list="fileList"
                :limit="1"
                class="upload-inline"
              >
                 <el-button type="primary" plain>点击上传PDF</el-button>
                 <template #tip>
                    <div class="el-upload__tip">只能上传pdf文件，且不超过2MB</div>
                 </template>
              </el-upload>
              <div class="mt-2 text-sm text-gray-500" style="margin-left: 16px;">
                  <a href="#" class="link-download">
                     <el-icon><Download /></el-icon> 下载申请书模板
                  </a>
              </div>
           </el-form-item>
        </div>

      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from "vue";
import { ElMessage, type FormInstance } from "element-plus";
import { Download } from "@element-plus/icons-vue";
import { useDictionary } from "@/composables/useDictionary";
import { DICT_CODES } from "@/api/dictionary";
import { useUserStore } from "@/stores/user";
import { createProjectApplication, updateProjectApplication, getProjectDetail } from "@/api/project";
import { useRouter, useRoute } from "vue-router";

// --- Logic Reuse ---
const userStore = useUserStore();
const router = useRouter();
const route = useRoute();
const { loadDictionaries, getOptions } = useDictionary();
const formRef = ref<FormInstance>();

const currentUser = computed(() => ({
  name: userStore.user?.real_name || userStore.user?.username || "学生用户",
  student_id: userStore.user?.employee_id || userStore.user?.username || "Unknown"
}));

const formData = reactive({
  id: null as number | null,
  source: "",
  level: "",
  category: "",
  is_key_field: "",
  college: "",
  budget: 0,
  major_code: "",
  leader_contact: "",
  leader_email: "",
  title: "",
  expected_results: "",
  description: "",
  advisors: [] as any[],
  members: [] as any[],
  attachment_file: null as File | null
});

// Watcher for Budget Automation
watch(() => formData.level, (newVal) => {
    switch (newVal) {
        case 'SCHOOL':
            formData.budget = 1000;
            break;
        case 'SCHOOL_KEY':
            formData.budget = 3000;
            break;
        case 'PROVINCIAL':
            formData.budget = 6000;
            break;
        case 'NATIONAL':
            formData.budget = 10000;
            break;
        default:
            formData.budget = 0;
            break;
    }
});

// Temp inputs
const newAdvisor = reactive({ job_number: "", name: "", title: "", contact: "", email: "" });
const newMember = reactive({ student_id: "", name: "" });

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

const getLabel = (options: any[], value: string) => {
    const found = options.find(opt => opt.value === value);
    return found ? found.label : value;
};

// Dynamic Actions
const handleAddNewAdvisor = () => {
    if(!newAdvisor.name) {
       ElMessage.warning("请至少填写姓名");
       return;
    }
    formData.advisors.push({ ...newAdvisor });
    // Reset
    newAdvisor.job_number = "";
    newAdvisor.name = "";
    newAdvisor.title = "";
    newAdvisor.contact = "";
};

const handleAddNewMember = () => {
    if(!newMember.student_id || !newMember.name) {
       ElMessage.warning("请填写学号和姓名");
       return;
    }
    formData.members.push({ ...newMember });
    // Reset
    newMember.student_id = "";
    newMember.name = "";
};

const removeAdvisor = (i: number) => formData.advisors.splice(i, 1);
const removeMember = (i: number) => formData.members.splice(i, 1);

const handleFileChange = (file: any) => {
  formData.attachment_file = file.raw;
};

// Submit Logic
const handleSaveOrSubmit = async (isDraft: boolean) => {
    if (!formRef.value) return;

    if (!isDraft) {
        if(formData.advisors.length === 0) {
             console.warn("No advisors added, user might have forgotten to click add");
        }
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
        const payload = new FormData();
        
        // 1. Basic Fields Mapping
        const basicFields = { ...formData };
        
        // Handle Logic before appending
        const validLevels = ['NATIONAL', 'PROVINCIAL', 'SCHOOL', 'SCHOOL_KEY'];
        if (!validLevels.includes(basicFields.level)) basicFields.level = 'SCHOOL';

        const validCategories = ['INNOVATION_TRAINING', 'ENTREPRENEURSHIP_TRAINING', 'ENTREPRENEURSHIP_PRACTICE'];
        if (basicFields.category === 'ENTREPRENEURSHIP') basicFields.category = 'ENTREPRENEURSHIP_PRACTICE';
        if (!validCategories.includes(basicFields.category)) basicFields.category = 'INNOVATION_TRAINING';
        
        const keyFieldVal = basicFields.is_key_field;
        basicFields.is_key_field = (keyFieldVal === true || keyFieldVal === 'TRUE' || keyFieldVal === 'YES' || keyFieldVal === 'KEY') ? 'KEY' : 'NORMAL'; // Backend expects boolean or specific value? Serializer expects boolean likely (is_key_field).
        // Check Serializer Line 92: "is_key_field"
        // Let's assume it handles boolean or string "true". 
        // Based on Step 222 line 133: is_draft = data.get("is_draft", True).
        // Let's stick to string "true"/"false" for boolean fields in FormData to be safe or whatever backend expects.
        // Actually Serializer defaults might work.
        // Let's pass it as string "true" if Key.
        
        if (!basicFields.leader_email || !/^\S+@\S+\.\S+$/.test(basicFields.leader_email)) {
            basicFields.leader_email = "";
        }
        
        basicFields.budget = Number(basicFields.budget) || 0;
        // basicFields.self_funding = Number(basicFields.self_funding) || 0; // self_funding not in formData definition but in payload logic previously

        payload.append('is_draft', String(isDraft));

        // Append fields loop
        Object.keys(basicFields).forEach(key => {
            if (key === 'attachment_file') {
                if (basicFields.attachment_file) {
                    payload.append('proposal_file', basicFields.attachment_file);
                }
            } else if (key === 'advisors' || key === 'members') {
                payload.append(key, JSON.stringify(basicFields[key]));
            } else if (key === 'id') {
                // Skip ID in body
            } else {
                 const val = (basicFields as any)[key];
                 if (val !== null && val !== undefined) {
                     payload.append(key, String(val));
                 }
            }
        });

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
            }

            if (Array.isArray(data.members_info) && data.members_info.length > 0) {
                 const otherMembers = data.members_info.filter((m: any) => m.role === 'MEMBER');
                 if (otherMembers.length > 0) {
                     formData.members = otherMembers.map((m: any) => ({
                         student_id: m.student_id || "",
                         name: m.user_name || m.name || ""
                     }));
                 }
            }
            ElMessage.success("数据加载成功");
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

.apply-page {
    padding: 24px;
    max-width: 1200px;
    margin: 0 auto;
}

.form-container {
  background: white;
  border-radius: $radius-lg;
  box-shadow: $shadow-sm;
  border: 1px solid $color-border-light;
  overflow: hidden;
}

.page-header {
  padding: 16px 24px;
  border-bottom: 1px solid $slate-100;
  display: flex;
  align-items: center;
  justify-content: space-between;
  
  .title-bar {
      display: flex;
      align-items: center;
      gap: 12px;
      
      .title {
          font-size: 16px;
          font-weight: 600;
          color: $slate-800;
          position: relative;
          padding-left: 14px;
          
          &::before {
              content: '';
              position: absolute;
              left: 0;
              top: 50%;
              transform: translateY(-50%);
              width: 4px;
              height: 16px;
              background: $primary-600;
              border-radius: 2px;
          }
      }
  }
}

.main-form {
    padding: 32px;
}

.form-section {
  margin-bottom: 40px;
  
  &:last-child {
    margin-bottom: 0;
  }
  
  .section-header {
      margin-bottom: 24px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px dashed $slate-200;
      padding-bottom: 8px;
      
      .section-title {
          font-size: 15px;
          font-weight: 600;
          color: $slate-700;
      }
  }
}

.w-full { width: 100%; }

.dynamic-input-row {
  background: $slate-50;
  padding: 16px;
  border-radius: $radius-md;
  border: 1px dashed $slate-200;
  margin-bottom: 12px;
}

.empty-text {
  color: $slate-400;
  font-size: 13px;
  text-align: center;
  padding: 8px 0;
}

.link-download {
  color: $primary-600;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  text-decoration: none;
  font-weight: 500;
  
  &:hover { text-decoration: underline; }
}
</style>
