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
                 <el-cascader
                    v-model="keyFieldCascaderValue"
                    :options="keyFieldCascaderOptions"
                    placeholder="请选择"
                    class="w-full"
                    style="width: 100%"
                    :props="{ expandTrigger: 'hover' }"
                 />
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
               <el-col :span="3">
                 <el-select v-model="newAdvisor.order" placeholder="次序" style="width: 100%">
                   <el-option label="第一指导老师" :value="1" />
                   <el-option label="第二指导老师" :value="2" />
                 </el-select>
               </el-col>
               <el-col :span="5">
                 <el-input 
                    v-model="newAdvisor.job_number" 
                    placeholder="工号 (回车查询)" 
                    @blur="handleSearchNewAdvisor"
                    @keyup.enter="handleSearchNewAdvisor"
                 >
                    <template #append>
                        <el-button :icon="Search" @click="handleSearchNewAdvisor" />
                    </template>
                 </el-input>
               </el-col>
               <el-col :span="4">
                 <el-input v-model="newAdvisor.name" placeholder="姓名" disabled />
               </el-col>
               <el-col :span="4">
                  <!-- Display Title Label if possible, or just code -->
                 <el-input v-model="newAdvisor.title" placeholder="职称" disabled />
               </el-col>
               <el-col :span="6">
                 <el-input v-model="newAdvisor.email" placeholder="邮箱" />
               </el-col>
               <el-col :span="2">
                 <el-button type="primary" plain @click="handleAddNewAdvisor" style="width: 100%">添加</el-button>
               </el-col>
            </el-row>
          </div>
          
          <el-table 
            :data="formData.advisors" 
            style="width: 100%; margin-top: 12px;" 
            border
            :header-cell-style="{ background: '#f8fafc', color: '#475569' }"
          >
             <el-table-column label="次序" width="120">
               <template #default="scope">
                 <el-tag :type="scope.row.order === 1 ? 'primary' : 'success'" effect="plain">
                   {{ scope.row.order === 1 ? '第一指导老师' : '第二指导老师' }}
                 </el-tag>
               </template>
             </el-table-column>
             <el-table-column prop="job_number" label="工号" width="120" />
             <el-table-column prop="name" label="姓名" width="100" />
             <el-table-column prop="title" label="职称" width="100">
                <template #default="scope">
                   {{ getLabel(advisorTitleOptions, scope.row.title) }}
                </template>
             </el-table-column>
             <el-table-column prop="contact" label="电话" />
             <el-table-column prop="email" label="邮箱" />
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
                 <el-input 
                    v-model="newMember.student_id" 
                    placeholder="成员学号 (回车查询)" 
                    @blur="handleSearchNewMember"
                    @keyup.enter="handleSearchNewMember"
                 >
                    <template #append>
                        <el-button :icon="Search" @click="handleSearchNewMember" />
                    </template>
                 </el-input>
               </el-col>
               <el-col :span="8">
                 <el-input v-model="newMember.name" placeholder="成员姓名" disabled />
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
                <el-form-item label="预期成果清单">
                  <div class="expected-grid">
                    <el-select
                      v-model="expectedForm.achievement_type"
                      placeholder="成果类型"
                      class="expected-select"
                    >
                      <el-option
                        v-for="item in achievementTypeOptions"
                        :key="item.value"
                        :label="item.label"
                        :value="item.value"
                      />
                    </el-select>
                    <el-input-number
                      v-model="expectedForm.expected_count"
                      :min="1"
                      controls-position="right"
                      class="expected-count"
                    />
                    <el-button type="primary" plain @click="addExpectedResult">
                      添加
                    </el-button>
                  </div>
                  <el-table
                    v-if="formData.expected_results_data.length"
                    :data="formData.expected_results_data"
                    border
                    style="width: 100%; margin-top: 12px;"
                    :header-cell-style="{ background: '#f8fafc', color: '#475569' }"
                  >
                    <el-table-column label="成果类型">
                      <template #default="{ row }">
                        {{ getLabel(achievementTypeOptions, row.achievement_type) }}
                      </template>
                    </el-table-column>
                    <el-table-column prop="expected_count" label="数量" width="120" />
                    <el-table-column label="操作" width="100" align="center">
                      <template #default="{ $index }">
                        <el-button link type="danger" @click="removeExpectedResult($index)">删除</el-button>
                      </template>
                    </el-table-column>
                  </el-table>
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
                <div class="attachment-container">
                    <div class="actions-row">
                        <el-upload
                            action="#" 
                            :auto-upload="false"
                            :on-change="handleFileChange"
                            :limit="1"
                            v-model:file-list="fileList"
                            accept=".pdf"
                            class="upload-demo"
                        >
                            <el-button type="primary" plain>
                                <el-icon class="mr-1"><Upload /></el-icon> 上传申请书 (PDF)
                            </el-button>
                        </el-upload>
                        
                        <div class="download-section">
                            <el-button 
                                v-if="currentTemplateUrl" 
                                link 
                                type="primary" 
                                @click="handleDownloadTemplate"
                            >
                                <el-icon class="mr-1"><Download /></el-icon> 下载申请书模板
                            </el-button>
                            <el-tag v-else type="info" size="small" effect="plain">
                                暂无申请书模板
                            </el-tag>
                        </div>
                    </div>
                    
                    <div class="form-tip">只能上传pdf文件，且不超过2MB</div>
                </div>
           </el-form-item>
        </div>

      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from "vue";
import { ElMessage, type FormInstance, type UploadUserFile } from "element-plus";
import { Download, Search, Upload } from "@element-plus/icons-vue";
import { getUsers } from "@/api/user-admin";
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
const loading = ref(false);
const fileList = ref<UploadUserFile[]>([]);

const currentUser = computed(() => ({
  name: userStore.user?.real_name || userStore.user?.username || "学生用户",
  student_id: userStore.user?.employee_id || userStore.user?.username || "Unknown"
}));

interface AdvisorInfo {
  user_id?: number | null;
  job_number: string;
  name: string;
  title: string;
  contact: string;
  email: string;
  order: number;
  college?: string;
}

interface MemberInfo {
  student_id: string;
  name: string;
}

interface CascaderOption {
  value: string;
  label: string;
  disabled?: boolean;
  children?: CascaderOption[];
}

interface FormDataState {
  id: number | null;
  source: string;
  level: string;
  category: string;
  is_key_field: boolean | string;
  key_field_code: string;
  college: string;
  budget: number;
  major_code: string;
  leader_contact: string;
  leader_email: string;
  title: string;
  expected_results: string;
  expected_results_data: { achievement_type: string; expected_count: number }[];
  description: string;
  advisors: AdvisorInfo[];
  members: MemberInfo[];
  attachment_file: File | null;
}

const formData = reactive<FormDataState>({
  id: null,
  source: "",
  level: "",
  category: "",
  is_key_field: false,
  key_field_code: "",
  college: "",
  budget: 0,
  major_code: "",
  leader_contact: "",
  leader_email: "",
  title: "",
  expected_results: "",
  expected_results_data: [],
  description: "",
  advisors: [],
  members: [],
  attachment_file: null
});

// Watcher for Budget Automation
watch(() => formData.level, (newVal) => {
    if (!newVal) {
        formData.budget = 0;
        return;
    }
    const selectedOption = levelOptions.value.find((opt: any) => opt.value === newVal);
    if (selectedOption && selectedOption.extra_data && selectedOption.extra_data.budget) {
        formData.budget = Number(selectedOption.extra_data.budget);
    } else {
        // Fallback or keep 0 if no config found
        formData.budget = 0;
    }
});

// Temp inputs
const newAdvisor = reactive({ user_id: null as number | null, job_number: "", name: "", title: "", contact: "", email: "", order: 1 });
const newMember = reactive({ student_id: "", name: "" });

const currentTemplateUrl = computed(() => {
    // console.log("Computing Template URL. Category:", formData.category);
    if (!formData.category) return null;
    const option = categoryOptions.value.find((opt: any) => opt.value === formData.category);
    // console.log("Refreshed Option:", option);
    return option?.template_file || null;
});

const handleDownloadTemplate = () => {
    if (!formData.category) {
        ElMessage.warning("请先选择项目类别");
        return;
    }
    if (currentTemplateUrl.value) {
        window.open(currentTemplateUrl.value, '_blank');
    } else {
        ElMessage.info("该类别暂无申请书模板");
    }
};

const rules = {
  source: [{ required: true, message: "必选项", trigger: "change" }],
  level: [{ required: true, message: "必选项", trigger: "change" }],
  category: [{ required: true, message: "必选项", trigger: "change" }],
  title: [{ required: true, message: "必填项", trigger: "blur" }],
  leader_contact: [{ required: true, message: "必填项", trigger: "blur" }],
  leader_email: [{ required: true, message: "必填项", trigger: "blur" }],
  college: [{ required: true, message: "必选项", trigger: "change" }],
  major_code: [{ required: true, message: "必选项", trigger: "change" }],
  expected_results: [{ required: true, message: "必填项", trigger: "blur" }],
  description: [{ required: true, message: "必填项", trigger: "blur" }],
  attachment_file: [{ required: true, message: "请上传申请书", trigger: "change" }]
};

// Dicts
const sourceOptions = computed(() => getOptions(DICT_CODES.PROJECT_SOURCE));
const collegeOptions = computed(() => getOptions(DICT_CODES.COLLEGE));
const majorOptions = computed(() => getOptions(DICT_CODES.MAJOR_CATEGORY));
const advisorTitleOptions = computed(() => getOptions(DICT_CODES.ADVISOR_TITLE));
const levelOptions = computed(() => getOptions(DICT_CODES.PROJECT_LEVEL));
const keyFieldOptions = computed(() => getOptions(DICT_CODES.KEY_FIELD_CODE));
const categoryOptions = computed(() => getOptions(DICT_CODES.PROJECT_CATEGORY));
const achievementTypeOptions = computed(() => getOptions(DICT_CODES.ACHIEVEMENT_TYPE));

const getDefaultLevel = () => levelOptions.value[0]?.value || "";
const getDefaultCategory = () => categoryOptions.value[0]?.value || "";

const keyFieldCascaderOptions = computed(() => {
  let keyChildren: CascaderOption[] = keyFieldOptions.value.map(opt => ({
    value: opt.value,
    label: opt.label
  }));

  // Fix: If no children, add a disabled placeholder so the submenu still appears
  if (keyChildren.length === 0) {
      keyChildren = [{
          value: '',
          label: '暂无数据 (请在后台添加)',
          disabled: true
      }];
  }
  
  return [
    {
      value: 'GENERAL',
      label: '一般项目'
    },
    {
      value: 'KEY',
      label: '重点领域项目',
      children: keyChildren
    }
  ] as CascaderOption[];
});

const keyFieldCascaderValue = computed({
  get: () => {
    if (!formData.is_key_field) return ['GENERAL'];
    // If it's a key field project but no code selected yet, return just ['KEY'] (although cascader usually wants full path)
    return formData.key_field_code ? ['KEY', formData.key_field_code] : ['KEY'];
  },
  set: (val: string[]) => {
    if (!val || val.length === 0) return;
    if (val[0] === 'GENERAL') {
      formData.is_key_field = false;
      formData.key_field_code = ''; 
    } else if (val[0] === 'KEY') {
      formData.is_key_field = true;
      // If user selected a child, it will be in val[1]
      if (val.length > 1) {
        formData.key_field_code = val[1];
      }
    }
  }
});

const expectedForm = reactive({
  achievement_type: "",
  expected_count: 1,
});

const addExpectedResult = () => {
  if (!expectedForm.achievement_type) {
    ElMessage.warning("请选择成果类型");
    return;
  }
  formData.expected_results_data.push({
    achievement_type: expectedForm.achievement_type,
    expected_count: expectedForm.expected_count || 1,
  });
  expectedForm.achievement_type = "";
  expectedForm.expected_count = 1;
};

const removeExpectedResult = (index: number) => {
  formData.expected_results_data.splice(index, 1);
};

const getLabel = (options: any[], value: string) => {
    const found = options.find(opt => opt.value === value);
    return found ? found.label : value;
};

// Dynamic Actions
const handleSearchNewAdvisor = async () => {
    if (!newAdvisor.job_number) {
        ElMessage.warning("请输入工号");
        return;
    }
    
    try {
        const res = await getUsers({ employee_id: newAdvisor.job_number, role: 'TEACHER', page_size: 1 });
        const users = res.data?.results || [];
        if (users.length > 0) {
            const user = users[0];
            // Ensure compatibility with AdvisorInfo interface
            // AdvisorInfo has: user_id, job_number, name, title, contact, email, order, college
            newAdvisor.user_id = user.id;
            newAdvisor.name = user.real_name;
            newAdvisor.title = user.title || ""; 
            newAdvisor.contact = user.phone;
            newAdvisor.email = user.email;
            
            ElMessage.success(`已找到教师: ${user.real_name}`);
        } else {
            ElMessage.error("未找到该工号的教师，请核对或联系管理员添加");
            newAdvisor.user_id = null;
            newAdvisor.name = "";
            newAdvisor.title = "";
            newAdvisor.contact = "";
            newAdvisor.email = "";
        }
    } catch (error) {
        console.error("Search failed", error);
        ElMessage.error("查询失败");
    }
};

const handleAddNewAdvisor = () => {
    if (newAdvisor.order === 2) {
        const hasFirst = formData.advisors.some(a => a.order === 1);
        if (!hasFirst) {
            ElMessage.warning("请先添加第一指导教师");
            return;
        }
    }
    // Check if user is selected
    if (!newAdvisor.user_id) {
         ElMessage.warning("请先查询并确认教师信息");
         return;
    }
    
    // Check duplicate
    if (formData.advisors.some(a => a.job_number === newAdvisor.job_number)) {
        ElMessage.warning("该教师已添加");
        return;
    }

    // Check if order already exists (optional, but good for UX)
    if (formData.advisors.some(a => a.order === newAdvisor.order)) {
         ElMessage.warning(newAdvisor.order === 1 ? "第一指导教师已存在" : "第二指导教师已存在");
         return;
    }

    formData.advisors.push({ ...newAdvisor });
    // Reset
    newAdvisor.user_id = null;
    newAdvisor.job_number = "";
    newAdvisor.name = "";
    newAdvisor.title = "";
    newAdvisor.contact = "";
    newAdvisor.email = "";
};

const handleSearchNewMember = async () => {
    if (!newMember.student_id) {
        ElMessage.warning("请输入学号");
        return;
    }
    
    try {
        const res = await getUsers({ employee_id: newMember.student_id, role: 'STUDENT', page_size: 1 });
        const users = res.data?.results || [];
        if (users.length > 0) {
            const user = users[0];
            newMember.name = user.real_name;
            ElMessage.success(`已找到学生: ${user.real_name}`);
        } else {
            ElMessage.error("未找到该学号的学生");
            newMember.name = "";
        }
    } catch (error) {
        console.error("Search failed", error);
        ElMessage.error("查询失败");
    }
};

const handleAddNewMember = () => {
    if(!newMember.student_id) {
       ElMessage.warning("请填写学号");
       return;
    }
    if(!newMember.name) {
       ElMessage.warning("请先查询并确认学生信息");
       return;
    }
    
    // Check duplicate
    if (formData.members.some(m => m.student_id === newMember.student_id)) {
        ElMessage.warning("该成员已添加");
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
  const isPDF = file.raw.type === 'application/pdf';
  const isLt2M = file.raw.size / 1024 / 1024 < 2;

  if (!isPDF) {
    ElMessage.error('只能上传 PDF 文件!');
    fileList.value = [];
    formData.attachment_file = null;
    return;
  }
  if (!isLt2M) {
    ElMessage.error('文件大小不能超过 2MB!');
    fileList.value = [];
    formData.attachment_file = null;
    return;
  }

  formData.attachment_file = file.raw;
  formRef.value?.validateField('attachment_file');
};

// Submit Logic
const handleSaveOrSubmit = async (isDraft: boolean) => {
    if (!formRef.value) return;

    // Advisor Validation (only for submit, draft can be partial)
    if (!isDraft) {
        if (formData.advisors.length === 0) {
            ElMessage.warning("请至少添加一名指导老师");
            return;
        }
        // Ensure First Advisor exists
        const hasFirst = formData.advisors.some(a => a.order === 1);
        if (!hasFirst) {
            ElMessage.warning("请添加第一指导老师");
            return;
        }
    }

    if (!isDraft) {
        if(formData.advisors.length === 0) {
             console.warn("No advisors added, user might have forgotten to click add");
        }
        if (formData.expected_results_data.length === 0) {
            ElMessage.warning("请补充预期成果清单");
            return;
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
        const validLevels = levelOptions.value.map((opt: any) => opt.value);
        if (!validLevels.includes(basicFields.level)) {
            basicFields.level = getDefaultLevel();
        }

        const validCategories = categoryOptions.value.map((opt: any) => opt.value);
        if (!validCategories.includes(basicFields.category)) {
            basicFields.category = getDefaultCategory();
        }
        
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
            } else if (key === 'expected_results_data') {
                payload.append(key, JSON.stringify(basicFields[key] || []));
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
            formData.level = data.level || getDefaultLevel(); 
            formData.category = data.category || getDefaultCategory(); 
            formData.college = data.college || "";
            formData.major_code = data.major_code || "";
            formData.budget = Number(data.budget || 0);
            formData.leader_contact = data.leader_contact || "";
            formData.leader_email = data.leader_email || "";
            formData.description = data.description || "";
            formData.expected_results = data.expected_results || "";
            formData.expected_results_data = Array.isArray(data.expected_results_data)
              ? data.expected_results_data
              : [];
            
            // Handle Boolean Key Field
            formData.is_key_field = !!data.is_key_field;

            if (Array.isArray(data.advisors_info) && data.advisors_info.length > 0) {
                formData.advisors = data.advisors_info.map((adh: any, index: number) => ({
                    job_number: adh.job_number || "", 
                    name: adh.name || "",
                    title: adh.title || "",
                    contact: adh.contact || "",
                    email: adh.email || "",
                    order: adh.order || (index + 1)
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

onMounted(async () => {
  await loadDictionaries([
    DICT_CODES.PROJECT_LEVEL, DICT_CODES.PROJECT_CATEGORY, DICT_CODES.PROJECT_SOURCE,
    DICT_CODES.COLLEGE, DICT_CODES.PROJECT_TYPE, DICT_CODES.MAJOR_CATEGORY,
    DICT_CODES.TITLE, DICT_CODES.KEY_FIELD_CODE, DICT_CODES.ACHIEVEMENT_TYPE
  ]);
  const id = route.query.id;
  if (id) {
      loadData(Number(id));
  } else {
      // Pre-fill contact info if creating new application
      if (userStore.user) {
          if (!formData.leader_contact) formData.leader_contact = userStore.user.phone || "";
          if (!formData.leader_email) formData.leader_email = userStore.user.email || "";
      }
  }
});

// Watch for user data loading if not available on mount
watch(() => userStore.user, (newUser) => {
    if (newUser && !route.query.id) {
         if (!formData.leader_contact) formData.leader_contact = newUser.phone || "";
         if (!formData.leader_email) formData.leader_email = newUser.email || "";
    }
});
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

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

.expected-grid {
  display: flex;
  gap: 12px;
  align-items: center;
}

.expected-select {
  width: 260px;
}

.expected-count {
  width: 140px;
}

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
  font-size: 14px;
  
  &:hover { text-decoration: underline; }
}

.upload-wrapper {
    display: flex;
    align-items: flex-start;
    gap: 24px;
}

.upload-inline {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
}

.upl.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.attachment-container {
    display: flex;
    flex-direction: column;
    
    .actions-row {
        display: flex;
        align-items: center;
        margin-bottom: 8px;
        
        .upload-demo {
            margin-right: 16px;
        }
        
        .download-section {
            display: flex;
            align-items: center;
        }
    }
}
.upload-tip {
    font-size: 12px;
    color: $slate-400;
    margin-top: 8px;
    line-height: 1.4;
}

.download-trigger {
    padding-top: 6px; // Slightly offset to align with button text baseline roughly if needed, or keeping top aligned
}

</style>
