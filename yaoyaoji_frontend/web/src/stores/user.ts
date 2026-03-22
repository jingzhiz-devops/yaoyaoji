/**
 * 用户状态管理
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authAPI } from '@/api'
import { heartbeatService } from '@/services/heartbeat'
import type { User } from '@/types'

// Token storage keys — 管理员和普通用户分开存储，避免同浏览器互相覆盖
const TOKEN_KEY = 'token'
const ADMIN_TOKEN_KEY = 'admin_token'

export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem(TOKEN_KEY))

  // 管理员状态
  const adminUser = ref<User | null>(null)
  const adminToken = ref<string | null>(localStorage.getItem(ADMIN_TOKEN_KEY))

  // 普通用户登录
  async function login(username: string, password: string, captchaId: string, captchaCode: string) {
    const res: any = await authAPI.login(username, password, captchaId, captchaCode)
    token.value = res.access_token
    localStorage.setItem(TOKEN_KEY, res.access_token)
    await fetchUserInfo()
    heartbeatService.connect(res.access_token)
  }

  // 管理员登录
  async function adminLogin(username: string, password: string, captchaId: string, captchaCode: string) {
    const res: any = await authAPI.login(username, password, captchaId, captchaCode)
    adminToken.value = res.access_token
    localStorage.setItem(ADMIN_TOKEN_KEY, res.access_token)
    await fetchAdminInfo()
    heartbeatService.connect(res.access_token)
  }

  // 注册
  async function register(data: { username: string; password: string; email?: string; captcha_id?: string; captcha_code?: string }) {
    await authAPI.register(data)
  }

  // 获取普通用户信息
  async function fetchUserInfo() {
    const res: any = await authAPI.getCurrentUser()
    user.value = res
  }

  // 获取管理员用户信息
  async function fetchAdminInfo() {
    const res: any = await authAPI.getCurrentUser(adminToken.value!)
    adminUser.value = res
  }

  // 普通用户登出
  function logout() {
    heartbeatService.disconnect()
    user.value = null
    token.value = null
    localStorage.removeItem(TOKEN_KEY)
  }

  // 管理员登出
  function adminLogout() {
    heartbeatService.disconnect()
    adminUser.value = null
    adminToken.value = null
    localStorage.removeItem(ADMIN_TOKEN_KEY)
  }

  return {
    user,
    token,
    adminUser,
    adminToken,
    login,
    adminLogin,
    register,
    fetchUserInfo,
    fetchAdminInfo,
    logout,
    adminLogout
  }
})
