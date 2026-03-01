/**
 * 慢性病管理API
 */
import service from './config'
import type {
  ChronicDisease,
  DiseaseIndicator,
  IndicatorRecord,
  FollowupPlan,
  FollowupRecord
} from '@/types'

// 慢性病管理
export const chronicDiseaseAPI = {
  // 获取慢性病列表
  list: (params?: { search?: string; control_status?: string; skip?: number; limit?: number }) =>
    service.get('/chronic-diseases', { params }),
  
  // 获取慢性病详情
  get: (diseaseId: number) =>
    service.get(`/chronic-diseases/${diseaseId}`),
  
  // 创建慢性病
  create: (data: Omit<ChronicDisease, 'id' | 'user_id' | 'indicators' | 'followup_plans' | 'created_at' | 'updated_at'>) =>
    service.post('/chronic-diseases', data),
  
  // 更新慢性病
  update: (diseaseId: number, data: Partial<Omit<ChronicDisease, 'id' | 'user_id' | 'indicators' | 'followup_plans' | 'created_at' | 'updated_at'>>) =>
    service.put(`/chronic-diseases/${diseaseId}`, data),
  
  // 删除慢性病
  delete: (diseaseId: number) =>
    service.delete(`/chronic-diseases/${diseaseId}`),

  // 收藏/取消收藏
  togglePin: (diseaseId: number) =>
    service.put(`/chronic-diseases/${diseaseId}/pin`),

  // 关键指标管理
  indicators: {
    // 获取指标列表
    list: (diseaseId: number) =>
      service.get(`/chronic-diseases/${diseaseId}/indicators`),
    
    // 添加指标
    add: (diseaseId: number, data: Omit<DiseaseIndicator, 'id' | 'disease_id' | 'created_at'>) =>
      service.post(`/chronic-diseases/${diseaseId}/indicators`, data)
  },

  // 指标记录管理
  indicatorRecords: {
    // 记录指标值
    create: (diseaseId: number, data: Omit<IndicatorRecord, 'id' | 'disease_id' | 'created_at'>) =>
      service.post(`/chronic-diseases/${diseaseId}/indicator-records`, data),
    
    // 获取历史记录
    list: (diseaseId: number, params?: { indicator_id?: number; days?: number }) =>
      service.get(`/chronic-diseases/${diseaseId}/indicator-records`, { params })
  },

  // 随访计划管理
  followupPlans: {
    // 创建随访计划
    create: (diseaseId: number, data: Omit<FollowupPlan, 'id' | 'disease_id' | 'created_at' | 'updated_at'>) =>
      service.post(`/chronic-diseases/${diseaseId}/followup-plans`, data),
    
    // 获取随访计划列表
    list: (diseaseId: number) =>
      service.get(`/chronic-diseases/${diseaseId}/followup-plans`),
    
    // 更新随访计划
    update: (diseaseId: number, planId: number, data: Partial<Omit<FollowupPlan, 'id' | 'disease_id' | 'created_at' | 'updated_at'>>) =>
      service.put(`/chronic-diseases/${diseaseId}/followup-plans/${planId}`, data),
    
    // 删除随访计划
    delete: (diseaseId: number, planId: number) =>
      service.delete(`/chronic-diseases/${diseaseId}/followup-plans/${planId}`)
  },

  // 随访记录管理
  followupRecords: {
    // 记录随访
    create: (diseaseId: number, planId: number, data: Omit<FollowupRecord, 'id' | 'followup_plan_id' | 'created_at'>) =>
      service.post(`/chronic-diseases/${diseaseId}/followup-plans/${planId}/records`, data),
    
    // 获取随访记录历史
    list: (diseaseId: number, planId: number) =>
      service.get(`/chronic-diseases/${diseaseId}/followup-plans/${planId}/records`)
  },

  // 异常值预警
  alerts: {
    // 获取预警列表
    list: (params?: { unread_only?: boolean; unhandled_only?: boolean; alert_level?: string }) =>
      service.get('/chronic-diseases/alerts', { params }),
    
    // 标记为已读
    markRead: (alertId: number) =>
      service.put(`/chronic-diseases/alerts/${alertId}/read`),
    
    // 处理预警
    handle: (alertId: number, data: { handler_notes?: string }) =>
      service.put(`/chronic-diseases/alerts/${alertId}/handle`, data),
    
    // 获取预警统计
    stats: () =>
      service.get('/chronic-diseases/alerts/stats')
  }
}


// ============= 慢性病管理扩展 API =============

// 疾病模板
export const diseaseTemplateAPI = {
  list: () => service.get('/disease-templates'),
}

// 基于模板创建
export const createFromTemplate = (data: {
  disease_type: string
  diagnosis_date?: string
  diagnosis_hospital?: string
  diagnosis_doctor?: string
  current_treatment?: string
}) => service.post('/chronic-diseases/from-template', data)

// 批量指标记录
export const batchRecordIndicators = (diseaseId: number, records: Array<{
  indicator_id: number
  value: number
  measurement_date: string
  recorded_by?: string
  notes?: string
}>) => service.post(`/chronic-diseases/${diseaseId}/indicators/batch-record`, { records })

// 饮食建议
export const dietAPI = {
  list: (params?: { disease_type?: string; meal_type?: string }) =>
    service.get('/diet-recommendations', { params }),
  personalized: (diseaseId: number) =>
    service.get(`/chronic-diseases/${diseaseId}/personalized-diet`),
}

// 并发症管理
export const complicationAPI = {
  create: (diseaseId: number, data: {
    complication_type: string
    severity: string
    discovered_date: string
    symptoms?: string
    treatment?: string
    notes?: string
  }) => service.post(`/chronic-diseases/${diseaseId}/complications`, data),
  
  list: (diseaseId: number, params?: { severity?: string; is_resolved?: boolean }) =>
    service.get(`/chronic-diseases/${diseaseId}/complications`, { params }),
  
  update: (complicationId: number, data: {
    severity?: string
    is_resolved?: boolean
    resolved_date?: string
    notes?: string
  }) => service.put(`/complications/${complicationId}`, data),
}

// 运动建议
export const exerciseAPI = {
  list: (params?: { disease_type?: string }) =>
    service.get('/exercise-recommendations', { params }),
  personalized: (diseaseId: number) =>
    service.get(`/chronic-diseases/${diseaseId}/personalized-exercise`),
}

// 用药提醒
export const medicationReminderAPI = {
  create: (data: {
    disease_id: number
    user_medication_id?: number
    reminder_time: string
    reminder_days: number[]
    advance_minutes?: number
  }) => service.post('/medication-reminders', data),
  
  list: (params?: { disease_id?: number; status?: string }) =>
    service.get('/medication-reminders', { params }),
  
  update: (reminderId: number, data: {
    status?: string
    reminder_time?: string
    reminder_days?: number[]
  }) => service.put(`/medication-reminders/${reminderId}`, data),

  delete: (reminderId: number) =>
    service.delete(`/medication-reminders/${reminderId}`),
}

// 高级搜索
export const advancedSearch = (params: {
  search?: string
  disease_type?: string
  control_status?: string
  start_date?: string
  end_date?: string
}) => service.get('/chronic-diseases/search/advanced', { params })

// 数据导出
export const exportAPI = {
  create: (data: {
    disease_ids: number[]
    format: string
    start_date?: string
    end_date?: string
    include_indicators?: boolean
    include_medications?: boolean
    include_complications?: boolean
  }) => service.post('/chronic-diseases/export', data),
  
  getTask: (taskId: string) => service.get(`/export-tasks/${taskId}`),
  
  download: (filename: string) => service.get(`/downloads/${filename}`, { responseType: 'blob' }),
}
