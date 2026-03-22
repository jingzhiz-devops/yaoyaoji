<template>
  <div class="login-container">
    <!-- 背景装饰元素 -->
    <div class="bg-decoration">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
      <div class="circle circle-3"></div>
      <div class="wave wave-1"></div>
      <div class="wave wave-2"></div>
    </div>

    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <div class="logo-container">
            <div class="logo-circle">
              <span class="logo-text">药药记</span>
            </div>
          </div>
          <h2 class="system-title">智能用药安全管理系统</h2>
          <p class="welcome-text">守护您的每一份健康</p>
        </div>
      </template>

      <el-tabs v-model="activeTab" class="login-tabs">
        <el-tab-pane label="登录" name="login">
          <el-form :model="loginForm" :rules="loginRules" ref="loginFormRef" class="auth-form">
            <el-form-item prop="username">
              <el-input 
                v-model="loginForm.username" 
                placeholder="请输入用户名" 
                prefix-icon="User"
                size="large"
              />
            </el-form-item>
            <el-form-item prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="请输入密码"
                prefix-icon="Lock"
                size="large"
                @keyup.enter="handleLogin"
              />
            </el-form-item>
            <el-form-item prop="captchaCode">
              <div style="display: flex; gap: 12px; width: 100%;">
                <el-input
                  v-model="loginForm.captchaCode"
                  placeholder="请输入验证码"
                  prefix-icon="Key"
                  size="large"
                  style="flex: 1;"
                  maxlength="4"
                  @keyup.enter="handleLogin"
                />
                <img
                  :src="loginCaptchaUrl"
                  alt="验证码"
                  style="height: 40px; border-radius: 8px; cursor: pointer; border: 1px solid #dcdfe6;"
                  title="点击刷新验证码"
                  @click="refreshLoginCaptcha"
                />
              </div>
            </el-form-item>
            <el-form-item>
              <el-button 
                type="primary" 
                :loading="loading" 
                @click="handleLogin" 
                size="large"
                class="submit-btn"
              >
                <span v-if="!loading">立即登录</span>
                <span v-else>登录中...</span>
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="注册" name="register">
          <el-form :model="registerForm" :rules="registerRules" ref="registerFormRef" class="auth-form">
            <el-form-item prop="username">
              <el-input 
                v-model="registerForm.username" 
                placeholder="请输入用户名（支持中文，至少2个字符）" 
                prefix-icon="User"
                size="large"
                maxlength="50"
                show-word-limit
              />
            </el-form-item>
            <el-form-item prop="email">
              <el-input 
                v-model="registerForm.email" 
                placeholder="邮箱（可选）" 
                prefix-icon="Message"
                size="large"
              />
            </el-form-item>
            <el-form-item prop="password">
              <el-input 
                v-model="registerForm.password" 
                type="password" 
                placeholder="请输入密码" 
                prefix-icon="Lock"
                size="large"
              />
            </el-form-item>
            <el-form-item prop="confirmPassword">
              <el-input 
                v-model="registerForm.confirmPassword" 
                type="password" 
                placeholder="确认密码" 
                prefix-icon="Lock"
                size="large"
              />
            </el-form-item>
            <el-form-item prop="captchaCode">
              <div style="display: flex; gap: 12px; width: 100%;">
                <el-input
                  v-model="registerForm.captchaCode"
                  placeholder="请输入验证码"
                  prefix-icon="Key"
                  size="large"
                  style="flex: 1;"
                  maxlength="4"
                />
                <img
                  :src="registerCaptchaUrl"
                  alt="验证码"
                  style="height: 40px; border-radius: 8px; cursor: pointer; border: 1px solid #dcdfe6;"
                  title="点击刷新验证码"
                  @click="refreshRegisterCaptcha"
                />
              </div>
            </el-form-item>
            <el-form-item>
              <el-button 
                type="success" 
                :loading="loading" 
                @click="handleRegister" 
                size="large"
                class="submit-btn"
              >
                <span v-if="!loading">立即注册</span>
                <span v-else>注册中...</span>
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 底部信息 -->
    <div class="footer-info">
      <p>© 2025 药药记 · 让用药更安全</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { authAPI } from '@/api'
import { User, Lock, Message, Key } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const activeTab = ref('login')
const loading = ref(false)
const loginFormRef = ref()
const registerFormRef = ref()

// 验证码状态
const loginCaptchaId = ref('')
const loginCaptchaUrl = ref('')
const registerCaptchaId = ref('')
const registerCaptchaUrl = ref('')

const loginForm = reactive({
  username: '',
  password: '',
  captchaCode: ''
})

const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  captchaCode: ''
})

const loginRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  captchaCode: [{ required: true, message: '请输入验证码', trigger: 'blur' }]
}

const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, message: '用户名至少2个字符', trigger: 'blur' },
    { 
      pattern: /^[\u4e00-\u9fa5a-zA-Z0-9_]+$/, 
      message: '用户名只能包含中文、英文、数字和下划线', 
      trigger: 'blur' 
    }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    {
      validator: (rule: any, value: string, callback: any) => {
        if (value !== registerForm.password) {
          callback(new Error('两次输入密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ],
  captchaCode: [{ required: true, message: '请输入验证码', trigger: 'blur' }]
}

async function handleLogin() {
  await loginFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      loading.value = true
      try {
        await userStore.login(loginForm.username, loginForm.password, loginCaptchaId.value, loginForm.captchaCode)
        ElMessage.success('登录成功')
        router.push('/')
      } catch (error: any) {
        // 登录失败后刷新验证码
        refreshLoginCaptcha()
        loginForm.captchaCode = ''

        // 检查是否是验证码错误
        if (error.response?.status === 400 && error.response?.data?.detail?.includes('验证码')) {
          ElMessage.warning(error.response.data.detail)
        // 检查是否是账号被禁用
        } else if (error.response?.status === 403) {
          ElMessage({
            type: 'error',
            message: error.response?.data?.detail || '该账号已被禁用，请联系管理员',
            duration: 5000,
            showClose: true
          })
        // 检查是否是用户不存在的错误
        } else if (error.response?.status === 401 || error.response?.data?.detail?.includes('Incorrect')) {
          ElMessage({
            type: 'warning',
            message: '用户名或密码错误',
            duration: 3000
          })
        } else if (error.response?.status === 404 || error.response?.data?.detail?.includes('not found')) {
          ElMessage({
            type: 'info',
            message: '该用户不存在，请先注册',
            duration: 3000,
            showClose: true
          })
          // 自动切换到注册标签页
          setTimeout(() => {
            activeTab.value = 'register'
            registerForm.username = loginForm.username
          }, 1500)
        } else {
          ElMessage.error('登录失败，请稍后重试')
        }
      } finally {
        loading.value = false
      }
    }
  })
}

async function handleRegister() {
  await registerFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      loading.value = true
      try {
        await userStore.register({
          username: registerForm.username,
          password: registerForm.password,
          email: registerForm.email || undefined,
          captcha_id: registerCaptchaId.value,
          captcha_code: registerForm.captchaCode
        })
        ElMessage.success('注册成功，请登录')
        activeTab.value = 'login'
        loginForm.username = registerForm.username
      } catch (error: any) {
        // 注册失败后刷新验证码
        refreshRegisterCaptcha()
        registerForm.captchaCode = ''

        const errorMsg = error.response?.data?.detail || '注册失败，请稍后重试'
        ElMessage.error(errorMsg)
      } finally {
        loading.value = false
      }
    }
  })
}

// 验证码刷新
async function refreshLoginCaptcha() {
  try {
    const { captchaId, imageUrl } = await authAPI.getCaptcha()
    loginCaptchaId.value = captchaId
    loginCaptchaUrl.value = imageUrl
  } catch {
    console.error('获取登录验证码失败')
  }
}

async function refreshRegisterCaptcha() {
  try {
    const { captchaId, imageUrl } = await authAPI.getCaptcha()
    registerCaptchaId.value = captchaId
    registerCaptchaUrl.value = imageUrl
  } catch {
    console.error('获取注册验证码失败')
  }
}

onMounted(() => {
  refreshLoginCaptcha()
  refreshRegisterCaptcha()
})
</script>

<style scoped>
.login-container {
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  width: 100vw;
  min-height: 100vh;
  background: linear-gradient(135deg, #2A9D8F 0%, #264653 100%);
  overflow: hidden;
  padding: 20px;
}

/* 背景装饰元素 */
.bg-decoration {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  pointer-events: none;
  overflow: hidden;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  animation: float 20s infinite ease-in-out;
}

.circle-1 {
  width: 300px;
  height: 300px;
  top: -100px;
  left: -100px;
  animation-delay: 0s;
}

.circle-2 {
  width: 200px;
  height: 200px;
  top: 50%;
  right: -50px;
  animation-delay: 5s;
}

.circle-3 {
  width: 150px;
  height: 150px;
  bottom: 100px;
  left: 20%;
  animation-delay: 10s;
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0) rotate(0deg);
  }
  33% {
    transform: translate(30px, -30px) rotate(120deg);
  }
  66% {
    transform: translate(-20px, 20px) rotate(240deg);
  }
}

.wave {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 100px;
  background: rgba(255, 255, 255, 0.05);
  animation: wave 15s linear infinite;
}

.wave-1 {
  animation-delay: 0s;
  opacity: 0.3;
}

.wave-2 {
  animation-delay: 5s;
  opacity: 0.2;
}

@keyframes wave {
  0% {
    transform: translateX(0) translateZ(0) scaleY(1);
  }
  50% {
    transform: translateX(-25%) translateZ(0) scaleY(0.8);
  }
  100% {
    transform: translateX(-50%) translateZ(0) scaleY(1);
  }
}

/* 登录卡片 */
.login-card {
  position: relative;
  width: 90%;
  max-width: 480px;
  border-radius: 24px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(20px);
  background: rgba(255, 255, 255, 0.95);
  animation: slideIn 0.6s ease-out;
  overflow: hidden;
  z-index: 1;
  border: none;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.login-card :deep(.el-card__header) {
  background: linear-gradient(135deg, rgba(42, 157, 143, 0.1) 0%, rgba(38, 70, 83, 0.1) 100%);
  border-bottom: none;
  padding: 30px 20px 20px;
}

.card-header {
  text-align: center;
}

.logo-container {
  margin-bottom: 20px;
}

.logo-circle {
  width: 80px;
  height: 80px;
  margin: 0 auto;
  background: linear-gradient(135deg, #2A9D8F 0%, #264653 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 24px rgba(42, 157, 143, 0.4);
  animation: pulse 3s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
    box-shadow: 0 8px 24px rgba(42, 157, 143, 0.4);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 8px 32px rgba(42, 157, 143, 0.6);
  }
}

.logo-text {
  color: white;
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 1px;
}

.system-title {
  margin: 0 0 8px 0;
  background: linear-gradient(135deg, #2A9D8F 0%, #264653 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  font-size: 24px;
  font-weight: 700;
}

.welcome-text {
  margin: 0;
  font-size: 14px;
  color: #909399;
  font-weight: 400;
}

/* 标签页 */
.login-tabs {
  padding: 0 20px;
}

.login-tabs :deep(.el-tabs__nav-wrap::after) {
  display: none;
}

.login-tabs :deep(.el-tabs__active-bar) {
  background: #2A9D8F;
  height: 3px;
}

.login-tabs :deep(.el-tabs__item) {
  font-size: 16px;
  font-weight: 500;
  color: #909399;
}

.login-tabs :deep(.el-tabs__item.is-active) {
  color: #2A9D8F;
  font-weight: 600;
}

/* 表单样式 */
.auth-form {
  padding: 20px 0;
}

.auth-form :deep(.el-input__wrapper) {
  border-radius: 12px;
  padding: 12px 15px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.auth-form :deep(.el-input__wrapper:hover) {
  box-shadow: 0 4px 12px rgba(42, 157, 143, 0.15);
}

.auth-form :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 4px 16px rgba(42, 157, 143, 0.25);
}

/* 提交按钮 */
.submit-btn {
  width: 100%;
  height: 48px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: 1px;
  background: linear-gradient(135deg, #2A9D8F 0%, #264653 100%);
  border: none;
  transition: all 0.3s ease;
  margin-top: 10px;
}

.submit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(42, 157, 143, 0.4);
}

.submit-btn:active {
  transform: translateY(0);
}

/* 成功按钮 */
.el-button--success.submit-btn {
  background: linear-gradient(135deg, #E76F51 0%, #F4A261 100%);
}

.el-button--success.submit-btn:hover {
  box-shadow: 0 8px 24px rgba(231, 111, 81, 0.4);
}

/* 底部信息 */
.footer-info {
  position: absolute;
  bottom: 20px;
  text-align: center;
  color: rgba(255, 255, 255, 0.8);
  font-size: 14px;
  z-index: 1;
}

.footer-info p {
  margin: 0;
  letter-spacing: 0.5px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .login-card {
    width: 95%;
    max-width: none;
  }

  .circle-1,
  .circle-2,
  .circle-3 {
    opacity: 0.5;
  }

  .system-title {
    font-size: 20px;
  }

  .logo-circle {
    width: 60px;
    height: 60px;
  }

  .logo-text {
    font-size: 16px;
  }
}

@media (max-width: 480px) {
  .login-tabs {
    padding: 0 10px;
  }

  .auth-form {
    padding: 10px 0;
  }

  .footer-info {
    font-size: 12px;
  }
}
</style>
