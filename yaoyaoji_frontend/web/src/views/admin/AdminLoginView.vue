<template>
  <div class="admin-login-container">
    <!-- 动态背景 -->
    <div class="bg-layer">
      <div class="gradient-orb orb-1"></div>
      <div class="gradient-orb orb-2"></div>
      <div class="gradient-orb orb-3"></div>
      <div class="grid-overlay"></div>
      <div class="particles">
        <span v-for="n in 20" :key="n" class="particle" :style="particleStyle(n)"></span>
      </div>
    </div>

    <!-- 登录卡片 -->
    <div class="login-wrapper">
      <div class="login-card">
        <!-- 顶部光效线 -->
        <div class="glow-line"></div>
        
        <div class="card-header">
          <div class="logo-icon">
            <svg viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg">
              <circle cx="24" cy="24" r="20" stroke="url(#logoGrad)" stroke-width="2" fill="none"/>
              <path d="M24 12 L24 36 M16 24 L32 24" stroke="url(#logoGrad)" stroke-width="2.5" stroke-linecap="round"/>
              <circle cx="24" cy="24" r="8" stroke="url(#logoGrad)" stroke-width="1.5" fill="none" opacity="0.5"/>
              <defs>
                <linearGradient id="logoGrad" x1="0" y1="0" x2="48" y2="48">
                  <stop offset="0%" stop-color="#60a5fa"/>
                  <stop offset="100%" stop-color="#a78bfa"/>
                </linearGradient>
              </defs>
            </svg>
          </div>
          <h1 class="title">管理员后台</h1>
          <p class="subtitle">药药记 · 智能用药安全管理系统</p>
        </div>

        <el-form :model="loginForm" :rules="loginRules" ref="loginFormRef" class="login-form">
          <el-form-item prop="username">
            <div class="input-wrapper">
              <el-icon class="input-icon"><User /></el-icon>
              <input
                v-model="loginForm.username"
                type="text"
                placeholder="请输入管理员账号"
                class="sci-input"
                autocomplete="username"
              />
            </div>
          </el-form-item>
          <el-form-item prop="password">
            <div class="input-wrapper">
              <el-icon class="input-icon"><Lock /></el-icon>
              <input
                v-model="loginForm.password"
                :type="showPassword ? 'text' : 'password'"
                placeholder="请输入密码"
                class="sci-input"
                autocomplete="current-password"
                @keyup.enter="handleLogin"
              />
              <el-icon class="toggle-pwd" @click="showPassword = !showPassword">
                <View v-if="showPassword" />
                <Hide v-else />
              </el-icon>
            </div>
          </el-form-item>
          <el-form-item prop="captchaCode">
            <div class="captcha-row">
              <div class="input-wrapper" style="flex: 1;">
                <el-icon class="input-icon"><Key /></el-icon>
                <input
                  v-model="loginForm.captchaCode"
                  type="text"
                  placeholder="请输入验证码"
                  class="sci-input"
                  maxlength="4"
                  @keyup.enter="handleLogin"
                />
              </div>
              <img
                :src="captchaUrl"
                alt="验证码"
                class="captcha-img"
                title="点击刷新验证码"
                @click="refreshCaptcha"
              />
            </div>
          </el-form-item>

          <button
            type="button"
            class="login-btn"
            :class="{ loading }"
            :disabled="loading"
            @click="handleLogin"
          >
            <span class="btn-glow"></span>
            <span class="btn-text">{{ loading ? '验证中...' : '进入系统' }}</span>
            <svg v-if="!loading" class="btn-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
            <span v-if="loading" class="btn-spinner"></span>
          </button>
        </el-form>

        <div class="back-link">
          <router-link to="/login">
            <el-icon><ArrowLeft /></el-icon>
            返回用户登录
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { authAPI } from '@/api'
import { User, Lock, View, Hide, ArrowLeft, Key } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const showPassword = ref(false)
const loginFormRef = ref()

const captchaId = ref('')
const captchaUrl = ref('')

const loginForm = reactive({
  username: '',
  password: '',
  captchaCode: ''
})

const loginRules = {
  username: [{ required: true, message: '请输入管理员账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  captchaCode: [{ required: true, message: '请输入验证码', trigger: 'blur' }]
}

function particleStyle(n: number) {
  const size = Math.random() * 3 + 1
  return {
    width: `${size}px`,
    height: `${size}px`,
    left: `${Math.random() * 100}%`,
    top: `${Math.random() * 100}%`,
    animationDelay: `${Math.random() * 6}s`,
    animationDuration: `${Math.random() * 4 + 3}s`
  }
}

async function handleLogin() {
  await loginFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      loading.value = true
      try {
        await userStore.adminLogin(loginForm.username, loginForm.password, captchaId.value, loginForm.captchaCode)
        
        if (!userStore.adminUser?.is_admin) {
          ElMessage.error('您没有管理员权限')
          userStore.adminLogout()
          return
        }
        
        ElMessage.success('登录成功')
        router.push('/admin/dashboard')
      } catch (error: any) {
        // 登录失败后刷新验证码
        refreshCaptcha()
        loginForm.captchaCode = ''

        console.error('登录错误:', error)
        if (error.response?.status === 400 && error.response?.data?.detail?.includes('验证码')) {
          ElMessage.warning(error.response.data.detail)
        } else if (error.response?.status === 403) {
          ElMessage.error(error.response?.data?.detail || '该账号已被禁用，请联系管理员')
        } else {
          const errorMsg = error.response?.data?.detail || '登录失败，请检查账号密码'
          ElMessage.error(errorMsg)
        }
      } finally {
        loading.value = false
      }
    }
  })
}

async function refreshCaptcha() {
  try {
    const res = await authAPI.getCaptcha()
    captchaId.value = res.captchaId
    captchaUrl.value = res.imageUrl
  } catch {
    console.error('获取验证码失败')
  }
}

onMounted(() => {
  refreshCaptcha()
})
</script>

<style scoped>
/* ===== 全屏容器 ===== */
.admin-login-container {
  position: relative;
  width: 100vw;
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #050510;
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

/* ===== 动态背景层 ===== */
.bg-layer {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.gradient-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.4;
}

.orb-1 {
  width: 500px;
  height: 500px;
  background: radial-gradient(circle, #1e40af 0%, transparent 70%);
  top: -10%;
  left: -5%;
  animation: float1 8s ease-in-out infinite;
}

.orb-2 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, #7c3aed 0%, transparent 70%);
  bottom: -10%;
  right: -5%;
  animation: float2 10s ease-in-out infinite;
}

.orb-3 {
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, #0ea5e9 0%, transparent 70%);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation: float3 12s ease-in-out infinite;
}

/* 网格叠加 */
.grid-overlay {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px);
  background-size: 60px 60px;
}

/* 粒子 */
.particles {
  position: absolute;
  inset: 0;
}

.particle {
  position: absolute;
  background: rgba(147, 197, 253, 0.6);
  border-radius: 50%;
  animation: particleFloat 5s ease-in-out infinite;
}

@keyframes particleFloat {
  0%, 100% { opacity: 0; transform: translateY(0); }
  50% { opacity: 1; transform: translateY(-30px); }
}

@keyframes float1 {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(40px, 30px); }
}

@keyframes float2 {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(-30px, -40px); }
}

@keyframes float3 {
  0%, 100% { transform: translate(-50%, -50%) scale(1); }
  50% { transform: translate(-50%, -50%) scale(1.2); }
}

/* ===== 登录卡片 ===== */
.login-wrapper {
  position: relative;
  z-index: 10;
  width: 90%;
  max-width: 420px;
}

.login-card {
  position: relative;
  background: rgba(15, 15, 35, 0.7);
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  padding: 48px 36px 36px;
  box-shadow:
    0 0 40px rgba(59, 130, 246, 0.08),
    0 25px 50px rgba(0, 0, 0, 0.4);
  overflow: hidden;
}

/* 顶部发光线 */
.glow-line {
  position: absolute;
  top: 0;
  left: 10%;
  right: 10%;
  height: 2px;
  background: linear-gradient(90deg, transparent, #60a5fa, #a78bfa, transparent);
  border-radius: 2px;
  animation: glowPulse 3s ease-in-out infinite;
}

@keyframes glowPulse {
  0%, 100% { opacity: 0.6; }
  50% { opacity: 1; }
}

/* ===== 头部 ===== */
.card-header {
  text-align: center;
  margin-bottom: 36px;
}

.logo-icon {
  width: 56px;
  height: 56px;
  margin: 0 auto 16px;
  animation: logoSpin 20s linear infinite;
}

.logo-icon svg {
  width: 100%;
  height: 100%;
}

@keyframes logoSpin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.title {
  margin: 0 0 8px;
  font-size: 26px;
  font-weight: 700;
  background: linear-gradient(135deg, #e0e7ff, #93c5fd, #c4b5fd);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  letter-spacing: 2px;
}

.subtitle {
  margin: 0;
  font-size: 13px;
  color: rgba(148, 163, 184, 0.8);
  letter-spacing: 1px;
}

/* ===== 表单 ===== */
.login-form {
  display: flex;
  flex-direction: column;
  gap: 4px;
  width: 100%;
}

.login-form :deep(.el-form-item) {
  margin-bottom: 20px;
  width: 100%;
}

.login-form :deep(.el-form-item__content) {
  width: 100%;
}

.login-form :deep(.el-form-item__error) {
  color: #f87171;
  font-size: 12px;
  padding-top: 4px;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  width: 100%;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  transition: all 0.3s ease;
}

.input-wrapper:focus-within {
  border-color: rgba(96, 165, 250, 0.5);
  background: rgba(255, 255, 255, 0.06);
  box-shadow: 0 0 20px rgba(96, 165, 250, 0.1);
}

.input-icon {
  position: absolute;
  left: 16px;
  font-size: 18px;
  color: rgba(148, 163, 184, 0.6);
  transition: color 0.3s;
  z-index: 1;
}

.input-wrapper:focus-within .input-icon {
  color: #60a5fa;
}

.sci-input {
  width: 100%;
  padding: 14px 44px;
  background: transparent;
  border: none;
  outline: none;
  color: #e2e8f0;
  font-size: 15px;
  letter-spacing: 0.5px;
}

.sci-input::placeholder {
  color: rgba(148, 163, 184, 0.4);
}

.sci-input:-webkit-autofill {
  -webkit-box-shadow: 0 0 0 30px rgba(15, 15, 35, 0.9) inset;
  -webkit-text-fill-color: #e2e8f0;
}

.toggle-pwd {
  position: absolute;
  right: 16px;
  font-size: 18px;
  color: rgba(148, 163, 184, 0.5);
  cursor: pointer;
  transition: color 0.3s;
  z-index: 1;
}

.toggle-pwd:hover {
  color: #60a5fa;
}

/* ===== 登录按钮 ===== */
.login-btn {
  position: relative;
  width: 100%;
  padding: 15px;
  margin-top: 8px;
  background: linear-gradient(135deg, #1d4ed8, #7c3aed);
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s ease;
  letter-spacing: 1px;
}

.login-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 8px 30px rgba(29, 78, 216, 0.4);
}

.login-btn:active:not(:disabled) {
  transform: translateY(0);
}

.login-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.btn-glow {
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
  transform: translateX(-100%);
  animation: btnGlow 3s ease-in-out infinite;
}

@keyframes btnGlow {
  0% { transform: translateX(-100%); }
  50% { transform: translateX(100%); }
  100% { transform: translateX(100%); }
}

.btn-text {
  position: relative;
  z-index: 1;
}

.btn-arrow {
  width: 18px;
  height: 18px;
  position: relative;
  z-index: 1;
  transition: transform 0.3s;
}

.login-btn:hover .btn-arrow {
  transform: translateX(4px);
}

.btn-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  position: relative;
  z-index: 1;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ===== 返回链接 ===== */
.back-link {
  text-align: center;
  margin-top: 24px;
}

.back-link a {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: rgba(148, 163, 184, 0.6);
  text-decoration: none;
  font-size: 13px;
  transition: color 0.3s;
}

.back-link a:hover {
  color: #60a5fa;
}

/* ===== 响应式 ===== */
@media (max-width: 480px) {
  .login-card {
    padding: 36px 24px 28px;
    border-radius: 16px;
  }

  .title {
    font-size: 22px;
  }
}

/* ===== 验证码 ===== */
.captcha-row {
  display: flex;
  gap: 12px;
  width: 100%;
  align-items: center;
}

.captcha-img {
  height: 46px;
  border-radius: 10px;
  cursor: pointer;
  border: 1px solid rgba(255, 255, 255, 0.08);
  transition: opacity 0.3s;
  flex-shrink: 0;
}

.captcha-img:hover {
  opacity: 0.8;
}
</style>
