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
  },

  // 用药依从性
  adherence: {
    // 计算依从性
    calculate: (diseaseId: number, params?: { period_days?: number }) =>
      service.post(`/chronic-diseases/${diseaseId}/adherence/calculate`, null, { params }),
    
    // 获取依从性记录
    list: (diseaseId: number) =>
      service.get(`/chronic-diseases/${diseaseId}/adherence`),
    
    // 获取依从性统计
    stats: (diseaseId: number) =>
      service.get(`/chronic-diseases/${diseaseId}/adherence/stats`)
  }
}
