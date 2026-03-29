/**
 * API 服务入口
 */
import axios from 'axios'
import service from './config'
import { API_BASE_URL } from './config'

// 认证相关
export const authAPI = {
  // 获取验证码图片（需要拿到响应头中的 captcha_id，所以用原始 axios）
  getCaptcha: async (): Promise<{ captchaId: string; imageUrl: string }> => {
    const res = await axios.get(`${API_BASE_URL}/auth/captcha`, { responseType: 'blob' })
    const captchaId = res.headers['x-captcha-id']
    const imageUrl = URL.createObjectURL(res.data)
    return { captchaId, imageUrl }
  },

  // 用户注册
  register: (data: { username: string; password: string; email?: string; captcha_id?: string; captcha_code?: string }) =>
    service.post('/auth/register', data),
  
  // 用户登录
  login: (username: string, password: string, captchaId: string, captchaCode: string) =>
    service.post('/auth/login', new URLSearchParams({ username, password, captcha_id: captchaId, captcha_code: captchaCode }), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    }),
  
  // Google 第三方登录
  googleLogin: (credential: string) =>
    service.post('/auth/google-login', new URLSearchParams({ credential }), {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    }),
  
  // 获取当前用户信息
  getCurrentUser: (customToken?: string) => {
    const config = customToken
      ? { headers: { Authorization: `Bearer ${customToken}` } }
      : {}
    return service.get('/users/me', config)
  },
  
  // 修改密码
  changePassword: (oldPassword: string, newPassword: string) =>
    service.patch('/users/change-password', null, {
      params: { old_password: oldPassword, new_password: newPassword }
    }),
  
  // 修改用户名
  changeUsername: (newUsername: string, password: string) =>
    service.patch('/users/change-username', null, {
      params: { new_username: newUsername, password: password }
    }),
  
  // 修改头像
  changeAvatar: (avatarUrl: string) =>
    service.patch('/users/change-avatar', null, {
      params: { avatar_url: avatarUrl }
    })
}

// 药品相关
export const medicineAPI = {
  // 获取药品列表
  list: (params?: { skip?: number; limit?: number; search?: string }) =>
    service.get('/medicines', { params }),
  
  // 获取药品详情
  get: (id: number) => service.get(`/medicines/${id}`),
  
  // 创建药品
  create: (data: any) => service.post('/medicines', data)
}

// 用户药箱相关
export const userMedicationAPI = {
  // 获取我的药箱
  list: (status?: string) =>
    service.get('/user-medications', { params: { status_filter: status } }),
  
  // 添加药品到药箱
  add: (data: { medicine_id: number; custom_name?: string; notes?: string }) =>
    service.post('/user-medications', data),
  
  // 更新药箱药品
  update: (id: number, data: any) =>
    service.patch(`/user-medications/${id}`, data),
  
  // 移除药品
  remove: (id: number) => service.delete(`/user-medications/${id}`)
}

// 用药计划相关
export const scheduleAPI = {
  // 获取用药计划
  list: (activeOnly: boolean = true) =>
    service.get('/schedules', { params: { active_only: activeOnly } }),
  
  // 创建用药计划
  create: (data: any) => service.post('/schedules', data),
  
  // 更新用药计划
  update: (id: number, data: any) => service.patch(`/schedules/${id}`, data),
  
  // 删除用药计划
  delete: (id: number) => service.delete(`/schedules/${id}`)
}

// 用药记录相关
export const recordAPI = {
  // 获取用药记录
  list: (params?: { start_date?: string; end_date?: string; status_filter?: string }) =>
    service.get('/records', { params }),
  
  // 获取今日用药记录
  today: () => service.get('/records/today'),
  
  // 更新用药记录
  update: (id: number, data: { status: string; actual_time?: string; skip_reason?: string }) =>
    service.patch(`/records/${id}`, data)
}

// 症状记录相关
export const symptomAPI = {
  // 获取症状记录
  list: (params?: { start_date?: string; end_date?: string; min_intensity?: number }) =>
    service.get('/symptoms', { params }),
  
  // 获取今日症状
  today: () => service.get('/symptoms/today'),
  
  // 获取症状时间轴
  timeline: (days: number = 7) =>
    service.get('/symptoms/timeline', { params: { days } }),
  
  // 创建症状记录
  create: (data: { symptom_emoji?: string; symptom_text: string; intensity: number }) =>
    service.post('/symptoms', data),
  
  // 更新症状记录
  update: (id: number, data: { symptom_emoji?: string; symptom_text?: string; intensity?: number }) =>
    service.patch(`/symptoms/${id}`, data),
  
  // 删除症状记录
  delete: (id: number) => service.delete(`/symptoms/${id}`)
}

// 疾病相关
export const diseaseAPI = {
  // 获取疾病列表（支持搜索）
  list: (params?: { search?: string; medicine_name?: string }) => service.get('/diseases', { params })
}

// 健康档案相关
export const healthProfileAPI = {
  // 获取我的健康档案
  get: () => service.get('/health-profile'),
  
  // 创建/更新健康档案
  createOrUpdate: (data: any) => service.post('/health-profile', data),
  
  // 过敏史
  allergies: {
    list: () => service.get('/health-profile/allergies'),
    create: (data: any) => service.post('/health-profile/allergies', data),
    update: (id: number, data: any) => service.patch(`/health-profile/allergies/${id}`, data),
    delete: (id: number) => service.delete(`/health-profile/allergies/${id}`)
  },
  
  // 家族病史
  familyHistory: {
    list: () => service.get('/health-profile/family-history'),
    create: (data: any) => service.post('/health-profile/family-history', data),
    update: (id: number, data: any) => service.patch(`/health-profile/family-history/${id}`, data),
    delete: (id: number) => service.delete(`/health-profile/family-history/${id}`)
  },
  
  // 手术记录
  surgeries: {
    list: () => service.get('/health-profile/surgeries'),
    create: (data: any) => service.post('/health-profile/surgeries', data),
    update: (id: number, data: any) => service.patch(`/health-profile/surgeries/${id}`, data),
    delete: (id: number) => service.delete(`/health-profile/surgeries/${id}`)
  },
  
  // 体检报告
  checkups: {
    list: () => service.get('/health-profile/checkups'),
    create: (data: any) => service.post('/health-profile/checkups', data),
    update: (id: number, data: any) => service.patch(`/health-profile/checkups/${id}`, data),
    delete: (id: number) => service.delete(`/health-profile/checkups/${id}`)
  },
  
  // 疫苗接种记录
  vaccinations: {
    list: () => service.get('/health-profile/vaccinations'),
    create: (data: any) => service.post('/health-profile/vaccinations', data),
    update: (id: number, data: any) => service.patch(`/health-profile/vaccinations/${id}`, data),
    delete: (id: number) => service.delete(`/health-profile/vaccinations/${id}`)
  }
}

// 家庭管理相关
export const familyAPI = {
  // 获取我的家庭
  getMyFamily: () => service.get('/family/my-family'),
  
  // 创建家庭
  createFamily: (data: { name: string }) => service.post('/family/create-family', data),
  
  // 更新家庭
  updateFamily: (data: { name: string }) => service.patch('/family/update-family', data),
  
  // 退出家庭
  leaveFamily: () => service.post('/family/leave-family'),
  
  // 通过邀请码加入家庭
  joinFamily: (inviteCode: string) => service.post('/family/join-family', { invite_code: inviteCode }),
  
  // 获取家庭成员用药信息
  getMembersMedication: () => service.get('/family/members-medication'),
  
  // 切换到家庭成员账号
  switchAccount: (target_user_id: number) => service.post('/family/switch-account', { target_user_id }),
  
  // 家庭成员
  members: {
    list: () => service.get('/family/members'),
    update: (id: number, data: any) => service.patch(`/family/members/${id}`, data),
    delete: (id: number) => service.delete(`/family/members/${id}`)
  },
  
  // 紧急联系人
  emergencyContacts: {
    list: () => service.get('/family/emergency-contacts'),
    create: (data: any) => service.post('/family/emergency-contacts', data),
    update: (id: number, data: any) => service.patch(`/family/emergency-contacts/${id}`, data),
    delete: (id: number) => service.delete(`/family/emergency-contacts/${id}`)
  }
}

// 文件上传相关
export const uploadAPI = {
  // 上传药品包装图
  uploadMedicineImage: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return service.post('/upload/medicine-image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },
  
  // 删除药品包装图
  deleteMedicineImage: (filename: string) => 
    service.delete(`/upload/medicine-image/${filename}`),
  
  // 上传用户头像
  uploadAvatar: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return service.post('/upload/avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },
  
  // 删除用户头像
  deleteAvatar: (filename: string) => 
    service.delete(`/upload/avatar/${filename}`)
}

// AI医生相关
export const aiDoctorAPI = {
  // AI智能医疗预测
  predict: (symptomDescription: string) =>
    service.post('/ai/predict', { symptom_description: symptomDescription }),
  
  // AI药品查询
  queryMedicine: (medicineName: string) =>
    service.post('/ai/query-medicine', { medicine_name: medicineName }),
  
  // AI疾病查询
  queryDisease: (diseaseName: string) =>
    service.post('/ai/query-disease', { disease_name: diseaseName })
}
