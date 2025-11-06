/**
 * 类型定义
 */

// 用户类型
export interface User {
  id: number
  username: string
  email?: string
  created_at: string
}

// 药品类型
export interface Medicine {
  id: number
  name: string
  generic_name?: string
  manufacturer?: string
  contraindications?: string
  side_effects?: string
  image_url?: string
  created_at: string
}

// 创建药品数据类型
export interface CreateMedicineData {
  name: string
  contraindications: string
  manufacturer?: string
  image_url?: string
  notes?: string
}

// 用户药箱类型
export interface UserMedication {
  id: number
  user_id: number
  medicine_id: number
  custom_name?: string
  notes?: string
  status: 'active' | 'inactive'
  medicine: Medicine
}

// 用药计划类型
export interface MedicationSchedule {
  id: number
  user_medication_id: number
  scheduled_time: string
  dose: string
  frequency: 'once_daily' | 'twice_daily' | 'three_times_daily' | 'four_times_daily'
  start_date: string
  end_date?: string
}

// 用药记录类型
export interface MedicationRecord {
  id: number
  schedule_id: number
  scheduled_time: string
  actual_time?: string
  status: 'pending' | 'taken' | 'skipped' | 'delayed'
  skip_reason?: string
}

// 症状记录类型
export interface SymptomRecord {
  id: number
  user_id: number
  symptom_emoji?: string
  symptom_text: string
  intensity: number
  recorded_time: string
}
