<template>
  <div class="login-page">
    <div class="login-card">
      <!-- 左侧插画区域 -->
      <div class="illustration-section">
        <div class="characters-container">
          <AnimatedCharacters
            :is-typing="isTyping"
            :show-password="showPassword"
            :password-length="loginForm.password.length"
            :login-failed="loginFailed"
            :login-success="loginSuccess"
          />
        </div>
      </div>
      
      <!-- 右侧表单区域 -->
      <div class="form-section">
        <div class="form-content">
          <!-- Logo -->
          <div class="logo-wrapper">
            <div class="logo-text">药药记</div>
          </div>
          
          <!-- 登录/注册切换 -->
          <div class="tab-switcher">
            <button 
              :class="['tab-btn', { active: activeTab === 'login' }]" 
              @click="activeTab = 'login'"
            >登录</button>
            <button 
              :class="['tab-btn', { active: activeTab === 'register' }]" 
              @click="activeTab = 'register'"
            >注册</button>
          </div>
          
          <!-- 登录表单 -->
          <el-form 
            v-show="activeTab === 'login'" 
            :model="loginForm" 
            :rules="loginRules" 
            ref="loginFormRef" 
            class="auth-form"
          >
            <div class="form-group">
              <label class="form-label">用户名</label>
              <el-form-item prop="username">
                <el-input 
                  v-model="loginForm.username" 
                  placeholder="请输入用户名"
                  size="large"
                  class="form-input"
                  autocomplete="username"
                />
              </el-form-item>
            </div>
            
            <div class="form-group">
              <label class="form-label">密码</label>
              <el-form-item prop="password">
                <el-input
                  v-model="loginForm.password"
                  :type="showPassword ? 'text' : 'password'"
                  placeholder="请输入密码"
                  size="large"
                  class="form-input"
                  autocomplete="current-password"
                  @keyup.enter="handleLogin"
                >
                  <template #suffix>
                    <span class="password-toggle" @click="showPassword = !showPassword">
                      <el-icon v-if="showPassword"><View /></el-icon>
                      <el-icon v-else><Hide /></el-icon>
                    </span>
                  </template>
                </el-input>
              </el-form-item>
            </div>
            
            <div class="form-group">
              <label class="form-label">验证码</label>
              <el-form-item prop="captchaCode">
                <div class="captcha-row">
                  <el-input
                    v-model="loginForm.captchaCode"
                    placeholder="请输入验证码"
                    size="large"
                    class="form-input"
                    maxlength="4"
                    @keyup.enter="handleLogin"
                  />
                  <img
                    :src="loginCaptchaUrl"
                    alt="验证码"
                    class="captcha-img"
                    title="点击刷新"
                    @click="refreshLoginCaptcha"
                  />
                </div>
              </el-form-item>
            </div>
            
            <div class="form-options">
              <span></span>
              <a href="#" class="forgot-link">忘记密码?</a>
            </div>
            
            <el-button 
              type="primary" 
              :loading="loading" 
              @click="handleLogin" 
              size="large"
              class="submit-btn"
            >
              {{ loading ? '登录中...' : '登录' }}
            </el-button>
          </el-form>
          
          <!-- 注册表单 -->
          <el-form 
            v-show="activeTab === 'register'" 
            :model="registerForm" 
            :rules="registerRules" 
            ref="registerFormRef" 
            class="auth-form"
          >
            <div class="form-group">
              <label class="form-label">用户名</label>
              <el-form-item prop="username">
                <el-input 
                  v-model="registerForm.username" 
                  placeholder="请输入用户名"
                  size="large"
                  class="form-input"
                  maxlength="50"
                />
              </el-form-item>
            </div>
            
            <div class="form-group">
              <label class="form-label">邮箱 (可选)</label>
              <el-form-item prop="email">
                <el-input 
                  v-model="registerForm.email" 
                  placeholder="请输入邮箱"
                  size="large"
                  class="form-input"
                />
              </el-form-item>
            </div>
            
            <div class="form-group">
              <label class="form-label">密码</label>
              <el-form-item prop="password">
                <el-input 
                  v-model="registerForm.password" 
                  type="password"
                  placeholder="请输入密码"
                  size="large"
                  class="form-input"
                />
              </el-form-item>
            </div>
            
            <div class="form-group">
              <label class="form-label">确认密码</label>
              <el-form-item prop="confirmPassword">
                <el-input 
                  v-model="registerForm.confirmPassword" 
                  type="password"
                  placeholder="请再次输入密码"
                  size="large"
                  class="form-input"
                />
              </el-form-item>
            </div>
            
            <div class="form-group">
              <label class="form-label">验证码</label>
              <el-form-item prop="captchaCode">
                <div class="captcha-row">
                  <el-input
                    v-model="registerForm.captchaCode"
                    placeholder="请输入验证码"
                    size="large"
                    class="form-input"
                    maxlength="4"
                  />
                  <img
                    :src="registerCaptchaUrl"
                    alt="验证码"
                    class="captcha-img"
                    title="点击刷新"
                    @click="refreshRegisterCaptcha"
                  />
                </div>
              </el-form-item>
            </div>
            
            <el-button 
              type="primary" 
              :loading="loading" 
              @click="handleRegister" 
              size="large"
              class="submit-btn"
            >
              {{ loading ? '注册中...' : '注册' }}
            </el-button>
          </el-form>
          
          <!-- 底部提示 -->
          <div class="form-footer">
            <span v-if="activeTab === 'login'">
              还没有账号? <a @click="activeTab = 'register'">立即注册</a>
            </span>
            <span v-else>
              已有账号? <a @click="activeTab = 'login'">立即登录</a>
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { View, Hide } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { authAPI } from '@/api'
import AnimatedCharacters from '@/components/login/AnimatedCharacters.vue'

const router = useRouter()
const userStore = useUserStore()

const activeTab = ref('login')
const loading = ref(false)
const loginFormRef = ref()
const registerFormRef = ref()

// 动画相关状态
const isTyping = ref(false)
const showPassword = ref(false)
const loginFailed = ref(false)
const loginSuccess = ref(false)
let typingTimeout: ReturnType<typeof setTimeout> | null = null

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

// 监听密码输入
watch(() => loginForm.password, () => {
  isTyping.value = true
  if (typingTimeout) clearTimeout(typingTimeout)
  typingTimeout = setTimeout(() => { isTyping.value = false }, 300)
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
      loginFailed.value = false
      loginSuccess.value = false
      try {
        await userStore.login(loginForm.username, loginForm.password, loginCaptchaId.value, loginForm.captchaCode)
        loginSuccess.value = true
        ElMessage.success('登录成功')
        setTimeout(() => { router.push('/') }, 1500)
      } catch (error: any) {
        refreshLoginCaptcha()
        loginForm.captchaCode = ''
        loginFailed.value = true
        
        if (error.response?.status === 400 && error.response?.data?.detail?.includes('验证码')) {
          ElMessage.warning(error.response.data.detail)
        } else if (error.response?.status === 403) {
          ElMessage({ type: 'error', message: error.response?.data?.detail || '该账号已被禁用', duration: 5000 })
        } else if (error.response?.status === 401 || error.response?.data?.detail?.includes('Incorrect')) {
          ElMessage({ type: 'warning', message: '用户名或密码错误', duration: 3000 })
        } else if (error.response?.status === 404 || error.response?.data?.detail?.includes('not found')) {
          ElMessage({ type: 'info', message: '该用户不存在，请先注册', duration: 3000 })
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
        refreshRegisterCaptcha()
        registerForm.captchaCode = ''
        ElMessage.error(error.response?.data?.detail || '注册失败，请稍后重试')
      } finally {
        loading.value = false
      }
    }
  })
}

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
.login-page {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #1a1a2e;
}

.login-card {
  display: flex;
  width: 100%;
  height: 100%;
  background: #ffffff;
  overflow: hidden;
}

/* 左侧插画区域 */
.illustration-section {
  flex: 1;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  position: relative;
  overflow: hidden;
}

.characters-container {
  transform: scale(1.2);
}

/* 右侧表单区域 */
.form-section {
  flex: 1;
  background: #ffffff;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.form-content {
  width: 100%;
  max-width: 360px;
}

/* Logo */
.logo-wrapper {
  display: flex;
  justify-content: center;
  margin-bottom: 24px;
}

.logo-text {
  font-size: 32px;
  font-weight: 700;
  color: #1a1a2e;
  letter-spacing: 4px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Tab 切换 */
.tab-switcher {
  display: flex;
  background: #f3f4f6;
  border-radius: 12px;
  padding: 4px;
  margin-bottom: 24px;
}

.tab-btn {
  flex: 1;
  padding: 10px 20px;
  border: none;
  background: transparent;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn.active {
  background: #ffffff;
  color: #1a1a2e;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

/* 表单样式 */
.auth-form {
  margin-bottom: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 8px;
}

.form-input :deep(.el-input__wrapper) {
  border-radius: 10px;
  box-shadow: none;
  border: 1px solid #e5e7eb;
  padding: 4px 15px;
  transition: all 0.2s;
}

.form-input :deep(.el-input__wrapper:hover) {
  border-color: #d1d5db;
}

.form-input :deep(.el-input__wrapper.is-focus) {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-input :deep(.el-input__inner) {
  font-size: 14px;
}

.captcha-row {
  display: flex;
  gap: 12px;
  align-items: center;
}

.captcha-row .form-input {
  flex: 1;
}

.captcha-img {
  height: 40px;
  border-radius: 8px;
  cursor: pointer;
  border: 1px solid #e5e7eb;
  transition: opacity 0.2s;
}

.captcha-img:hover {
  opacity: 0.8;
}

.password-toggle {
  cursor: pointer;
  display: flex;
  align-items: center;
  color: #9ca3af;
  transition: color 0.2s;
}

.password-toggle:hover {
  color: #667eea;
}

/* 表单选项 */
.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  font-size: 14px;
}

.forgot-link {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

.forgot-link:hover {
  text-decoration: underline;
}

/* 提交按钮 */
.submit-btn {
  width: 100%;
  height: 48px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  background: #1a1a2e;
  border: none;
  transition: all 0.2s;
}

.submit-btn:hover {
  background: #2d2d44;
  transform: translateY(-1px);
}

/* 底部提示 */
.form-footer {
  text-align: center;
  font-size: 14px;
  color: #6b7280;
}

.form-footer a {
  color: #667eea;
  font-weight: 500;
  cursor: pointer;
  text-decoration: none;
}

.form-footer a:hover {
  text-decoration: underline;
}

/* 响应式 */
@media (max-width: 768px) {
  .login-card {
    flex-direction: column;
  }
  
  .illustration-section {
    min-height: 180px;
    flex: none;
  }
  
  .characters-container {
    transform: scale(0.7);
  }
  
  .form-section {
    padding: 30px;
    flex: 1;
    display: flex;
    align-items: flex-start;
    justify-content: center;
    overflow-y: auto;
  }
  
  .form-content {
    max-width: 100%;
  }
}
</style>
