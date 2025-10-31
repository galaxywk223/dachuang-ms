<template>
  <el-form
    ref="loginFormRef"
    :model="loginForm"
    :rules="rules"
    label-width="80px"
    @submit.prevent="handleSubmit"
  >
    <el-form-item label="学号/工号" prop="employeeId">
      <el-input
        v-model="loginForm.employeeId"
        placeholder="请输入学号或工号"
        clearable
        size="large"
      />
    </el-form-item>

    <el-form-item label="密码" prop="password">
      <el-input
        v-model="loginForm.password"
        type="password"
        placeholder="请输入密码"
        show-password
        size="large"
        @keyup.enter="handleSubmit"
      />
    </el-form-item>

    <el-form-item label="选择身份" prop="role">
      <el-select
        v-model="loginForm.role"
        placeholder="请选择身份"
        size="large"
        style="width: 100%"
      >
        <el-option label="学生" value="student" />
        <el-option label="二级管理员" value="admin" />
      </el-select>
    </el-form-item>

    <el-form-item>
      <el-checkbox v-model="loginForm.rememberMe">记住我</el-checkbox>
    </el-form-item>

    <el-form-item>
      <el-button
        type="primary"
        style="width: 100%"
        size="large"
        :loading="loading"
        @click="handleSubmit"
      >
        登录
      </el-button>
    </el-form-item>
  </el-form>

  <div class="tips">
    <el-alert title="默认密码为：123456" type="info" :closable="false" />
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";

const emit = defineEmits(["submit"]);

const props = defineProps({
  loading: {
    type: Boolean,
    default: false,
  },
});

const loginFormRef = ref(null);

const loginForm = reactive({
  employeeId: "",
  password: "",
  role: "student",
  rememberMe: false,
});

const rules = {
  employeeId: [
    { required: true, message: "请输入学号或工号", trigger: "blur" },
  ],
  password: [
    { required: true, message: "请输入密码", trigger: "blur" },
    { min: 6, message: "密码长度不能少于6位", trigger: "blur" },
  ],
  role: [{ required: true, message: "请选择身份", trigger: "change" }],
};

const handleSubmit = async () => {
  if (!loginFormRef.value) return;

  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      emit("submit", {
        employeeId: loginForm.employeeId,
        password: loginForm.password,
        role: loginForm.role,
      });
    }
  });
};
</script>

<style scoped lang="scss">
.tips {
  margin-top: 20px;
}
</style>
