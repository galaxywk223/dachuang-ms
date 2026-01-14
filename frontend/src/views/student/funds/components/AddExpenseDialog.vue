<template>
  <el-dialog
    title="录入经费支出"
    :model-value="visible"
    width="500px"
    @update:model-value="handleUpdateVisible"
    @close="handleClose"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="支出事项" prop="title">
        <el-input v-model="form.title" placeholder="请输入支出事项名称" />
      </el-form-item>

      <el-form-item label="支出金额" prop="amount">
        <el-input-number
          v-model="form.amount"
          :min="0.01"
          :precision="2"
          :step="100"
          style="width: 100%"
          placeholder="请输入金额"
        />
      </el-form-item>

      <el-form-item label="支出日期" prop="expenditure_date">
        <el-date-picker
          v-model="form.expenditure_date"
          type="date"
          placeholder="选择日期"
          style="width: 100%"
          value-format="YYYY-MM-DD"
        />
      </el-form-item>

      <el-form-item label="凭证文件" prop="proof_file">
        <el-upload
          class="upload-demo"
          :action="uploadAction"
          :headers="headers"
          :on-success="handleUploadSuccess"
          :on-error="handleUploadError"
          :before-upload="beforeUpload"
          :limit="1"
          :file-list="fileList"
          name="file"
        >
          <!-- 注意：这里为了简化，我们暂时假设后端 proof_file 是直接在创建时上传，或者先上传获取 URL。
                 通常 Django REST Framework 的 FileField 可以在 create 时直接接收文件对象。
                 但这里使用了 el-upload，通常是异步上传。
                 如果我们要随表单一起提交文件，可以使用 :auto-upload="false" 然后用 FormData。
                 
                 为了兼容现有 API (ProjectExpenditureViewSet)，我们采用 FormData 提交。
            -->
          <el-button type="primary">点击上传凭证</el-button>
          <template #tip>
            <div class="el-upload__tip">
              只能上传 jpg/png/pdf 文件，且不超过 5MB
            </div>
          </template>
        </el-upload>
      </el-form-item>
    </el-form>

    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" :loading="loading" @click="handleSubmit">
          确认录入
        </el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive } from "vue";
import type { FormInstance, FormRules, UploadFile } from "element-plus";
import { ElMessage } from "element-plus";
import request from "@/utils/request";

const props = defineProps<{
  visible: boolean;
  projectId: number | null;
}>();

const emit = defineEmits(["update:visible", "success"]);

const formRef = ref<FormInstance>();
const loading = ref(false);
const fileList = ref<UploadFile[]>([]);
const uploadFile = ref<File | null>(null);

const form = reactive({
  title: "",
  amount: 0,
  expenditure_date: "",
});

const rules = reactive<FormRules>({
  title: [{ required: true, message: "请输入支出事项", trigger: "blur" }],
  amount: [{ required: true, message: "请输入金额", trigger: "blur" }],
  expenditure_date: [
    { required: true, message: "请选择日期", trigger: "change" },
  ],
});

// 计算属性或常量
const uploadAction = "#"; // 不使用自动上传
const headers = {};

const handleUpdateVisible = (val: boolean) => {
  emit("update:visible", val);
};

const handleClose = () => {
  emit("update:visible", false);
  formRef.value?.resetFields();
  fileList.value = [];
  uploadFile.value = null;
};

const beforeUpload = (file: File) => {
  const isLt5M = file.size / 1024 / 1024 < 5;
  if (!isLt5M) {
    ElMessage.error("上传文件大小不能超过 5MB!");
    return false;
  }

  // 简单验证类型
  const allowedTypes = ["image/jpeg", "image/png", "application/pdf"];
  if (!allowedTypes.includes(file.type)) {
    ElMessage.error("只能上传 JPG/PNG/PDF 文件!");
    return false;
  }

  uploadFile.value = file;
  fileList.value = [
    { name: file.name, status: "ready", raw: file } as UploadFile,
  ];
  return false; // 阻止自动上传
};

const handleUploadSuccess = () => {};
const handleUploadError = () => {};

const handleSubmit = async () => {
  if (!formRef.value) return;
  
  try {
    await formRef.value.validate();
  } catch {
    return;
  }

  if (!props.projectId) {
    ElMessage.error("项目信息缺失");
    return;
  }

  loading.value = true;
  try {
    const formData = new FormData();
    formData.append("project", props.projectId.toString());
    formData.append("title", form.title);
    formData.append("amount", form.amount.toString());
    formData.append("expenditure_date", form.expenditure_date);

    if (uploadFile.value) {
      formData.append("proof_file", uploadFile.value);
    }

    await request.post("/projects/expenditures/", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    ElMessage.success("经费录入成功");
    emit("success");
    handleClose();
  } catch (error: unknown) {
    console.error(error);
    const message = error instanceof Error ? error.message : "录入失败";
    ElMessage.error(message);
  } finally {
    loading.value = false;
  }
};
</script>
