<template>
  <div class="user-profile-container">
    <el-card class="profile-card">
      <template #header>
        <div class="card-header">
          <h2>👤 用户信息</h2>
        </div>
      </template>

      <!-- 账号基本信息 -->
      <el-descriptions :column="2" border class="profile-info">
        <el-descriptions-item label="用户名">
          <strong>{{ userStore.user?.username }}</strong>
        </el-descriptions-item>
        <el-descriptions-item label="注册时间">
          {{ formatDate(userStore.user?.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="使用时长">
          <el-tag type="success">{{ accountAge }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="邮箱">
          {{ userStore.user?.email || '未设置' }}
        </el-descriptions-item>
      </el-descriptions>

      <el-divider />

      <!-- 账号安全设置 -->
      <div class="security-section">
        <h3>🔐 账号安全</h3>
        
        <!-- 修改用户名 -->
        <el-card class="action-card" shadow="hover">
          <div class="action-content">
            <div class="action-info">
              <h4>修改用户名</h4>
              <p>当前用户名：<strong>{{ userStore.user?.username }}</strong></p>
              <p class="tip">支持中文、英文、数字和下划线，至少2个字符</p>
            </div>
            <el-button type="primary" @click="showChangeUsernameDialog">修改</el-button>
          </div>
        </el-card>

        <!-- 修改密码 -->
        <el-card class="action-card" shadow="hover">
          <div class="action-content">
            <div class="action-info">
              <h4>修改密码</h4>
              <p>定期修改密码可以提高账号安全性</p>
              <p class="tip">密码至少6个字符</p>
            </div>
            <el-button type="primary" @click="showChangePasswordDialog">修改</el-button>
          </div>
        </el-card>
      </div>
    </el-card>

    <!-- 修改用户名对话框 -->
    <el-dialog v-model="usernameDialogVisible" title="修改用户名" width="500px">
      <el-form :model="usernameForm" :rules="usernameRules" ref="usernameFormRef" label-width="100px">
        <el-form-item label="新用户名" prop="newUsername">
          <el-input v-model="usernameForm.newUsername" placeholder="请输入新用户名" />
        </el-form-item>
        <el-form-item label="确认密码" prop="password">
          <el-input v-model="usernameForm.password" type="password" placeholder="请输入当前密码确认" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="usernameDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleChangeUsername" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>

    <!-- 修改密码对话框 -->
    <el-dialog v-model="passwordDialogVisible" title="修改密码" width="500px">
      <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-width="100px">
        <el-form-item label="原密码" prop="oldPassword">
          <el-input v-model="passwordForm.oldPassword" type="password" placeholder="请输入原密码" />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input v-model="passwordForm.newPassword" type="password" placeholder="请输入新密码（至少6位）" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="passwordForm.confirmPassword" type="password" placeholder="请再次输入新密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="passwordDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleChangePassword" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { authAPI } from '@/api'

const router = useRouter()
const userStore = useUserStore()

const usernameDialogVisible = ref(false)
const passwordDialogVisible = ref(false)
const submitting = ref(false)

const usernameFormRef = ref()
const passwordFormRef = ref()

const usernameForm = ref({
  newUsername: '',
  password: ''
})

const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 验证规则
const usernameRules = {
  newUsername: [
    { required: true, message: '请输入新用户名', trigger: 'blur' },
    { min: 2, message: '用户名至少2个字符', trigger: 'blur' },
    {
      pattern: /^[\u4e00-\u9fa5a-zA-Z0-9_]+$/,
      message: '用户名只能包含中文、英文、数字和下划线',
      trigger: 'blur'
    }
  ],
  password: [
    { required: true, message: '请输入当前密码', trigger: 'blur' }
  ]
}

const passwordRules = {
  oldPassword: [
    { required: true, message: '请输入原密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码至少6个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (rule: any, value: string, callback: any) => {
        if (value !== passwordForm.value.newPassword) {
          callback(new Error('两次输入密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 格式化日期
function formatDate(dateStr: string | undefined) {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 计算账号使用时长
const accountAge = computed(() => {
  if (!userStore.user?.created_at) return '-'
  
  const createdDate = new Date(userStore.user.created_at)
  const now = new Date()
  const diffMs = now.getTime() - createdDate.getTime()
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  
  if (diffDays === 0) {
    return '今天注册'
  } else if (diffDays < 30) {
    return `${diffDays} 天`
  } else if (diffDays < 365) {
    const months = Math.floor(diffDays / 30)
    const days = diffDays % 30
    return days > 0 ? `${months} 个月 ${days} 天` : `${months} 个月`
  } else {
    const years = Math.floor(diffDays / 365)
    const months = Math.floor((diffDays % 365) / 30)
    return months > 0 ? `${years} 年 ${months} 个月` : `${years} 年`
  }
})

// 显示修改用户名对话框
function showChangeUsernameDialog() {
  usernameForm.value = {
    newUsername: '',
    password: ''
  }
  usernameDialogVisible.value = true
}

// 显示修改密码对话框
function showChangePasswordDialog() {
  passwordForm.value = {
    oldPassword: '',
    newPassword: '',
    confirmPassword: ''
  }
  passwordDialogVisible.value = true
}

// 修改用户名
async function handleChangeUsername() {
  await usernameFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      submitting.value = true
      try {
        await authAPI.changeUsername(usernameForm.value.newUsername, usernameForm.value.password)
        ElMessage.success('用户名修改成功，请重新登录')
        usernameDialogVisible.value = false
        setTimeout(() => {
          userStore.logout()
          router.push('/login')
        }, 1500)
      } catch (error: any) {
        ElMessage.error(error.response?.data?.detail || '用户名修改失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

// 修改密码
async function handleChangePassword() {
  await passwordFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      submitting.value = true
      try {
        await authAPI.changePassword(passwordForm.value.oldPassword, passwordForm.value.newPassword)
        ElMessage.success('密码修改成功，请重新登录')
        passwordDialogVisible.value = false
        setTimeout(() => {
          userStore.logout()
          router.push('/login')
        }, 1500)
      } catch (error: any) {
        ElMessage.error(error.response?.data?.detail || '密码修改失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

onMounted(async () => {
  if (!userStore.user) {
    await userStore.fetchUserInfo()
  }
})
</script>

<style scoped>
.user-profile-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 20px;
}

.profile-card {
  border-radius: 8px;
}

.card-header h2 {
  margin: 0;
  color: #303133;
}

.profile-info {
  margin-bottom: 20px;
}

.profile-info :deep(.el-descriptions__label) {
  font-weight: 500;
  color: #606266;
}

.security-section {
  margin-top: 20px;
}

.security-section h3 {
  margin: 0 0 20px 0;
  color: #303133;
  font-size: 18px;
}

.action-card {
  margin-bottom: 15px;
  cursor: pointer;
  transition: all 0.3s;
}

.action-card:hover {
  transform: translateY(-2px);
}

.action-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.action-info h4 {
  margin: 0 0 8px 0;
  color: #303133;
  font-size: 16px;
}

.action-info p {
  margin: 5px 0;
  color: #606266;
  font-size: 14px;
}

.action-info .tip {
  font-size: 12px;
  color: #909399;
}
</style>
