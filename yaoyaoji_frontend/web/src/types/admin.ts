/**
 * 管理员后台类型定义
 */

// ============= 分页响应 =============

export interface PaginatedResult<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

// ============= 仪表盘 =============

export interface UserGrowthTrend {
  date: string
  count: number
}

export interface AdminDashboardStats {
  total_users: number
  active_users: number
  online_users: number
  total_medicines: number
  total_diseases: number
  total_schedules: number
  new_users_today: number
  new_users_this_week: number
  user_growth_trend: UserGrowthTrend[]
}

export interface OnlineUser {
  id: number
  username: string
  real_name: string | null
  avatar: string | null
  is_admin: boolean
  connected_at: string | null
}

// ============= 用户管理 =============

export interface AdminUser {
  id: number
  username: string
  email: string | null
  real_name: string | null
  is_admin: boolean
  is_active: boolean
  created_at: string
  medication_count: number
  schedule_count: number
  family_name: string | null
}

export interface AdminUserUpdate {
  is_admin?: boolean
  is_active?: boolean
  email?: string
  real_name?: string
}

export interface AdminUserListParams {
  page?: number
  page_size?: number
  search?: string
  is_admin?: boolean
  is_active?: boolean
}

// ============= 药品管理 =============

export interface AdminMedicine {
  id: number
  name: string
  generic_name: string | null
  manufacturer: string | null
  ingredients: string | null
  efficacy: string | null
  contraindications: string | null
  side_effects: string | null
  image_url: string | null
  created_at: string
  users: string[]
}

export interface MedicineCreate {
  name: string
  generic_name?: string
  manufacturer?: string
  ingredients?: string
  efficacy?: string
  contraindications?: string
  side_effects?: string
  image_url?: string
}

export interface MedicineUpdate {
  name?: string
  generic_name?: string
  manufacturer?: string
  ingredients?: string
  efficacy?: string
  contraindications?: string
  side_effects?: string
  image_url?: string
}

// ============= 疾病管理 =============

export interface AdminDisease {
  id: number
  name: string
  aliases: string | null
  description: string | null
  recommended: string | null
  avoid: string | null
  created_at: string
}

export interface DiseaseCreate {
  name: string
  aliases?: string
  description?: string
  recommended?: string
  avoid?: string
}

export interface DiseaseUpdate {
  name?: string
  aliases?: string
  description?: string
  recommended?: string
  avoid?: string
}

// ============= 系统监控 =============

export interface SystemHealth {
  status: string
  database: string
  timestamp: string
}

export interface DbStats {
  users: number
  medicines: number
  diseases: number
  user_medications: number
  medication_schedules: number
  medication_records: number
}


// ============= 慢性病模板管理 =============

export interface AdminDiseaseTemplate {
  id: number
  disease_type: string
  display_name: string
  icd10_code: string | null
  description: string | null
  default_indicators: any[]
  created_at: string
}

export interface DiseaseTemplateCreate {
  disease_type: string
  display_name: string
  icd10_code?: string
  description?: string
  default_indicators: any[]
}

export interface DiseaseTemplateUpdate {
  disease_type?: string
  display_name?: string
  icd10_code?: string
  description?: string
  default_indicators?: any[]
}

// ============= 用户慢性病记录 =============

export interface AdminChronicRecord {
  id: number
  user_id: number
  username: string
  disease_name: string
  icd10_code: string | null
  diagnosis_date: string | null
  diagnosis_hospital: string | null
  diagnosis_doctor: string | null
  current_treatment: string | null
  control_status: string | null
  created_at: string | null
  updated_at: string | null
}
