/**
 * 类型定义
 */

// 用户类型
export interface User {
  id: number
  username: string
  email?: string
  avatar?: string
  birth_date?: string
  real_name?: string
  is_family_admin?: boolean  // 是否家庭管理员
  relation_to_admin?: string  // 与管理员的关系（角色）：parent/child/elderly/spouse/other/admin/member
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
  purchase_date?: string
  therapy_duration?: number
  remind_advance_days: number
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

// 慢性病管理类型
export interface ChronicDisease {
  id: number
  user_id: number
  disease_name: string
  icd10_code?: string
  diagnosis_date?: string
  diagnosis_hospital?: string
  diagnosis_doctor?: string
  current_treatment?: string
  control_status: 'good' | 'fair' | 'poor'
  is_pinned: boolean
  indicators?: DiseaseIndicator[]
  followup_plans?: FollowupPlan[]
  created_at: string
  updated_at: string
}

export interface DiseaseIndicator {
  id: number
  disease_id: number
  indicator_name: string
  normal_range_min?: number
  normal_range_max?: number
  unit?: string
  check_frequency?: string
  created_at: string
}

export interface IndicatorRecord {
  id: number
  disease_id: number
  indicator_id: number
  value: number
  measurement_date: string
  recorded_by?: string
  notes?: string
  created_at: string
}

export interface FollowupPlan {
  id: number
  disease_id: number
  frequency: string
  last_followup_date?: string
  next_followup_date: string
  responsible_doctor?: string
  followup_checklist?: any
  target_values?: any
  reminder_days: number
  created_at: string
  updated_at: string
}

export interface FollowupRecord {
  id: number
  followup_plan_id: number
  followup_date: string
  symptoms_assessment?: string
  indicator_check?: any
  medication_evaluation?: string
  lifestyle_guidance?: string
  doctor_notes?: string
  next_plan?: string
  created_at: string
}


// ============= 慢性病管理扩展类型 =============

export interface DiseaseTemplate {
  id: number
  disease_type: string
  display_name: string
  icd10_code?: string
  description?: string
  default_indicators: Array<{
    name: string
    unit: string
    normal_min?: number
    normal_max?: number
    check_frequency?: string
  }>
  created_at: string
}

export interface DietRecommendation {
  id: number
  disease_type: string
  meal_type?: 'breakfast' | 'lunch' | 'dinner' | 'snack'
  title: string
  content: string
  food_suggestions?: string[]
  food_restrictions?: string[]
  applicable_conditions?: Record<string, any>
  priority: number
  created_at: string
}

export interface PersonalizedDiet {
  disease_type: string
  breakfast?: DietRecommendation[]
  lunch?: DietRecommendation[]
  dinner?: DietRecommendation[]
  general_tips: DietRecommendation[]
}

export interface ComplicationRecord {
  id: number
  disease_id: number
  complication_type: string
  severity: 'mild' | 'moderate' | 'severe'
  discovered_date: string
  symptoms?: string
  treatment?: string
  is_resolved: boolean
  resolved_date?: string
  notes?: string
  created_at: string
  updated_at: string
}

export interface ExerciseRecommendation {
  id: number
  disease_type: string
  title: string
  exercise_type: string
  duration_minutes?: number
  frequency_per_week?: number
  intensity?: string
  description: string
  precautions?: string
  created_at: string
}

export interface PersonalizedExercise {
  disease_type: string
  recommended_exercises: ExerciseRecommendation[]
  current_status?: string
  safety_tips: string[]
}

export interface MedicationReminder {
  id: number
  user_id: number
  disease_id: number
  user_medication_id: number
  reminder_time: string
  reminder_days: number[]
  status: 'active' | 'paused' | 'completed'
  advance_minutes: number
  repeat_interval_minutes?: number
  created_at: string
  updated_at: string
}

export interface ExportTask {
  task_id: string
  status: string
  download_url?: string
  expires_at?: string
}

export interface IndicatorAlert {
  id: number
  user_id: number
  disease_id: number
  indicator_id: number
  record_id: number
  alert_level: 'yellow' | 'orange' | 'red'
  alert_message: string
  indicator_value: number
  normal_range?: string
  suggestion?: string
  is_read: boolean
  is_handled: boolean
  handled_at?: string
  handler_notes?: string
  created_at: string
}
