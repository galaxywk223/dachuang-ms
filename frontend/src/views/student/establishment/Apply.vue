<template>
  <div class="apply-page">
    <el-card class="page-hero" shadow="hover">
      <div class="hero-text">
        <p class="eyebrow">项目申报</p>
        <h1>申请项目</h1>
        <p class="subtitle">
          以更清晰的步骤完成申报，所有字段均被保留并优化为分段式表单。
        </p>
      </div>
      <div class="hero-meta">
        <div class="meta-block">
          <span class="meta-label">负责人</span>
          <div class="meta-value">{{ currentUser.name }}</div>
          <div class="meta-sub">学号 {{ currentUser.student_id }}</div>
        </div>
        <div class="meta-block soft">
          <span class="meta-label">提示</span>
          <div class="meta-sub">请确保信息真实，分段填写更易校验</div>
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
    >
      <el-card class="section-card" shadow="hover">
        <div class="section-header">
          <el-icon class="section-icon"><InfoFilled /></el-icon>
          <div>
            <h3>基本信息</h3>
            <p class="section-desc">选择项目来源、级别与重点领域归属</p>
          </div>
        </div>
        <div class="section-body">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="项目来源" prop="source" required>
                <el-select
                  v-model="formData.source"
                  placeholder="请选择"
                  style="width: 100%"
                  size="large"
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
            <el-col :span="12">
              <el-form-item label="项目级别" prop="level" required>
                <el-select
                  v-model="formData.level"
                  placeholder="请选择"
                  style="width: 100%"
                  size="large"
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
            <el-col :span="12">
              <el-form-item label="项目类别" prop="category" required>
                <el-select
                  v-model="formData.category"
                  placeholder="请选择"
                  style="width: 100%"
                  size="large"
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
            <el-col :span="12">
              <el-form-item prop="is_key_field" required>
                <template #label>
                  <span class="label-with-tip">
                    重点领域项目
                    <el-tooltip
                      content="是否属于国家重点支持的领域"
                      placement="top"
                    >
                      <el-icon class="help-icon"><QuestionFilled /></el-icon>
                    </el-tooltip>
                  </span>
                </template>
                <el-select
                  v-model="formData.is_key_field"
                  placeholder="请选择"
                  style="width: 100%"
                  size="large"
                >
                  <el-option
                    v-for="item in specialTypeOptions"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value"
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
        </div>
      </el-card>

      <el-card class="section-card" shadow="hover">
        <div class="section-header">
          <el-icon class="section-icon"><Document /></el-icon>
          <div>
            <h3>项目详情</h3>
            <p class="section-desc">填写项目名称、归属学院与经费预算</p>
          </div>
        </div>
        <div class="section-body">
          <el-form-item label="项目名称" prop="title" required>
            <el-input
              v-model="formData.title"
              placeholder="请输入项目名称"
              clearable
              size="large"
            />
          </el-form-item>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="学院" prop="college" required>
                <el-select
                  v-model="formData.college"
                  placeholder="请选择"
                  style="width: 100%"
                  size="large"
                >
                  <el-option
                    v-for="item in collegeOptions"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value"
                  />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item
                label="项目所属专业代码"
                prop="major_code"
                required
              >
                <el-select
                  v-model="formData.major_code"
                  placeholder="请选择"
                  style="width: 100%"
                  filterable
                  size="large"
                >
                  <el-option
                    v-for="item in majorOptions"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value"
                  />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-form-item label="项目经费 (元)" prop="budget" required>
            <el-input-number
              v-model="formData.budget"
              :min="0"
              :step="100"
              style="width: 100%"
              placeholder="请输入"
              size="large"
            />
          </el-form-item>
        </div>
      </el-card>

      <el-card class="section-card" shadow="hover">
        <div class="section-header">
          <el-icon class="section-icon"><UserFilled /></el-icon>
          <div>
            <h3>团队组建</h3>
            <p class="section-desc">负责人信息、指导教师与成员列表</p>
          </div>
        </div>
        <div class="section-body">
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="项目负责人姓名">
                <el-input
                  v-model="currentUser.name"
                  disabled
                  size="large"
                  class="is-disabled-light"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="项目负责人学号">
                <el-input
                  v-model="currentUser.student_id"
                  disabled
                  size="large"
                  class="is-disabled-light"
                />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item
                label="负责人联系方式"
                prop="leader_contact"
                required
              >
                <el-input
                  v-model="formData.leader_contact"
                  placeholder="请输入手机号"
                  size="large"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item
                label="负责人联系邮箱"
                prop="leader_email"
                required
              >
                <el-input
                  v-model="formData.leader_email"
                  placeholder="请输入邮箱"
                  size="large"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <div class="subsection">
            <div class="subsection-head">
              <span>指导教师</span>
              <span class="sub-label">第一指导教师必须填写所有信息</span>
            </div>
            <div
              v-for="(advisor, index) in formData.advisors"
              :key="index"
              class="dynamic-row"
            >
              <el-row :gutter="16">
                <el-col :span="6">
                  <el-input
                    v-model="advisor.job_number"
                    placeholder="指导教师工号"
                    size="large"
                  />
                </el-col>
                <el-col :span="6">
                  <el-input
                    v-model="advisor.name"
                    placeholder="指导教师姓名"
                    size="large"
                  />
                </el-col>
                <el-col :span="6">
                  <el-select
                    v-model="advisor.title"
                    placeholder="指导教师职称"
                    style="width: 100%"
                    size="large"
                  >
                    <el-option
                      v-for="item in advisorTitleOptions"
                      :key="item.value"
                      :label="item.label"
                      :value="item.value"
                    />
                  </el-select>
                </el-col>
                <el-col :span="6">
                  <el-input
                    v-model="advisor.contact"
                    placeholder="指导教师联系方式"
                    size="large"
                  />
                </el-col>
              </el-row>
              <el-row :gutter="16" class="mt-2">
                <el-col :span="12">
                  <el-input
                    v-model="advisor.email"
                    placeholder="指导教师邮箱"
                    size="large"
                  />
                </el-col>
                <el-col :span="12" class="action-col">
                  <el-button
                    type="primary"
                    link
                    v-if="index === formData.advisors.length - 1"
                    @click="addAdvisor"
                  >
                    添加指导教师
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
            </div>
            <div class="info-display" v-if="advisorsDisplayText">
              <label>当前教师：</label>
              <div class="info-content">{{ advisorsDisplayText }}</div>
            </div>
          </div>

          <div class="subsection">
            <div class="subsection-head">
              <span>成员</span>
              <span class="sub-label">补充学号与姓名，动态添加</span>
            </div>
            <div
              v-for="(member, index) in formData.members"
              :key="index"
              class="dynamic-row"
            >
              <el-row :gutter="16">
                <el-col :span="10">
                  <el-input
                    v-model="member.student_id"
                    placeholder="成员学号"
                    size="large"
                  />
                </el-col>
                <el-col :span="10">
                  <el-input
                    v-model="member.name"
                    placeholder="成员姓名"
                    size="large"
                  />
                </el-col>
                <el-col :span="4" class="action-col">
                  <el-button
                    type="primary"
                    link
                    v-if="index === formData.members.length - 1"
                    @click="addMember"
                  >
                    添加成员
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
            <div class="info-display" v-if="membersDisplayText">
              <label>当前成员：</label>
              <div class="info-content">{{ membersDisplayText }}</div>
            </div>
          </div>
        </div>
      </el-card>

      <el-card class="section-card" shadow="hover">
        <div class="section-header">
          <el-icon class="section-icon"><Document /></el-icon>
          <div>
            <h3>申报内容</h3>
            <p class="section-desc">简述项目简介与预期成果</p>
          </div>
        </div>
        <div class="section-body">
          <el-form-item
            label="立项预期成果"
            prop="expected_results"
            required
          >
            <el-input
              v-model="formData.expected_results"
              type="textarea"
              :rows="3"
              placeholder="调研报告/发表文章/申请专利/参加竞赛/实物/软件"
              maxlength="200"
              show-word-limit
              size="large"
            />
          </el-form-item>
          <el-form-item label="项目简介 (200字内)" prop="description" required>
            <el-input
              v-model="formData.description"
              type="textarea"
              :rows="4"
              placeholder="请输入内容"
              maxlength="200"
              show-word-limit
              size="large"
            />
          </el-form-item>
        </div>
      </el-card>

      <el-card class="section-card" shadow="hover">
        <div class="section-header">
          <el-icon class="section-icon"><Upload /></el-icon>
          <div>
            <h3>附件</h3>
            <p class="section-desc">下载模板并上传申请书或证明材料</p>
          </div>
        </div>
        <div class="section-body">
          <div class="upload-container">
            <el-button type="success" :icon="Download" size="large">
              下载对应项目类型的申请书模板
            </el-button>
            <span class="text-secondary">学科竞赛类只需上传获奖证书或立项文件即可</span>
          </div>
          <el-form-item
            label="上传文件"
            prop="attachment_file"
            required
            class="full-width mt-3"
          >
            <div class="upload-wrapper">
              <el-upload
                action="#"
                :auto-upload="false"
                :on-change="handleFileChange"
                :file-list="fileList"
              >
                <el-button type="primary" :icon="Upload" size="large">
                  选取文件
                </el-button>
              </el-upload>
              <span class="upload-tip">仅限 pdf 文件，且不超过 2M</span>
            </div>
          </el-form-item>
        </div>
      </el-card>
    </el-form>

    <div class="action-bar">
      <div class="action-inner">
        <div class="hint">
          <span class="dot"></span>
          进度实时保存草稿，确认后提交审核
        </div>
        <div class="actions">
          <el-button size="large" @click="handleReset">重置</el-button>
          <el-button type="success" plain size="large" @click="saveAsDraft">
            保存草稿
          </el-button>
          <el-button type="success" size="large" @click="submitForm">
            提交
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from "vue";
import { ElMessage, type FormInstance } from "element-plus";
import {
  QuestionFilled,
  Upload,
  Download,
  InfoFilled,
  UserFilled,
  Document
} from "@element-plus/icons-vue";
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
  is_key_field: "NORMAL", // Default to Normal instead of boolean false
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
const sourceOptions = computed(() => getOptions(DICT_CODES.PROJECT_SOURCE));
const collegeOptions = computed(() => getOptions(DICT_CODES.COLLEGE));
const specialTypeOptions = computed(() => getOptions(DICT_CODES.SPECIAL_PROJECT_TYPE));
const majorOptions = computed(() => getOptions(DICT_CODES.MAJOR_CATEGORY));
const advisorTitleOptions = computed(() => getOptions(DICT_CODES.ADVISOR_TITLE));
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
      DICT_CODES.PROJECT_SOURCE,
      DICT_CODES.COLLEGE,
      DICT_CODES.SPECIAL_PROJECT_TYPE,
      DICT_CODES.MAJOR_CATEGORY,
      DICT_CODES.ADVISOR_TITLE
  ]);
});

</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.apply-page {
  max-width: 1000px;
  margin: 0 auto;
  padding: 32px 20px 120px;
  background: linear-gradient(135deg, #f6f8fb 0%, #eef1f6 100%);
}

.page-hero {
  margin-bottom: 20px;
  padding: 24px 28px;
  border: 1px solid rgba(87, 117, 144, 0.12);
  background: linear-gradient(120deg, rgba(79, 70, 229, 0.08), rgba(15, 23, 42, 0.06));
  display: flex;
  justify-content: space-between;
  gap: 16px;

  h1 {
    margin: 0 0 8px;
    font-size: 24px;
    font-weight: 700;
    color: $text-primary;
  }

  .subtitle {
    color: $text-secondary;
    margin: 0;
  }
}

.eyebrow {
  letter-spacing: 0.08em;
  color: $primary-color;
  font-weight: 700;
  text-transform: uppercase;
  margin: 0 0 8px;
}

.hero-text {
  flex: 1;
}

.hero-meta {
  display: flex;
  gap: 12px;
  align-items: center;
}

.meta-block {
  min-width: 160px;
  padding: 12px 14px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);

  &.soft {
    background: rgba(255, 255, 255, 0.6);
  }
}

.meta-label {
  display: block;
  font-size: 12px;
  color: $text-secondary;
}

.meta-value {
  font-size: 18px;
  font-weight: 700;
  color: $text-primary;
  margin: 4px 0;
}

.meta-sub {
  font-size: 12px;
  color: $text-secondary;
}

.stacked-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section-card {
  border: 1px solid rgba(87, 117, 144, 0.12);
  transition: transform 0.15s ease, box-shadow 0.15s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 16px 30px rgba(15, 23, 42, 0.08);
  }
}

.section-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;

  h3 {
    margin: 0;
    font-size: 18px;
    font-weight: 700;
    color: $text-primary;
  }

  .section-desc {
    margin: 4px 0 0;
    color: $text-secondary;
  }
}

.section-icon {
  color: $primary-color;
  background: rgba(79, 70, 229, 0.12);
  border-radius: 12px;
  padding: 10px;
  font-size: 18px;
}

.section-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.label-with-tip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.help-icon {
  color: $text-secondary;
  cursor: pointer;
}

.subsection {
  margin-top: 8px;
  padding: 16px;
  border-radius: 12px;
  background: rgba(79, 70, 229, 0.04);
  border: 1px dashed rgba(79, 70, 229, 0.2);
}

.subsection-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  color: $text-primary;
  margin-bottom: 10px;

  .sub-label {
    font-weight: 400;
    font-size: 12px;
    color: $text-secondary;
  }
}

.dynamic-row {
  background: #fff;
  border: 1px solid rgba(87, 117, 144, 0.12);
  border-radius: 10px;
  padding: 12px;
  box-shadow: 0 6px 20px rgba(15, 23, 42, 0.04);
  & + .dynamic-row {
    margin-top: 12px;
  }
}

.info-display {
  margin-top: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: $text-secondary;

  .info-content {
    background: #fff;
    border-radius: 999px;
    padding: 6px 12px;
    color: $text-primary;
    box-shadow: inset 0 0 0 1px rgba(87, 117, 144, 0.12);
  }
}

.upload-container {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;

  .text-secondary {
    color: $text-secondary;
    font-size: 13px;
  }
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

.full-width {
  width: 100%;
}

.is-disabled-light :deep(.el-input__wrapper) {
  background-color: #f5f7fa;
}

.action-col {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  height: 100%;
}

.action-bar {
  position: sticky;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 12px 0;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0) 0%, #f6f8fb 35%);
  backdrop-filter: blur(6px);
}

.action-inner {
  max-width: 1000px;
  margin: 0 auto;
  padding: 12px 20px;
  border-radius: 14px;
  border: 1px solid rgba(87, 117, 144, 0.12);
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  box-shadow: 0 -6px 20px rgba(15, 23, 42, 0.08);
}

.actions {
  display: flex;
  gap: 12px;
}

.hint {
  display: flex;
  align-items: center;
  gap: 8px;
  color: $text-secondary;
  font-size: 13px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: $success-color;
  box-shadow: 0 0 0 6px rgba(34, 197, 94, 0.16);
}

.mt-2 {
  margin-top: 8px;
}

.mt-3 {
  margin-top: 12px;
}
</style>
