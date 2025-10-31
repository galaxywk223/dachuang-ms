<template>
  <div class="apply-page">
    <div class="page-header">
      <h2>申请项目</h2>
      <p>填写项目申请信息，提交立项申请</p>
    </div>
    <div class="page-content">
      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="180px"
        class="project-form"
      >
        <!-- 第一行：项目类别、项目级别、项目类别 -->
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="项目类别" prop="category">
              <el-select
                v-model="formData.category"
                placeholder="请选择"
                style="width: 100%"
              >
                <el-option label="创新训练项目" value="INNOVATION_TRAINING" />
                <el-option
                  label="创业训练项目"
                  value="ENTREPRENEURSHIP_TRAINING"
                />
                <el-option
                  label="创业实践项目"
                  value="ENTREPRENEURSHIP_PRACTICE"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="项目级别" prop="level">
              <el-select
                v-model="formData.level"
                placeholder="请选择"
                style="width: 100%"
              >
                <el-option label="国家级" value="NATIONAL" />
                <el-option label="省级" value="PROVINCIAL" />
                <el-option label="校级" value="SCHOOL" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="项目类别" prop="category2">
              <el-select
                v-model="formData.category2"
                placeholder="请选择"
                style="width: 100%"
              >
                <el-option label="请选择" value="" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 第二行：重点领域项目、学院、项目自筹 -->
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="重点领域项目" prop="is_key_field">
              <el-select
                v-model="formData.is_key_field"
                placeholder="请选择"
                style="width: 100%"
              >
                <el-option label="是" :value="true" />
                <el-option label="否" :value="false" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="学院" prop="college">
              <el-select
                v-model="formData.college"
                placeholder="请选择"
                style="width: 100%"
              >
                <el-option label="请选择" value="" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="项目自筹（元）" prop="self_funding">
              <el-input v-model="formData.self_funding" placeholder="请输入" />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 第三行：项目所属专业代码、负责人姓名、负责人学号 -->
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="项目所属专业代码" prop="major_code">
              <el-select
                v-model="formData.major_code"
                placeholder="请选择"
                style="width: 100%"
              >
                <el-option label="请选择" value="" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="项目负责人姓名" prop="leader_name">
              <el-input v-model="formData.leader_name" placeholder="主负" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="项目负责人学号" prop="leader_student_id">
              <el-input
                v-model="formData.leader_student_id"
                placeholder="2390774330"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 第四行：负责人联系方式、负责人邮箱 -->
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="负责人联系方式" prop="leader_contact">
              <el-input
                v-model="formData.leader_contact"
                placeholder="请输入"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="负责人联系邮箱" prop="leader_email">
              <el-input v-model="formData.leader_email" placeholder="请输入" />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 项目名称 -->
        <el-form-item label="项目名称" prop="title">
          <el-input
            v-model="formData.title"
            placeholder="请输入"
            style="width: 100%"
          />
        </el-form-item>

        <!-- 添加指导教师信息 -->
        <el-form-item label="添加指导教师信息">
          <div class="advisor-list">
            <div
              v-for="(advisor, index) in formData.advisors"
              :key="index"
              class="advisor-item"
            >
              <el-input
                v-model="advisor.name"
                placeholder="指导教师姓名"
                class="advisor-input"
              />
              <el-input
                v-model="advisor.department"
                placeholder="指导教师单位"
                class="advisor-input"
              />
              <el-input
                v-model="advisor.title"
                placeholder="指导教师职称"
                class="advisor-input"
              />
              <el-button
                type="danger"
                link
                @click="removeAdvisor(index)"
                v-if="formData.advisors.length > 1"
              >
                删除
              </el-button>
            </div>
            <el-link
              type="primary"
              :underline="false"
              @click="addAdvisor"
              class="add-link"
            >
              添加(若还有可选择添加)
            </el-link>
          </div>
        </el-form-item>

        <!-- 指导教师信息 -->
        <el-form-item label="指导教师信息">
          <div class="info-text">
            <!-- 这里显示指导教师信息汇总 -->
          </div>
        </el-form-item>

        <!-- 添加成员信息 -->
        <el-form-item label="添加成员信息">
          <div class="member-list">
            <div
              v-for="(member, index) in formData.members"
              :key="index"
              class="member-item"
            >
              <el-input
                v-model="member.student_id"
                placeholder="成员学号"
                class="member-input"
              />
              <el-input
                v-model="member.name"
                placeholder="成员姓名"
                class="member-input"
              />
              <el-button type="primary" link @click="addMember">
                添加
              </el-button>
            </div>
          </div>
        </el-form-item>

        <!-- 成员信息 -->
        <el-form-item label="成员信息">
          <div class="info-text">
            <!-- 这里显示成员信息汇总 -->
          </div>
        </el-form-item>

        <!-- 立项类别描述 -->
        <el-form-item label="立项类别描述" prop="category_description">
          <el-input
            v-model="formData.category_description"
            type="textarea"
            :rows="4"
            placeholder="立项类别是指：训练计划（或）实践类（或）企业合作（或）参加比赛"
            maxlength="30"
            show-word-limit
          />
        </el-form-item>

        <!-- 项目简介 -->
        <el-form-item label="项目简介(200字内)" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="4"
            placeholder="请输入内容"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>

        <!-- 项目申报书 -->
        <el-form-item label="项目申报书" prop="proposal_file">
          <div class="file-upload-section">
            <el-button type="success" @click="selectProposalFile">
              下载对应的项目类型的申报表进行填写
            </el-button>
            <el-button type="primary" disabled>
              学科竞赛类只需上传获奖证书或立项文件即可
            </el-button>
          </div>
        </el-form-item>

        <!-- 上传文件 -->
        <el-form-item label="上传文件" prop="attachment_file">
          <div class="upload-info">
            <el-upload
              ref="uploadRef"
              :auto-upload="false"
              :limit="1"
              accept=".pdf,.doc,.docx"
            >
              <el-button type="primary">选取文件</el-button>
            </el-upload>
            <div class="upload-hint">只能上传的文件, 且不超过2M</div>
          </div>
        </el-form-item>

        <!-- 操作按钮 -->
        <el-form-item>
          <el-space>
            <el-button type="success" @click="saveAsDraft">
              保存草稿
            </el-button>
            <el-button type="success" @click="submitForm"> 提交 </el-button>
          </el-space>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from "vue";
import { ElMessage } from "element-plus";
import type { FormInstance, FormRules } from "element-plus";
import { createProjectApplication } from "@/api/project";

// 表单引用
const formRef = ref<FormInstance>();
const uploadRef = ref();

// 表单数据
const formData = reactive({
  category: "",
  level: "",
  category2: "",
  is_key_field: false,
  college: "",
  self_funding: "0",
  major_code: "",
  leader_name: "",
  leader_student_id: "",
  leader_contact: "",
  leader_email: "",
  title: "",
  advisors: [{ name: "", department: "", title: "", contact: "", email: "" }],
  members: [{ student_id: "", name: "" }],
  category_description: "",
  description: "",
  proposal_file: null,
  attachment_file: null,
});

// 表单验证规则
const rules: FormRules = {
  category: [{ required: true, message: "请选择项目类别", trigger: "change" }],
  level: [{ required: true, message: "请选择项目级别", trigger: "change" }],
  college: [{ required: true, message: "请选择学院", trigger: "change" }],
  leader_student_id: [
    { required: true, message: "请输入负责人学号", trigger: "blur" },
  ],
  leader_contact: [
    { required: true, message: "请输入联系方式", trigger: "blur" },
  ],
  leader_email: [
    { required: true, message: "请输入邮箱", trigger: "blur" },
    { type: "email", message: "请输入正确的邮箱格式", trigger: "blur" },
  ],
  title: [{ required: true, message: "请输入项目名称", trigger: "blur" }],
};

// 添加指导教师
const addAdvisor = () => {
  formData.advisors.push({
    name: "",
    department: "",
    title: "",
    contact: "",
    email: "",
  });
};

// 删除指导教师
const removeAdvisor = (index: number) => {
  formData.advisors.splice(index, 1);
};

// 添加成员
const addMember = () => {
  formData.members.push({ student_id: "", name: "" });
};

// 选择申报书文件
const selectProposalFile = () => {
  ElMessage.info("请下载对应的申报表模板");
};

// 保存草稿
const saveAsDraft = async () => {
  try {
    const submitData = {
      ...formData,
      is_draft: true,
    };
    const response: any = await createProjectApplication(submitData);
    if (response.code === 200) {
      ElMessage.success("草稿保存成功");
    } else {
      ElMessage.error(response.message || "保存失败");
    }
  } catch (error: any) {
    ElMessage.error(error.message || "保存失败，请重试");
  }
};

// 提交表单
const submitForm = async () => {
  if (!formRef.value) return;

  await formRef.value.validate(async (valid) => {
    if (valid) {
      try {
        const submitData = {
          ...formData,
          is_draft: false,
        };
        const response: any = await createProjectApplication(submitData);
        if (response.code === 200) {
          ElMessage.success("提交成功");
          // 可以跳转到我的项目页面
          // router.push('/establishment/my-projects')
        } else {
          ElMessage.error(response.message || "提交失败");
        }
      } catch (error: any) {
        ElMessage.error(error.message || "提交失败，请重试");
      }
    } else {
      ElMessage.error("请完善表单信息");
    }
  });
};
</script>

<style scoped lang="scss">
.apply-page {
  .page-header {
    background: #ffffff;
    padding: 24px;
    border-radius: 8px;
    margin-bottom: 24px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);

    h2 {
      margin: 0 0 8px 0;
      font-size: 24px;
      color: #262626;
    }

    p {
      margin: 0;
      color: #8c8c8c;
      font-size: 14px;
    }
  }

  .page-content {
    background: #ffffff;
    padding: 24px;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  }

  .project-form {
    max-width: 1200px;

    .advisor-list,
    .member-list {
      width: 100%;
    }

    .advisor-item,
    .member-item {
      display: flex;
      gap: 12px;
      margin-bottom: 12px;
      align-items: center;
    }

    .advisor-input,
    .member-input {
      flex: 1;
    }

    .add-link {
      display: inline-block;
      margin-top: 8px;
    }

    .info-text {
      color: #8c8c8c;
      font-size: 14px;
    }

    .file-upload-section {
      display: flex;
      gap: 12px;
    }

    .upload-info {
      .upload-hint {
        margin-top: 8px;
        color: #8c8c8c;
        font-size: 12px;
      }
    }
  }
}
</style>
