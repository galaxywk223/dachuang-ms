<template>
  <div class="login-container">
    <div class="login-wrapper">
      <!-- Atmospheric Left Panel -->
      <div class="brand-side">
        <div class="brand-main">
          <h1 class="app-title">
            <div class="university-wrapper">
              <img
                src="@/assets/ahut_logo.jpg"
                alt="AHUT Logo"
                class="university-logo"
              />
              <span class="title-primary">安徽工业大学</span>
            </div>
            <span class="title-secondary">大创项目管理系统</span>
          </h1>
          <div class="title-decoration"></div>
          <p class="brand-slogan">创新驱动发展 &nbsp;•&nbsp; 实践成就梦想</p>
        </div>

        <div class="brand-footer">
          <p>© 2025 Anhui University of Technology. All Rights Reserved.</p>
        </div>

        <!-- Decorative Background -->
        <div class="bg-circles">
          <div class="circle c1"></div>
          <div class="circle c2"></div>
        </div>
      </div>

      <!-- Minimalist Right Panel -->
      <div class="form-side">
        <LoginForm :loading="loading" @submit="handleLogin" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useUserStore } from "@/stores/user";
import { ElMessage } from "element-plus";
import LoginForm from "@/components/forms/LoginForm.vue";

defineOptions({
  name: "LoginView",
});

const loading = ref(false);
const router = useRouter();
const userStore = useUserStore();

type LoginFormData = {
  employeeId: string;
  password: string;
};

const handleLogin = async (formData: LoginFormData) => {
  loading.value = true;
  try {
    // 使用新的登录接口，不再需要 role 参数
    const success = await userStore.loginAction(
      formData.employeeId,
      formData.password
    );

    if (success) {
      ElMessage.success({
        message: `欢迎回来，${userStore.user?.real_name || "用户"}`,
        duration: 2000,
      });

      // 根据后端返回的 default_route 进行跳转
      const defaultRoute = userStore.roleInfo?.default_route || "/";
      router.push(defaultRoute);
    }
  } catch (error: unknown) {
    const message = error instanceof Error ? error.message : "登录服务暂不可用";
    ElMessage.error(message);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped lang="scss">
@use "sass:color";
@use "@/styles/variables.scss" as *;

.login-container {
  height: 100vh;
  width: 100vw;
  display: flex;
  align-items: center;
  justify-content: center;
  // background-color: $slate-50;
  background: url("@/assets/background.png") no-repeat center center;
  background-size: cover;
  overflow: hidden;
}

.login-wrapper {
  display: flex;
  width: 1000px;
  height: 600px;
  background: #ffffff;
  border-radius: 24px;
  box-shadow: $shadow-2xl;
  overflow: hidden;
  transition: transform 0.3s ease;

  @media (max-width: 1024px) {
    width: 90%;
    height: auto;
    min-height: 500px;
  }
}

// Left Panel: Premium & Clean
.brand-side {
  flex: 1;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
  color: #ffffff;
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 48px;
  overflow: hidden;

  // Main Center Content
  .brand-main {
    z-index: 10;
    margin-bottom: 20px;

    .app-title {
      display: flex;
      flex-direction: column;
      margin: 0 0 24px 0;

      .university-wrapper {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 12px;

        .university-logo {
          width: 32px;
          height: 32px;
          border-radius: 50%;
          // border: 2px solid rgba(255, 255, 255, 0.2);
          object-fit: cover;
        }

        .title-primary {
          font-size: 28px;
          font-weight: 500;
          opacity: 0.95;
          letter-spacing: 2px;
          line-height: 1;
          margin-bottom: 0; // Reset margin
        }
      }

      .title-secondary {
        font-size: 36px;
        font-weight: 700;
        letter-spacing: 1px;
        background: linear-gradient(to right, #fff, #94a3b8);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
      }
    }

    .title-decoration {
      width: 60px;
      height: 4px;
      background: $primary-500;
      border-radius: 2px;
      margin-bottom: 24px;
    }

    .brand-slogan {
      font-size: 16px;
      font-weight: 300;
      color: $slate-300;
      letter-spacing: 2px;
      margin: 0;
    }
  }

  // Footer
  .brand-footer {
    z-index: 10;
    p {
      font-size: 12px;
      color: $slate-400;
      margin: 0;
      font-family: monospace;
      opacity: 0.7;
    }
  }

  // Background Decorations
  .bg-circles {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
    pointer-events: none;
    z-index: 1;

    .circle {
      position: absolute;
      border-radius: 50%;
      filter: blur(60px);
      opacity: 0.15;
    }

    .c1 {
      width: 300px;
      height: 300px;
      background: $primary-400;
      top: -100px;
      right: -100px;
    }

    .c2 {
      width: 400px;
      height: 400px;
      background: $primary-600;
      bottom: -150px;
      left: -150px;
    }
  }
}

// Right Panel: Minimalist Form
.form-side {
  width: 440px; // Fixed width for optimal form reading
  padding: 60px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  background: #ffffff;
}

// User Experience & Responsive
@media (max-width: 768px) {
  .login-wrapper {
    flex-direction: column;
    height: auto;
    border-radius: 16px;
  }

  .brand-side {
    padding: 40px;
    min-height: 200px;
  }

  .form-side {
    width: 100%;
    padding: 40px;
  }

  .app-title {
    font-size: 24px !important;
  }
}
</style>
