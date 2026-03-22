/**
 * 管理员后台 API 服务
 */
import service from '@/api/config'
import type {
  AdminDashboardStats,
  AdminUser,
  AdminUserUpdate,
  AdminUserListParams,
  AdminMedicine,
  MedicineCreate,
  MedicineUpdate,
  AdminDisease,
  DiseaseCreate,
  DiseaseUpdate,
  SystemHealth,
  DbStats,
  PaginatedResult,
  OnlineUser
} from '@/types/admin'

// ============= 仪表盘 API =============

export const getDashboardStats = (): Promise<AdminDashboardStats> => {
  return service.get('/admin/dashboard/stats')
}

export const getOnlineUsers = (): Promise<OnlineUser[]> => {
  return service.get('/admin/online-users')
}

// ============= 用户管理 API =============

export const getAdminUsers = (params?: AdminUserListParams): Promise<PaginatedResult<AdminUser>> => {
  return service.get('/admin/users', { params })
}

export const getAdminUser = (id: number): Promise<AdminUser> => {
  return service.get(`/admin/users/${id}`)
}

export const updateAdminUser = (id: number, data: AdminUserUpdate): Promise<AdminUser> => {
  return service.patch(`/admin/users/${id}`, data)
}

export const deleteAdminUser = (id: number): Promise<{ message: string }> => {
  return service.delete(`/admin/users/${id}`)
}

// ============= 药品管理 API =============

export const getAdminMedicines = (params?: {
  page?: number
  page_size?: number
  search?: string
}): Promise<PaginatedResult<AdminMedicine>> => {
  return service.get('/admin/medicines', { params })
}

export const createAdminMedicine = (data: MedicineCreate): Promise<AdminMedicine> => {
  return service.post('/admin/medicines', data)
}

export const updateAdminMedicine = (id: number, data: MedicineUpdate): Promise<AdminMedicine> => {
  return service.patch(`/admin/medicines/${id}`, data)
}

export const deleteAdminMedicine = (id: number): Promise<{ message: string }> => {
  return service.delete(`/admin/medicines/${id}`)
}

// ============= 疾病管理 API =============

export const getAdminDiseases = (params?: {
  page?: number
  page_size?: number
  search?: string
}): Promise<PaginatedResult<AdminDisease>> => {
  return service.get('/admin/diseases', { params })
}

export const createAdminDisease = (data: DiseaseCreate): Promise<AdminDisease> => {
  return service.post('/admin/diseases', data)
}

export const updateAdminDisease = (id: number, data: DiseaseUpdate): Promise<AdminDisease> => {
  return service.patch(`/admin/diseases/${id}`, data)
}

export const deleteAdminDisease = (id: number): Promise<{ message: string }> => {
  return service.delete(`/admin/diseases/${id}`)
}

// ============= 系统监控 API =============

export const getSystemHealth = (): Promise<SystemHealth> => {
  return service.get('/admin/system/health')
}

export const getDbStats = (): Promise<DbStats> => {
  return service.get('/admin/system/db-stats')
}


// ============= 慢性病模板管理 API =============

import type {
  AdminDiseaseTemplate,
  DiseaseTemplateCreate,
  DiseaseTemplateUpdate,
  AdminChronicRecord
} from '@/types/admin'

export const getAdminDiseaseTemplates = (params?: {
  page?: number
  page_size?: number
  search?: string
}): Promise<PaginatedResult<AdminDiseaseTemplate>> => {
  return service.get('/admin/chronic/templates', { params })
}

export const createAdminDiseaseTemplate = (data: DiseaseTemplateCreate): Promise<AdminDiseaseTemplate> => {
  return service.post('/admin/chronic/templates', data)
}

export const updateAdminDiseaseTemplate = (id: number, data: DiseaseTemplateUpdate): Promise<AdminDiseaseTemplate> => {
  return service.patch(`/admin/chronic/templates/${id}`, data)
}

export const deleteAdminDiseaseTemplate = (id: number): Promise<{ message: string }> => {
  return service.delete(`/admin/chronic/templates/${id}`)
}

// ============= 用户慢性病记录 API =============

export const getAdminChronicRecords = (params?: {
  page?: number
  page_size?: number
  search?: string
  control_status?: string
}): Promise<PaginatedResult<AdminChronicRecord>> => {
  return service.get('/admin/chronic/records', { params })
}
