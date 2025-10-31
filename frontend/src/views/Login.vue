<template>
  <div class="login-container">
    <div class="login-box">
      <h1 class="title">大 创 项 目 管 理 平 台</h1>

      <div class="login-card">
        <h2 class="card-title">系统登陆</h2>

        <LoginForm :loading="loading" @submit="handleLogin" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useUserStore } from "@/stores/user";
import { ElMessage } from "element-plus";
import LoginForm from "@/components/forms/LoginForm.vue";

const router = useRouter();
const userStore = useUserStore();

const loading = ref(false);

const handleLogin = async ({ employeeId, password, role }) => {
  loading.value = true;
  try {
    const success = await userStore.loginAction(employeeId, password, role);

    if (success) {
      ElMessage.success("登录成功");

      // 根据角色跳转到不同页面
      if (role === "student") {
        // 学生跳转到申请项目页面
        router.push("/establishment/apply");
      } else if (role === "admin") {
        // 管理员跳转到管理员首页
        router.push("/admin/dashboard");
      }
    } else {
      ElMessage.error("登录失败，请检查用户名和密码");
    }
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped lang="scss">
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #4a6fa5 0%, #3d5a80 100%);
  position: relative;
  overflow: hidden;
}

.login-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  max-width: 500px;
  padding: 20px;
}

.title {
  color: white;
  font-size: 48px;
  font-weight: 500;
  margin-bottom: 60px;
  letter-spacing: 12px;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
}

.login-card {
  width: 100%;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 50px 40px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  backdrop-filter: blur(10px);
}

.card-title {
  text-align: center;
  font-size: 28px;
  font-weight: 500;
  color: #303133;
  margin: 0 0 40px 0;
}
</style>
