<template>
  <div class="user-profile-container">
    <div class="profile-content">
      <el-row :gutter="24">
        <el-col :span="8">
          <!-- 个人信息卡片 -->
          <el-card class="profile-card" shadow="hover">
            <div class="profile-header">
              <div class="avatar-wrapper">
                <el-upload
                  class="avatar-uploader"
                  :show-file-list="false"
                  :before-upload="beforeAvatarUpload"
                  :http-request="handleAvatarUpload"
                  accept="image/*"
                >
                  <div class="avatar-circle" v-if="!userStore.user?.avatar">
                    {{ userStore.user?.username?.charAt(0).toUpperCase() }}
                    <div class="avatar-overlay">
                      <el-icon><Camera /></el-icon>
                    </div>
                  </div>
                  <div class="avatar-image-wrapper" v-else>
                    <img :src="getAvatarUrl(userStore.user.avatar)" class="avatar-image" />
                    <div class="avatar-overlay">
                      <el-icon><Camera /></el-icon>
                    </div>
                  </div>
                </el-upload>
              </div>
              <h3 class="username">{{ userStore.user?.username }}</h3>
              <div class="contact-info">
                <p class="info-item" v-if="userStore.user?.phone">
                  <el-icon><Iphone /></el-icon>
                  {{ userStore.user.phone }}
                </p>
                <p class="info-item" v-if="userStore.user?.email">
                  <el-icon><Message /></el-icon>
                  {{ userStore.user.email }}
                </p>
                <p class="info-item empty" v-if="!userStore.user?.phone && !userStore.user?.email">
                  未设置联系方式
                </p>
              </div>
              <el-tag class="role-tag" effect="dark" round>普通用户</el-tag>
            </div>
            
            <div class="profile-stats">
              <div class="stat-item">
                <span class="stat-label">注册时间</span>
                <span class="stat-value">{{ formatDate(userStore.user?.created_at) }}</span>
              </div>
              <div class="stat-divider"></div>
              <div class="stat-item">
                <span class="stat-label">使用时长</span>
                <span class="stat-value">{{ accountAge }}</span>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="16">
          <!-- 个人信息设置 -->
          <el-card class="security-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon><User /></el-icon>
                <span>个人信息</span>
              </div>
            </template>
            
            <div class="security-list">
              <div class="security-item">
                <div class="item-icon">
                  <el-icon><User /></el-icon>
                </div>
                <div class="item-content">
                  <div class="item-title">用户名</div>
                  <div class="item-desc">当前用户名：<strong>{{ userStore.user?.username }}</strong></div>
                </div>
                <el-button type="primary" plain @click="showChangeUsernameDialog">修改</el-button>
              </div>
              
              <div class="security-item">
                <div class="item-icon">
                  <el-icon><Iphone /></el-icon>
                </div>
                <div class="item-content">
                  <div class="item-title">手机号</div>
                  <div class="item-desc">当前手机号：<strong>{{ userStore.user?.phone || '未设置' }}</strong></div>
                </div>
                <el-button type="primary" plain @click="showEditPhoneDialog">修改</el-button>
              </div>
              
              <div class="security-item">
                <div class="item-icon">
                  <el-icon><Message /></el-icon>
                </div>
                <div class="item-content">
                  <div class="item-title">邮箱</div>
                  <div class="item-desc">当前邮箱：<strong>{{ userStore.user?.email || '未设置' }}</strong></div>
                </div>
                <el-button type="primary" plain @click="showEditEmailDialog">修改</el-button>
              </div>
              
              <div class="security-item">
                <div class="item-icon">
                  <el-icon><Key /></el-icon>
                </div>
                <div class="item-content">
                  <div class="item-title">登录密码</div>
                  <div class="item-desc">定期修改密码可以提高账号安全性</div>
                </div>
                <el-button type="primary" plain @click="showChangePasswordDialog">修改</el-button>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 修改用户名对话框 -->
    <el-dialog v-model="usernameDialogVisible" title="修改用户名" width="400px" class="custom-dialog">
      <el-form :model="usernameForm" :rules="usernameRules" ref="usernameFormRef" label-position="top">
        <el-form-item label="新用户名" prop="newUsername">
          <el-input v-model="usernameForm.newUsername" placeholder="请输入新用户名" size="large">
            <template #prefix><el-icon><User /></el-icon></template>
          </el-input>
          <div class="form-tip">支持中文、英文、数字和下划线，至少2个字符</div>
        </el-form-item>
        <el-form-item label="确认密码" prop="password">
          <el-input v-model="usernameForm.password" type="password" placeholder="请输入当前密码确认" size="large" show-password>
            <template #prefix><el-icon><Lock /></el-icon></template>
          </el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="usernameDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleChangeUsername" :loading="submitting">确定修改</el-button>
      </template>
    </el-dialog>

    <!-- 修改密码对话框 -->
    <el-dialog v-model="passwordDialogVisible" title="修改密码" width="400px" class="custom-dialog">
      <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-position="top">
        <el-form-item label="原密码" prop="oldPassword">
          <el-input v-model="passwordForm.oldPassword" type="password" placeholder="请输入原密码" size="large" show-password>
            <template #prefix><el-icon><Key /></el-icon></template>
          </el-input>
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input v-model="passwordForm.newPassword" type="password" placeholder="请输入新密码（至少6位）" size="large" show-password>
            <template #prefix><el-icon><Lock /></el-icon></template>
          </el-input>
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="passwordForm.confirmPassword" type="password" placeholder="请再次输入新密码" size="large" show-password>
            <template #prefix><el-icon><Check /></el-icon></template>
          </el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="passwordDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleChangePassword" :loading="submitting">确定修改</el-button>
      </template>
    </el-dialog>

    <!-- 修改手机号对话框 -->
    <el-dialog v-model="phoneDialogVisible" title="修改手机号" width="400px" class="custom-dialog">
      <el-form :model="phoneForm" :rules="phoneRules" ref="phoneFormRef" label-position="top">
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="phoneForm.phone" placeholder="请输入11位手机号" size="large">
            <template #prefix><el-icon><Iphone /></el-icon></template>
          </el-input>
        </el-form-item>
        <div class="form-tip">手机号用于接收飞书用药提醒通知</div>
      </el-form>
      <template #footer>
        <el-button @click="phoneDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleUpdatePhone" :loading="submitting">确定修改</el-button>
      </template>
    </el-dialog>

    <!-- 修改邮箱对话框 -->
    <el-dialog v-model="emailDialogVisible" title="修改邮箱" width="400px" class="custom-dialog">
      <el-form :model="emailForm" :rules="emailRules" ref="emailFormRef" label-position="top">
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="emailForm.email" placeholder="请输入邮箱地址" size="large">
            <template #prefix><el-icon><Message /></el-icon></template>
          </el-input>
        </el-form-item>
        <div class="form-tip">邮箱用于接收飞书用药提醒通知</div>
      </el-form>
      <template #footer>
        <el-button @click="emailDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleUpdateEmail" :loading="submitting">确定修改</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { authAPI, uploadAPI } from '@/api'
import { User, Lock, Key, Check, Camera, Iphone, Message } from '@element-plus/icons-vue'
import type { UploadRequestOptions } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()

const usernameDialogVisible = ref(false)
const passwordDialogVisible = ref(false)
const phoneDialogVisible = ref(false)
const emailDialogVisible = ref(false)
const submitting = ref(false)

const usernameFormRef = ref()
const passwordFormRef = ref()
const phoneFormRef = ref()
const emailFormRef = ref()

const usernameForm = ref({
  newUsername: '',
  password: ''
})

const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const phoneForm = ref({
  phone: ''
})

const emailForm = ref({
  email: ''
})

const avatarUploading = ref(false)

// 获取头像完整URL
function getAvatarUrl(avatarPath: string) {
  if (!avatarPath) return ''
  if (avatarPath.startsWith('http')) return avatarPath
  // 返回相对路径，会通过后端静态文件服务访问
  const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  return `${baseUrl}${avatarPath}`
}

// 头像上传前校验
function beforeAvatarUpload(file: File) {
  const isImage = file.type.startsWith('image/')
  const isLt5M = file.size / 1024 / 1024 < 5

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过 5MB!')
    return false
  }
  return true
}

// 处理头像上传
async function handleAvatarUpload(options: UploadRequestOptions) {
  avatarUploading.value = true
  try {
    // 上传文件
    const uploadRes: any = await uploadAPI.uploadAvatar(options.file as File)
    const avatarUrl = uploadRes.url
    
    // 更新用户头像
    await authAPI.changeAvatar(avatarUrl)
    
    // 刷新用户信息
    await userStore.fetchUserInfo()
    
    ElMessage.success('头像修改成功')
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '头像上传失败')
  } finally {
    avatarUploading.value = false
  }
}

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

const phoneRules = {
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的11位手机号', trigger: 'blur' }
  ]
}

const emailRules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ]
}

// 格式化日期
function formatDate(dateStr: string | undefined) {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
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

// 显示修改手机号对话框
function showEditPhoneDialog() {
  phoneForm.value = {
    phone: userStore.user?.phone || ''
  }
  phoneDialogVisible.value = true
}

// 显示修改邮箱对话框
function showEditEmailDialog() {
  emailForm.value = {
    email: userStore.user?.email || ''
  }
  emailDialogVisible.value = true
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

// 更新手机号
async function handleUpdatePhone() {
  await phoneFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      submitting.value = true
      try {
        await authAPI.updateProfile({ phone: phoneForm.value.phone })
        await userStore.fetchUserInfo()
        ElMessage.success('手机号修改成功')
        phoneDialogVisible.value = false
      } catch (error: any) {
        ElMessage.error(error.response?.data?.detail || '手机号修改失败')
      } finally {
        submitting.value = false
      }
    }
  })
}

// 更新邮箱
async function handleUpdateEmail() {
  await emailFormRef.value.validate(async (valid: boolean) => {
    if (valid) {
      submitting.value = true
      try {
        await authAPI.updateProfile({ email: emailForm.value.email })
        await userStore.fetchUserInfo()
        ElMessage.success('邮箱修改成功')
        emailDialogVisible.value = false
      } catch (error: any) {
        ElMessage.error(error.response?.data?.detail || '邮箱修改失败')
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
  width: 100%;
  max-width: 1000px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 32px;
}

.header-left h2 {
  font-size: 24px;
  font-weight: 700;
  color: var(--color-text-main);
  margin: 0 0 8px 0;
}

.subtitle {
  color: var(--color-text-secondary);
  font-size: 14px;
  margin: 0;
}

/* Profile Card */
.profile-card {
  border: none;
  text-align: center;
  padding: 20px 0;
}

.profile-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 32px;
}

.avatar-wrapper {
  margin-bottom: 16px;
  position: relative;
}

.avatar-uploader {
  cursor: pointer;
}

.avatar-circle {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-light) 100%);
  color: white;
  font-size: 40px;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 20px rgba(42, 157, 143, 0.3);
  position: relative;
  overflow: hidden;
}

.avatar-image-wrapper {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  position: relative;
  overflow: hidden;
  box-shadow: 0 8px 20px rgba(42, 157, 143, 0.3);
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
  border-radius: 50%;
}

.avatar-overlay .el-icon {
  font-size: 24px;
  color: white;
}

.avatar-circle:hover .avatar-overlay,
.avatar-image-wrapper:hover .avatar-overlay {
  opacity: 1;
}

.username {
  margin: 0 0 4px 0;
  font-size: 24px;
  color: var(--color-text-main);
}

.contact-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  margin-bottom: 12px;
}

.info-item {
  margin: 0;
  font-size: 14px;
  color: var(--color-text-secondary);
  display: flex;
  align-items: center;
  gap: 6px;
}

.info-item.empty {
  color: var(--color-text-light);
  font-style: italic;
}

.email {
  margin: 0 0 12px 0;
  color: var(--color-text-secondary);
  font-size: 14px;
}

.profile-stats {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 24px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  font-size: 12px;
  color: var(--color-text-light);
}

.stat-value {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-main);
}

.stat-divider {
  width: 1px;
  height: 30px;
  background: var(--color-border);
}

/* Security Card */
.security-card {
  border: none;
  height: 100%;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-main);
}

.security-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.security-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: #f9fafb;
  border-radius: 12px;
  border: 1px solid var(--color-border);
  transition: all 0.3s;
}

.security-item:hover {
  background: white;
  box-shadow: var(--shadow-sm);
  transform: translateY(-2px);
}

.item-icon {
  width: 48px;
  height: 48px;
  background: white;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: var(--color-primary);
  box-shadow: var(--shadow-sm);
}

.item-content {
  flex: 1;
}

.item-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--color-text-main);
  margin-bottom: 4px;
}

.item-desc {
  font-size: 13px;
  color: var(--color-text-secondary);
}

.form-tip {
  font-size: 12px;
  color: var(--color-text-light);
  margin-top: 4px;
}
</style>
