<template>
  <div class="midterm-submit">
    <h2>提交中期检查</h2>
    <el-alert
      title="中期检查说明"
      type="info"
      description="请按要求填写中期检查报告，提交后将进入审核流程。"
      :closable="false"
      show-icon
      style="margin-bottom: 20px"
    />
    <el-card>
      <el-form :model="form" label-width="120px">
        <el-form-item label="项目名称">
          <el-input v-model="form.projectName" disabled />
        </el-form-item>
        <el-form-item label="完成进度">
          <el-slider v-model="form.progress" :marks="marks" />
        </el-form-item>
        <el-form-item label="已完成内容">
          <el-input
            v-model="form.completed"
            type="textarea"
            :rows="4"
            placeholder="请详细描述已完成的工作内容"
          />
        </el-form-item>
        <el-form-item label="遇到的问题">
          <el-input
            v-model="form.problems"
            type="textarea"
            :rows="4"
            placeholder="请描述项目推进过程中遇到的问题"
          />
        </el-form-item>
        <el-form-item label="下一步计划">
          <el-input
            v-model="form.nextPlan"
            type="textarea"
            :rows="4"
            placeholder="请描述下一阶段的工作计划"
          />
        </el-form-item>
        <el-form-item label="附件上传">
          <el-upload :file-list="form.files" action="#" :auto-upload="false">
            <el-button type="primary">选择文件</el-button>
          </el-upload>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSubmit">提交检查</el-button>
          <el-button @click="handleSaveDraft">保存草稿</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive } from "vue";
import { ElMessage } from "element-plus";

const marks = {
  0: "0%",
  25: "25%",
  50: "50%",
  75: "75%",
  100: "100%",
};

const form = reactive({
  projectName: "基于AI的智能问答系统",
  progress: 50,
  completed: "",
  problems: "",
  nextPlan: "",
  files: [],
});

const handleSubmit = () => {
  ElMessage.success("提交成功");
};

const handleSaveDraft = () => {
  ElMessage.success("草稿已保存");
};
</script>

<style scoped lang="scss">
.midterm-submit {
  h2 {
    margin: 0 0 20px 0;
    font-size: 20px;
    font-weight: 500;
  }
}
</style>
