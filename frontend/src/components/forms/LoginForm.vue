<template>
  <el-form
    ref="loginFormRef"
    :model="loginForm"
    :rules="rules"
    label-width="0"
    class="login-form-content"
    @submit.prevent="handleSubmit"
  >
    <div class="input-group">
      <label class="input-label">学号 / 工号</label>
      <el-form-item prop="employeeId">
        <el-input
          v-model="loginForm.employeeId"
          placeholder="请输入学号或工号"
          size="large"
          class="modern-input"
        >
          <template #prefix>
            <el-icon class="input-icon"><User /></el-icon>
          </template>
        </el-input>
      </el-form-item>
    </div>

    <div class="input-group">
      <label class="input-label">密码</label>
      <el-form-item prop="password">
        <el-input
          v-model="loginForm.password"
          type="password"
          placeholder="请输入密码"
          show-password
          size="large"
          class="modern-input"
          @keyup.enter="handleSubmit"
        >
          <template #prefix>
            <el-icon class="input-icon"><Lock /></el-icon>
          </template>
        </el-input>
      </el-form-item>
    </div>

    <div class="input-group">
      <label class="input-label">身份选择</label>
      <el-form-item prop="role">
        <el-select
          v-model="loginForm.role"
          placeholder="请选择登录身份"
          size="large"
          class="modern-select"
          style="width: 100%"
        >
          <template #prefix>
            <el-icon class="input-icon"><Avatar /></el-icon>
          </template>
          <el-option label="学生" value="student" />
          <el-option label="管理员" value="admin" />
        </el-select>
      </el-form-item>
    </div>

    <div class="form-actions">
      <el-checkbox v-model="loginForm.rememberMe" class="custom-checkbox">记住我</el-checkbox>
      <a href="#" class="forgot-link">忘记密码？</a>
    </div>

    <el-button
      type="primary"
      class="login-btn"
      :loading="loading"
      @click="handleSubmit"
    >
      登 录
      <el-icon class="el-icon--right"><ArrowRight /></el-icon>
    </el-button>

    <div class="demo-tips">
      <el-alert 
        title="演示账号默认密码：123456" 
        type="info" 
        show-icon 
        :closable="false"
        class="custom-alert" 
      />
    </div>
  </el-form>
</template>

<script setup>
import { ref, reactive } from "vue";
import { User, Lock, Avatar, ArrowRight } from "@element-plus/icons-vue";

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
  role: [{ required: true, message: "请选择登录身份", trigger: "change" }],
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
.login-form-content {
  width: 100%;
}

.input-group {
  margin-bottom: 20px;
}

.input-label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #334155;
}

/* Customizing Element Plus Inputs */
:deep(.modern-input .el-input__wrapper),
:deep(.modern-select .el-select__wrapper) {
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  box-shadow: none !important;
  border-radius: 8px;
  padding: 12px 16px;
  height: auto;
  transition: all 0.2s;
  
  &:hover, &.is-focus {
    background-color: #fff;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
  }
}

:deep(.modern-input .el-input__inner) {
  font-weight: 500;
  color: #1e293b;
  height: 24px;
}

.input-icon {
  font-size: 16px;
  color: #64748b;
  margin-right: 8px;
}

.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.forgot-link {
  font-size: 14px;
  color: #3b82f6;
  text-decoration: none;
  font-weight: 500;
  
  &:hover {
    text-decoration: underline;
  }
}

.login-btn {
  width: 100%;
  height: 52px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 8px;
  background-color: #2563eb;
  border-color: #2563eb;
  margin-bottom: 24px;
  transition: all 0.2s;
  
  &:hover {
    background-color: #1d4ed8;
    border-color: #1d4ed8;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
  }
  
  &:active {
    transform: translateY(0);
  }
}

.demo-tips {
  margin-top: 24px;
}

.custom-alert {
  background-color: #f1f5f9;
  border: 1px solid #e2e8f0;
  color: #64748b;
}

:deep(.custom-alert .el-alert__title) {
  color: #475569;
}
</style>
