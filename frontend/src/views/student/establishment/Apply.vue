<template>
  <div class="apply-page page-container">
    <div class="card-panel header-card">
      <div class="flex-between">
        <div>
          <h2>申请项目</h2>
          <p class="subtitle">请按照要求填写真实的申报信息</p>
        </div>
        <div class="actions">
          <el-button @click="handleReset">重置</el-button>
          <el-button type="success" plain @click="saveAsDraft">
            保存草稿
          </el-button>
          <el-button type="success" @click="submitForm">提交</el-button>
        </div>
      </div>
    </div>

    <div class="card-panel form-card">
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="140px"
        class="project-form"
        status-icon
      >
        <!-- 第一行 -->
        <el-row :gutter="40">
          <el-col :span="8">
            <el-form-item label="项目来源" prop="source" required>
              <el-select
                v-model="formData.source"
                placeholder="请选择"
                style="width: 100%"
              >
                <el-option
                  v-for="item in sourceOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="项目级别" prop="level" required>
              <el-select
                v-model="formData.level"
                placeholder="请选择"
                style="width: 100%"
              >
                <el-option
                  v-for="item in levelOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="项目类别" prop="category" required>
              <el-select
                v-model="formData.category"
                placeholder="请选择"
                style="width: 100%"
              >
                <el-option
                  v-for="item in categoryOptions"
                  :key="item.value"
                  :label="item.label"
                  :value="item.value"
                />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 第二行 -->
        <el-row :gutter="40">
          <el-col :span="8">
            <el-form-item label="重点领域项目" prop="is_key_field" required>
              <el-select
                v-model="formData.is_key_field"
                placeholder="请选择"
                style="width: 100%"
              >
                <el-option label="是" :value="true" />
                <el-option label="否" :value="false" />
              </el-select>
              <el-tooltip
                content="是否属于国家重点支持的领域"
                placement="top"
                class="help-icon"
              >
                <el-icon><QuestionFilled /></el-icon>
              </el-tooltip>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="学院" prop="college" required>
              <el-select
                v-model="formData.college"
                placeholder="请选择"
                style="width: 100%"
              >
                <el-option label="计算机学院" value="CS" />
                <el-option label="软件学院" value="SE" />
                <!-- 暂时硬编码，后续可改为字典 -->
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="项目经费 (元)" prop="budget" required>
              <el-input-number
                v-model="formData.budget"
                :min="0"
                :step="100"
                style="width: 100%"
                placeholder="请输入"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 第三行 -->
        <el-row :gutter="40">
          <el-col :span="8">
            <el-form-item label="项目所属专业代码" prop="major_code" required>
              <el-input v-model="formData.major_code" placeholder="请选择" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="项目负责人姓名">
              <el-input
                v-model="currentUser.name"
                disabled
                class="is-disabled-light"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="项目负责人学号">
              <el-input
                v-model="currentUser.student_id"
                disabled
                class="is-disabled-light"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 第四行 -->
        <el-row :gutter="40">
          <el-col :span="12">
            <el-form-item label="负责人联系方式" prop="leader_contact" required>
              <el-input
                v-model="formData.leader_contact"
                placeholder="请输入手机号"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="负责人联系邮箱" prop="leader_email" required>
              <el-input
                v-model="formData.leader_email"
                placeholder="请输入邮箱"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 项目名称 -->
        <el-form-item label="项目名称" prop="title" required class="full-width">
          <el-input
            v-model="formData.title"
            placeholder="请输入项目名称"
            clearable
          />
        </el-form-item>

        <!-- 动态列表：指导教师 -->
        <div class="dynamic-section">
          <div class="section-label">
            添加指导教师信息：
            <span class="sub-label">第一指导教师必须填写所有信息</span>
          </div>
          <div
            v-for="(advisor, index) in formData.advisors"
            :key="index"
            class="dynamic-row"
          >
            <el-row :gutter="20">
              <el-col :span="5">
                <el-input v-model="advisor.job_number" placeholder="指导教师工号" />
              </el-col>
              <el-col :span="5">
                <el-input v-model="advisor.name" placeholder="指导教师姓名" />
              </el-col>
              <el-col :span="5">
                <el-input v-model="advisor.title" placeholder="指导教师职称" />
              </el-col>
              <el-col :span="5">
                <el-input v-model="advisor.contact" placeholder="指导教师联系方式" />
              </el-col>
              <el-col :span="4" class="action-col">
                <el-button
                  type="primary"
                  link
                  v-if="index === formData.advisors.length - 1"
                  @click="addAdvisor"
                >
                  添加
                </el-button>
                <el-button
                  type="danger"
                  link
                  v-if="formData.advisors.length > 1"
                  @click="removeAdvisor(index)"
                >
                  删除
                </el-button>
              </el-col>
            </el-row>
            <el-row :gutter="20" class="mt-2">
              <el-col :span="10">
                 <el-input v-model="advisor.email" placeholder="指导教师邮箱" />
              </el-col>
            </el-row>
          </div>
        </div>

        <div class="info-display">
          <label>指导教师信息：</label>
          <div class="info-content">
             {{ advisorsDisplayText }}
          </div>
        </div>

        <!-- 动态列表：成员 -->
        <div class="dynamic-section">
          <div class="section-label">添加成员信息：</div>
          <div
            v-for="(member, index) in formData.members"
            :key="index"
            class="dynamic-row"
          >
            <el-row :gutter="20">
              <el-col :span="8">
                <el-input v-model="member.student_id" placeholder="成员学号" />
              </el-col>
              <el-col :span="8">
                <el-input v-model="member.name" placeholder="成员姓名" />
              </el-col>
              <el-col :span="8" class="action-col">
                <el-button
                  type="primary"
                  link
                  v-if="index === formData.members.length - 1"
                  @click="addMember"
                >
                  添加
                </el-button>
                 <el-button
                  type="danger"
                  link
                  v-if="formData.members.length > 1"
                  @click="removeMember(index)"
                >
                  删除
                </el-button>
              </el-col>
            </el-row>
          </div>
        </div>
        
        <div class="info-display">
          <label>成员信息：</label>
          <div class="info-content">
             {{ membersDisplayText }}
          </div>
        </div>

        <!-- 立项预期成果 -->
        <el-form-item label="立项预期成果" prop="expected_results" required class="full-width mt-4">
          <el-input
            v-model="formData.expected_results"
            type="textarea"
            :rows="3"
            placeholder="立项预期成果: 调研报告/发表文章/申请专利/参加竞赛/实物/软件"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>

        <!-- 项目简介 -->
        <el-form-item label="项目简介(200字内)" prop="description" required class="full-width">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="4"
            placeholder="请输入内容"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>

        <!-- 项目申请书 -->
        <el-form-item label="项目申请书" required class="full-width">
           <div class="upload-container">
             <el-button type="success" icon="Download" class="mr-4">下载对应项目类型的申请书模板</el-button>
             <span class="text-secondary text-sm">学科竞赛类只需上传获奖证书或立项文件即可</span>
           </div>
        </el-form-item>

        <!-- 上传文件 -->
        <el-form-item label="上传文件" prop="attachment_file" required class="full-width">
          <div class="upload-wrapper">
             <el-upload
                action="#"
                :auto-upload="false"
                :on-change="handleFileChange"
                :file-list="fileList"
             >
               <el-button type="primary" icon="Upload">选取文件</el-button>
             </el-upload>
             <span class="upload-tip">只能上传pdf文件，且不超过2M</span>
          </div>
        </el-form-item>

      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from "vue";
import { ElMessage, type FormInstance } from "element-plus";
import { QuestionFilled, Upload, Download } from "@element-plus/icons-vue";
import { useDictionary } from "@/composables/useDictionary";
import { DICT_CODES } from "@/api/dictionary";
import { useUserStore } from "@/stores/user";

const userStore = useUserStore();
const { loadDictionaries, getOptions } = useDictionary();
const formRef = ref<FormInstance>();

// Current User Info (Mock or from Store)
const currentUser = computed(() => ({
  name: userStore.user?.real_name || "王凯",
  student_id: userStore.user?.username || "239074336"
}));

// Form Data matches backend + extra UI fields
const formData = reactive({
  source: "",
  level: "",
  category: "",
  is_key_field: false,
  college: "",
  budget: 0,
  major_code: "",
  leader_contact: "",
  leader_email: "",
  title: "",
  expected_results: "",
  description: "",
  advisors: [
    { job_number: "", name: "", title: "", contact: "", email: "" }
  ],
  members: [
    { student_id: "", name: "" }
  ],
  attachment_file: null as File | null
});

const fileList = ref([]);

// Rules
const rules = {
  source: [{ required: true, message: "请选择项目来源", trigger: "change" }],
  level: [{ required: true, message: "请选择项目级别", trigger: "change" }],
  category: [{ required: true, message: "请选择项目类别", trigger: "change" }],
  title: [{ required: true, message: "请输入项目名称", trigger: "blur" }],
  leader_contact: [{ required: true, message: "请输入联系方式", trigger: "blur" }],
  leader_email: [{ required: true, message: "请输入邮箱", trigger: "blur" }]
};

// Dictionaries
const sourceOptions = computed(() => getOptions("project_source") || [
    { label: "学生自拟", value: "STUDENT_PROPOSED" }, // Fallback
    { label: "教师选题", value: "TEACHER" }
]);
const levelOptions = computed(() => getOptions(DICT_CODES.PROJECT_LEVEL));
const categoryOptions = computed(() => getOptions(DICT_CODES.PROJECT_CATEGORY));

// Computed Display Text
const advisorsDisplayText = computed(() => {
  return formData.advisors
    .filter(a => a.name)
    .map(a => `${a.name}(${a.title || '无职称'})`)
    .join("、");
});

const membersDisplayText = computed(() => {
   return formData.members
    .filter(m => m.name)
    .map(m => `${m.name}(${m.student_id})`)
    .join("、");
});

// Actions
const addAdvisor = () => {
  formData.advisors.push({ job_number: "", name: "", title: "", contact: "", email: "" });
};
const removeAdvisor = (index: number) => {
  formData.advisors.splice(index, 1);
};

const addMember = () => {
  formData.members.push({ student_id: "", name: "" });
};
const removeMember = (index: number) => {
  formData.members.splice(index, 1);
};

const handleFileChange = (file: any) => {
  formData.attachment_file = file.raw;
  // Validate size/type here
};

const handleReset = () => {
  if (formRef.value) formRef.value.resetFields();
};

const saveAsDraft = () => {
  ElMessage.success("保存草稿功能暂未连接API");
};

const submitForm = async () => {
    if (!formRef.value) return;
    await formRef.value.validate((valid) => {
        if (valid) {
            ElMessage.success("提交成功 (模拟)");
        } else {
            ElMessage.error("请完善表单信息");
        }
    });
};

onMounted(() => {
  loadDictionaries([
      DICT_CODES.PROJECT_LEVEL, 
      DICT_CODES.PROJECT_CATEGORY,
      // "project_source" // Will fail until backend dictionary is created
  ]);
});

</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.header-card {
  padding: 20px 32px;
  margin-bottom: $spacing-lg;

  h2 {
    margin: 0;
    font-size: 20px;
    font-weight: 600;
  }
  
  .subtitle {
    color: $text-secondary;
    margin-top: 4px;
    font-size: 14px;
  }
}

.form-card {
  padding: 32px 40px;
}

.help-icon {
  color: $text-secondary;
  margin-left: 8px;
  cursor: pointer;
}

.section-label {
  font-weight: 600;
  color: $text-primary;
  margin-bottom: 12px;
  
  .sub-label {
    font-weight: normal;
    color: $text-secondary;
    font-size: 12px;
    margin-left: 12px;
  }
}

.dynamic-section {
  background: $background-base;
  padding: 16px;
  border-radius: $border-radius-base;
  margin-bottom: 24px;
  border: 1px dashed $border-base;

  .dynamic-row:not(:last-child) {
    margin-bottom: 16px;
    padding-bottom: 16px;
    border-bottom: 1px solid rgba(0,0,0,0.05);
  }
}

.info-display {
  margin-bottom: 24px;
  display: flex;
  align-items: flex-start;
  font-size: 14px;
  
  label {
    color: $text-secondary;
    min-width: 100px;
  }
  
  .info-content {
    color: $text-primary;
    font-weight: 500;
  }
}

.mt-2 { margin-top: 8px; }
.mt-4 { margin-top: 16px; }
.mr-4 { margin-right: 16px; }

.full-width {
  width: 100%;
}

.is-disabled-light :deep(.el-input__wrapper) {
  background-color: #f5f7fa; // Lighter disabled state
}

.upload-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
  
  .upload-tip {
    font-size: 12px;
    color: $text-secondary;
  }
}

.action-col {
  display: flex;
  align-items: center;
}
</style>
