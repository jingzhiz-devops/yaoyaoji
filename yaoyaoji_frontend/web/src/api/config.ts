/**
 * API 配置文件
 */
import axios from 'axios'
import type { AxiosInstance } from 'axios'
import { ElMessage } from 'element-plus'

// 支持环境变量配置，如果没有则使用默认值
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

const service: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60秒超时，适配AI请求
  headers: {
    'Content-Type': 'application/json'
  }
})

service.interceptors.request.use(
  (config) => {
    // 根据当前页面路径选择对应的 token
    const isAdminPath = window.location.pathname.startsWith('/admin')
    const token = localStorage.getItem(isAdminPath ? 'admin_token' : 'token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

service.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    // 打印详细错误信息供调试
    console.error('API 错误:', {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      data: error.response?.data,
      message: error.message
    })

    if (error.response) {
      const { status } = error.response
      // 401错误自动跳转登录，但不显示错误消息（由页面处理）
      if (status === 401 && window.location.pathname !== '/login' && window.location.pathname !== '/admin/login') {
        const isAdminPath = window.location.pathname.startsWith('/admin')
        localStorage.removeItem(isAdminPath ? 'admin_token' : 'token')
        window.location.href = isAdminPath ? '/admin/login' : '/login'
      }
      // 其他错误不在这里处理，由各个页面自己处理
    } else if (error.request) {
      // 请求已发出但没有收到响应
      console.error('网络错误: 无法连接到后端服务器')
    }
    return Promise.reject(error)
  }
)

export default service
