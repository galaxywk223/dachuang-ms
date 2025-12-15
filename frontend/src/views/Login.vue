<template>
  <div class="login-container">
    <div class="split-layout">
      <!-- Left Side: Visual Branding -->
      <div class="brand-panel">
        <div class="brand-content">
          <div class="logo-circle">
            <span class="logo-text">MS</span>
          </div>
          <h1 class="brand-title">大创项目<br/>管理平台</h1>
          <p class="brand-subtitle">
            专业、高效、创新的大学生创新创业项目全流程管理系统
          </p>
          
          <div class="brand-features">
            <div class="feature-item">
              <div class="feature-icon">✨</div>
              <span>智能追踪</span>
            </div>
            <div class="feature-item">
              <div class="feature-icon">🚀</div>
              <span>快速审批</span>
            </div>
            <div class="feature-item">
              <div class="feature-icon">📊</div>
              <span>数据洞察</span>
            </div>
          </div>
        </div>
        
        <div class="abstract-shapes">
          <div class="shape shape-1"></div>
          <div class="shape shape-2"></div>
        </div>
      </div>

      <!-- Right Side: Login Form -->
      <div class="form-panel">
        <div class="form-container">
          <div class="form-header">
            <h2 class="welcome-title">欢迎使用</h2>
            <p class="welcome-subtitle">请登录您的账户以继续</p>
          </div>

          <LoginForm :loading="loading" @submit="handleLogin" />
          
          <div class="form-footer">
             © {{ new Date().getFullYear() }} 大创项目管理系统 版权所有
          </div>
        </div>
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
      
      setTimeout(() => {
        if (role === "student") {
          router.push("/establishment/apply");
        } else if (role === "admin") {
          router.push("/admin/dashboard");
        } else {
             // Default fallback
             router.push("/establishment/apply");
        }
      }, 500);
    } else {
      ElMessage.error("登录失败，请检查用户名和密码");
    }
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped lang="scss">
@use "@/styles/variables.scss" as *;

.login-container {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  font-family: $font-family-sans;
  background-color: $color-bg-body;
}

.split-layout {
  display: flex;
  width: 100%;
  height: 100%;
}

/* Left Panel Styles */
.brand-panel {
  flex: 1;
  // Gradient from variables
  background: linear-gradient(135deg, $primary-800 0%, $primary-500 100%);
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 80px;
  color: white;
  overflow: hidden;
  
  @media (max-width: 900px) {
    display: none;
  }
}

.brand-content {
  position: relative;
  z-index: 10;
  max-width: 520px;
}

.logo-circle {
  width: 64px;
  height: 64px;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border-radius: $radius-lg;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 40px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.logo-text {
  font-weight: 800;
  font-size: 24px;
  letter-spacing: -1px;
}

.brand-title {
  font-size: 3.5rem; // Large headline
  font-weight: 800;
  line-height: 1.1;
  margin-bottom: 24px;
  letter-spacing: -0.02em;
}

.brand-subtitle {
  font-size: $font-size-lg;
  line-height: 1.6;
  opacity: 0.9;
  margin-bottom: 48px;
  font-weight: 300;
  color: $primary-100;
}

.brand-features {
  display: flex;
  gap: 20px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.1);
  padding: 10px 16px;
  border-radius: 50px;
  font-size: $font-size-sm;
  font-weight: 500;
  backdrop-filter: blur(5px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.abstract-shapes {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
  pointer-events: none;
  
  .shape {
    position: absolute;
    border-radius: 50%;
    filter: blur(80px);
    opacity: 0.4;
  }
  
  .shape-1 {
    width: 600px;
    height: 600px;
    background: #4f46e5; // Indigo
    top: -20%;
    right: -20%;
    animation: float 15s infinite ease-in-out;
  }
  
  .shape-2 {
    width: 500px;
    height: 500px;
    background: #ec4899; // Pink/Magenta for contrast
    bottom: -10%;
    left: -10%;
    animation: float 20s infinite ease-in-out reverse;
  }
}

@keyframes float {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(30px, 30px); }
}

/* Right Panel Styles */
.form-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  background-color: $color-bg-card; // White
  padding: 40px;
}

.form-container {
  width: 100%;
  max-width: 420px;
  animation: fadeIn 0.8s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.form-header {
  margin-bottom: 40px;
  
  .welcome-title {
    font-size: 2rem;
    font-weight: 700;
    color: $slate-900;
    margin-bottom: 12px;
    letter-spacing: -0.5px;
  }
  
  .welcome-subtitle {
    color: $slate-500;
    font-size: $font-size-base;
  }
}

.form-footer {
  margin-top: 40px;
  text-align: center;
  font-size: $font-size-xs;
  color: $slate-400;
}
</style>
