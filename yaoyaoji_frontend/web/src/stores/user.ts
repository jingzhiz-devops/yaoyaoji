/**
 * 用户状态管理
 */
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authAPI } from '@/api'
import type { User } from '@/types'

export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))

  // 登录
  async function login(username: string, password: string) {
    const res: any = await authAPI.login(username, password)
    token.value = res.access_token
    localStorage.setItem('token', res.access_token)
    await fetchUserInfo()
  }

  // 注册
  async function register(data: { username: string; password: string; email?: string }) {
    await authAPI.register(data)
  }

  // 获取用户信息
  async function fetchUserInfo() {
    const res: any = await authAPI.getCurrentUser()
    user.value = res
  }

  // 登出
  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
  }

  return {
    user,
    token,
    login,
    register,
    fetchUserInfo,
    logout
  }
})
