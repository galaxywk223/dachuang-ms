<template>
  <div class="login-container">
    <div class="login-wrapper">
      <!-- Atmospheric Left Panel -->
      <div class="brand-side">
        <div class="brand-content">
          <div class="logo-area">
            <div class="logo-circle">
              <img src="@/assets/ahut_logo.jpg" alt="AHUT Logo" class="brand-logo-img" />
            </div>
            <h1 class="app-title">安徽工业大学<br>大创项目管理系统</h1>
          </div>
          <p class="brand-slogan">
            创新驱动发展 &nbsp;•&nbsp; 实践成就梦想
          </p>
          <div class="brand-footer">
            <span>© 2025 Anhui University of Technology</span>
          </div>
        </div>
        <!-- Decorative Background Elements -->
        <div class="bg-shape shape-1"></div>
        <div class="bg-shape shape-2"></div>
      </div>

      <!-- Minimalist Right Panel -->
      <div class="form-side">
        <div class="form-header">
          <h2>欢迎登录</h2>
          <p>请使用您的学号/工号进行身份验证</p>
        </div>
        
        <LoginForm :loading="loading" @submit="handleLogin" />
        
        <div class="form-footer">
          <el-button link type="info" size="small">忘记密码?</el-button>
          <el-divider direction="vertical" />
          <el-button link type="primary" size="small">帮助中心</el-button>
        </div>
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
  role?: string;
};

const handleLogin = async (formData: LoginFormData) => {
  loading.value = true;
  try {
    // Correct store action usage with destructured args
    const success = await userStore.loginAction(
      formData.employeeId, 
      formData.password, 
      formData.role
    );
    
    if (success) {
      ElMessage.success({
        message: `欢迎回来，${userStore.user?.real_name || '用户'}`,
        duration: 2000,
      });
      // Redirect based on role
      switch (formData.role) {
        case 'level1_admin':
          router.push('/level1-admin/users/students');
          break;
        case 'level2_admin':
          router.push('/level2-admin/projects');
          break;
        case 'expert':
          router.push('/expert/reviews');
          break;
        case 'teacher':
          router.push('/teacher/dashboard');
          break;
        case 'student':
        default:
          router.push('/');
          break;
      }
    } else {
      ElMessage.error("登录失败，请检查用户名或密码");
    }
  } catch (error: unknown) {
    const message =
      error instanceof Error ? error.message : "登录服务暂不可用";
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

// Left Panel: Atmospheric
.brand-side {
  flex: 1;
  background: linear-gradient(135deg, $primary-800 0%, $primary-600 100%); // Royal Blue Gradient
  color: #ffffff;
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 60px;
  overflow: hidden;

  .brand-content {
    position: relative;
    z-index: 10;
  }

  .logo-area {
    margin-bottom: 40px;
    
    .logo-circle {
      width: 64px;
      height: 64px;
      background: rgba(255, 255, 255, 0.15);
      backdrop-filter: blur(12px);
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-bottom: 24px;
      border: 4px solid rgba(255, 255, 255, 0.2); // Thicker border for avatar look
      overflow: hidden; // Ensure image stays inside
      
      .brand-logo-img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        // border-radius: 50%; // Handled by parent overflow
      }
    }

    .app-title {
      font-size: 32px;
      font-weight: 700;
      line-height: 1.3;
      margin: 0;
      letter-spacing: 0.5px;
      text-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
  }

  .brand-slogan {
    font-size: 16px;
    opacity: 0.9;
    font-weight: 300;
    letter-spacing: 2px;
  }

  .brand-footer {
    position: absolute;
    bottom: 40px;
    left: 60px;
    font-size: 12px;
    opacity: 0.6;
    font-family: monospace;
  }

  // Abstract Shapes
  .bg-shape {
    position: absolute;
    border-radius: 50%;
    filter: blur(80px);
    opacity: 0.4;
  }
  
  .shape-1 {
    width: 300px;
    height: 300px;
    background: color.adjust($primary-400, $lightness: 10%);
    top: -50px;
    right: -50px;
  }
  
  .shape-2 {
    width: 400px;
    height: 400px;
    background: color.adjust($primary-800, $lightness: -5%);
    bottom: -100px;
    left: -100px;
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

  .form-header {
    margin-bottom: 40px;
    text-align: center;

    h2 {
      font-size: 24px;
      color: $slate-800;
      margin: 0 0 12px 0;
      font-weight: 600;
    }

    p {
      color: $slate-500;
      font-size: 14px;
      margin: 0;
    }
  }

  .form-footer {
    margin-top: 30px;
    text-align: center;
  }
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
