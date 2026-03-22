<template>
  <div class="admin-login-container">
    <div class="bg-decoration">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
    </div>

    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <div class="logo-circle">
            <el-icon :size="32"><Setting /></el-icon>
          </div>
          <h2 class="system-title">管理员后台</h2>
          <p class="welcome-text">药药记 · 智能用药安全管理系统</p>
        </div>
      </template>

      <el-form :model="loginForm" :rules="loginRules" ref="loginFormRef" class="auth-form">
        <el-form-item prop="username">
          <el-input 
            v-model="loginForm.username" 
            placeholder="请输入管理员账号" 
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
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-form-item>
          <el-button 
            type="primary" 
            :loading="loading" 
            @click="handleLogin" 
            size="large"
            class="submit-btn"
          >
            {{ loading ? '登录中...' : '登录管理后台' }}
          </el-button>
        </el-form-item>
      </el-form>

      <div class="back-link">
        <router-link to="/login">← 返回用户登录</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { Setting } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const loginFormRef = ref()

const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules = {
  username: [{ required: true, message: '请输入管理员账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

async function handleLogin() {
  await loginFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      loading.value = true
      try {
        await userStore.adminLogin(loginForm.username, loginForm.password)
        
        // 调试：打印用户信息
        console.log('登录后用户信息:', userStore.adminUser)
        
        // 检查是否是管理员
        if (!userStore.adminUser?.is_admin) {
          ElMessage.error('您没有管理员权限')
          userStore.adminLogout()
          return
        }
        
        ElMessage.success('登录成功')
        router.push('/admin/dashboard')
      } catch (error: any) {
        console.error('登录错误:', error)
        const errorMsg = error.response?.data?.detail || '登录失败，请检查账号密码'
        ElMessage.error(errorMsg)
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.admin-login-container {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100vw;
  min-height: 100vh;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  overflow: hidden;
}

.bg-decoration {
  position: absolute;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.05);
}

.circle-1 {
  width: 400px;
  height: 400px;
  top: -150px;
  right: -150px;
}

.circle-2 {
  width: 300px;
  height: 300px;
  bottom: -100px;
  left: -100px;
}

.login-card {
  width: 90%;
  max-width: 420px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.login-card :deep(.el-card__header) {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-bottom: none;
  padding: 30px 20px;
}

.card-header {
  text-align: center;
  color: white;
}

.logo-circle {
  width: 64px;
  height: 64px;
  margin: 0 auto 16px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.system-title {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
}

.welcome-text {
  margin: 0;
  font-size: 14px;
  opacity: 0.8;
}

.auth-form {
  padding: 20px;
}

.auth-form :deep(.el-input__wrapper) {
  border-radius: 8px;
  padding: 10px 15px;
}

.submit-btn {
  width: 100%;
  height: 44px;
  border-radius: 8px;
  font-size: 16px;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border: none;
}

.submit-btn:hover {
  opacity: 0.9;
}

.back-link {
  text-align: center;
  padding-bottom: 20px;
}

.back-link a {
  color: #909399;
  text-decoration: none;
  font-size: 14px;
}

.back-link a:hover {
  color: #1a1a2e;
}
</style>
