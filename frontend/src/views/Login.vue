<template>
  <div class="login-container">
    <!-- 动态网格背景 -->
    <div class="grid-background">
      <div class="grid-lines"></div>
      <div class="glow-orb orb-1"></div>
      <div class="glow-orb orb-2"></div>
    </div>

    <!-- 浮动数据粒子 -->
    <div class="data-particles">
      <span v-for="i in 20" :key="i" class="particle" :style="getParticleStyle(i)"></span>
    </div>

    <!-- 登录卡片 -->
    <div class="login-card">
      <!-- 顶部装饰线 -->
      <div class="card-top-line"></div>

      <!-- Logo区域 -->
      <div class="logo-section">
        <div class="logo-icon">
          <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="4" y="8" width="40" height="32" rx="4" stroke="currentColor" stroke-width="2"/>
            <rect x="8" y="14" width="12" height="8" rx="1" fill="currentColor" opacity="0.6"/>
            <rect x="8" y="26" width="12" height="8" rx="1" fill="currentColor" opacity="0.4"/>
            <line x1="24" y1="14" x2="40" y2="14" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <line x1="24" y1="20" x2="36" y2="20" stroke="currentColor" stroke-width="2" stroke-linecap="round" opacity="0.6"/>
            <line x1="24" y1="26" x2="40" y2="26" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <line x1="24" y1="32" x2="32" y2="32" stroke="currentColor" stroke-width="2" stroke-linecap="round" opacity="0.6"/>
          </svg>
        </div>
        <h1 class="logo-title">IT ASSET MANAGER</h1>
        <p class="logo-subtitle">Infrastructure Control Center</p>
      </div>

      <!-- 分隔线 -->
      <div class="divider">
        <span class="divider-text">SECURE ACCESS</span>
      </div>

      <!-- 登录表单 -->
      <el-form ref="formRef" :model="form" :rules="rules" class="login-form" @submit.prevent="handleLogin">
        <el-form-item prop="username">
          <div class="input-wrapper">
            <span class="input-icon">
              <el-icon><User /></el-icon>
            </span>
            <el-input
              v-model="form.username"
              placeholder="用户名"
              size="large"
              :prefix-icon="null"
              class="custom-input"
              @keyup.enter="handleLogin"
            />
            <span class="input-line"></span>
          </div>
        </el-form-item>

        <el-form-item prop="password">
          <div class="input-wrapper">
            <span class="input-icon">
              <el-icon><Lock /></el-icon>
            </span>
            <el-input
              v-model="form.password"
              type="password"
              placeholder="密码"
              size="large"
              show-password
              class="custom-input"
              @keyup.enter="handleLogin"
            />
            <span class="input-line"></span>
          </div>
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            class="login-button"
            @click="handleLogin"
          >
            <span class="btn-text">{{ loading ? '认证中...' : '系统登录' }}</span>
            <span class="btn-arrow" v-if="!loading">→</span>
          </el-button>
        </el-form-item>
      </el-form>

      <!-- 底部状态 -->
      <div class="status-bar">
        <span class="status-item">
          <span class="status-dot online"></span>
          系统在线
        </span>
        <span class="status-item">
          <span class="status-dot"></span>
          v1.0.0
        </span>
      </div>
    </div>

    <!-- 底部版权 -->
    <div class="footer">
      <p>© 2024 IT Asset Management Platform</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const getParticleStyle = (index) => {
  const left = Math.random() * 100
  const delay = Math.random() * 20
  const duration = 15 + Math.random() * 10
  const size = 2 + Math.random() * 4
  return {
    left: `${left}%`,
    animationDelay: `${delay}s`,
    animationDuration: `${duration}s`,
    width: `${size}px`,
    height: `${size}px`
  }
}

const handleLogin = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      await authStore.login(form.username, form.password)
      // 确保 token 已存入 localStorage
      await new Promise(resolve => setTimeout(resolve, 100))

      // 验证 token 已存储
      const storedToken = localStorage.getItem('token')
      if (!storedToken) {
        throw new Error('Token 存储失败')
      }

      ElMessage.success('登录成功')
      const redirect = route.query.redirect || '/assets'
      // 使用 replace 并等待导航完成
      await router.replace(redirect)
    } catch (error) {
      ElMessage.error(error.message || '登录失败')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style lang="scss" scoped>
// 引入科技感字体
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700&family=JetBrains+Mono:wght@400;500&display=swap');

.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  background: linear-gradient(135deg, #0a0e17 0%, #1a1f2e 50%, #0d1117 100%);
}

// 网格背景
.grid-background {
  position: absolute;
  inset: 0;
  overflow: hidden;

  .grid-lines {
    position: absolute;
    inset: 0;
    background-image:
      linear-gradient(rgba(0, 212, 255, 0.03) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0, 212, 255, 0.03) 1px, transparent 1px);
    background-size: 50px 50px;
    animation: gridMove 20s linear infinite;
  }

  .glow-orb {
    position: absolute;
    border-radius: 50%;
    filter: blur(80px);
    opacity: 0.4;

    &.orb-1 {
      width: 400px;
      height: 400px;
      background: radial-gradient(circle, rgba(0, 212, 255, 0.3) 0%, transparent 70%);
      top: -100px;
      right: -100px;
      animation: float 8s ease-in-out infinite;
    }

    &.orb-2 {
      width: 300px;
      height: 300px;
      background: radial-gradient(circle, rgba(99, 102, 241, 0.3) 0%, transparent 70%);
      bottom: -50px;
      left: -50px;
      animation: float 10s ease-in-out infinite reverse;
    }
  }
}

@keyframes gridMove {
  0% { transform: translate(0, 0); }
  100% { transform: translate(50px, 50px); }
}

@keyframes float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  50% { transform: translate(30px, -30px) scale(1.1); }
}

// 数据粒子
.data-particles {
  position: absolute;
  inset: 0;
  pointer-events: none;

  .particle {
    position: absolute;
    bottom: -20px;
    background: rgba(0, 212, 255, 0.6);
    border-radius: 50%;
    animation: rise linear infinite;
    box-shadow: 0 0 6px rgba(0, 212, 255, 0.8);
  }
}

@keyframes rise {
  0% {
    transform: translateY(0) scale(1);
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  90% {
    opacity: 1;
  }
  100% {
    transform: translateY(-100vh) scale(0.5);
    opacity: 0;
  }
}

// 登录卡片
.login-card {
  position: relative;
  width: 420px;
  padding: 48px 40px 40px;
  background: rgba(15, 20, 30, 0.8);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(0, 212, 255, 0.1);
  border-radius: 16px;
  box-shadow:
    0 0 0 1px rgba(0, 212, 255, 0.05),
    0 20px 50px rgba(0, 0, 0, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.05);
  z-index: 10;

  .card-top-line {
    position: absolute;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 60%;
    height: 2px;
    background: linear-gradient(90deg, transparent, #00d4ff, transparent);
    border-radius: 2px;
  }
}

// Logo区域
.logo-section {
  text-align: center;
  margin-bottom: 32px;

  .logo-icon {
    width: 64px;
    height: 64px;
    margin: 0 auto 16px;
    color: #00d4ff;
    animation: pulse 3s ease-in-out infinite;

    svg {
      width: 100%;
      height: 100%;
    }
  }

  .logo-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 22px;
    font-weight: 700;
    letter-spacing: 4px;
    color: #fff;
    margin: 0 0 8px;
    text-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
  }

  .logo-subtitle {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    letter-spacing: 3px;
    color: rgba(0, 212, 255, 0.6);
    margin: 0;
    text-transform: uppercase;
  }
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.8; transform: scale(1.02); }
}

// 分隔线
.divider {
  display: flex;
  align-items: center;
  margin-bottom: 32px;

  &::before,
  &::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0, 212, 255, 0.2), transparent);
  }

  .divider-text {
    padding: 0 16px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 10px;
    letter-spacing: 2px;
    color: rgba(255, 255, 255, 0.3);
  }
}

// 表单
.login-form {
  :deep(.el-form-item) {
    margin-bottom: 24px;
  }

  :deep(.el-form-item__error) {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    padding-top: 6px;
  }
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;

  .input-icon {
    position: absolute;
    left: 16px;
    z-index: 2;
    color: rgba(0, 212, 255, 0.5);
    font-size: 18px;
    transition: color 0.3s;
  }

  .custom-input {
    :deep(.el-input__wrapper) {
      background: rgba(0, 20, 40, 0.5);
      border: 1px solid rgba(0, 212, 255, 0.15);
      border-radius: 8px;
      padding: 4px 16px 4px 48px;
      box-shadow: none;
      transition: all 0.3s;

      &:hover {
        border-color: rgba(0, 212, 255, 0.3);
      }

      &.is-focus {
        border-color: rgba(0, 212, 255, 0.5);
        box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.1);
      }
    }

    :deep(.el-input__inner) {
      font-family: 'JetBrains Mono', monospace;
      font-size: 14px;
      color: #fff;
      height: 48px;

      &::placeholder {
        color: rgba(255, 255, 255, 0.3);
      }
    }

    :deep(.el-input__suffix) {
      color: rgba(255, 255, 255, 0.3);
    }
  }

  &:focus-within .input-icon {
    color: #00d4ff;
  }

  .input-line {
    position: absolute;
    bottom: 0;
    left: 50%;
    width: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #00d4ff, transparent);
    transition: all 0.3s;
    transform: translateX(-50%);
  }

  &:focus-within .input-line {
    width: 80%;
  }
}

// 登录按钮
.login-button {
  width: 100%;
  height: 52px;
  font-family: 'Orbitron', sans-serif;
  font-size: 14px;
  font-weight: 500;
  letter-spacing: 2px;
  background: linear-gradient(135deg, #00d4ff 0%, #0099cc 100%);
  border: none;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s;
  position: relative;
  overflow: hidden;

  &::before {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, transparent 50%);
  }

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 30px rgba(0, 212, 255, 0.3);
  }

  &:active {
    transform: translateY(0);
  }

  .btn-text {
    position: relative;
  }

  .btn-arrow {
    font-size: 18px;
    transition: transform 0.3s;
  }

  &:hover .btn-arrow {
    transform: translateX(4px);
  }
}

// 状态栏
.status-bar {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);

  .status-item {
    display: flex;
    align-items: center;
    gap: 6px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: rgba(255, 255, 255, 0.4);
  }

  .status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: rgba(255, 255, 255, 0.3);

    &.online {
      background: #00d4ff;
      box-shadow: 0 0 8px rgba(0, 212, 255, 0.6);
      animation: blink 2s infinite;
    }
  }
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

// 页脚
.footer {
  position: absolute;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.2);
}
</style>
