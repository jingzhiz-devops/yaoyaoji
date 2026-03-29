"""
Pydantic Schemas - 数据验证和序列化
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Any
from datetime import datetime, date, time
from enum import Enum


# ============= 用户相关 Schemas =============

class UserBase(BaseModel):
    """用户基础Schema"""
    username: str = Field(..., min_length=2, max_length=50, description="用户名（支持中文，至少2个字符）")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    
    @validator('username')
    def validate_username(cls, v):
        """验证用户名：支持中文、英文、数字、下划线，至少2个字符"""
        if len(v) < 2:
            raise ValueError('用户名至少需要2个字符')
        # 支持中文、英文、数字、下划线
        import re
        if not re.match(r'^[\u4e00-\u9fa5a-zA-Z0-9_]+$', v):
            raise ValueError('用户名只能包含中文、英文、数字和下划线')
        return v


class UserCreate(UserBase):
    """用户创建Schema"""
    password: str = Field(..., min_length=6, max_length=50, description="密码")
    captcha_id: Optional[str] = Field(None, description="验证码ID")
    captcha_code: Optional[str] = Field(None, description="验证码")


class UserLogin(BaseModel):
    """用户登录Schema"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserResponse(UserBase):
    """用户响应Schema"""
    id: int
    phone: Optional[str] = None
    feishu_webhook: Optional[str] = None  # 飞书机器人Webhook
    avatar: Optional[str] = None
    birth_date: Optional[date] = None
    real_name: Optional[str] = None
    is_admin: bool = False  # 是否管理员
    is_active: bool = True  # 账号是否启用
    is_family_admin: bool = True  # 是否家庭管理员
    relation_to_admin: Optional[str] = None  # 与管理员的关系（角色）：parent/child/elderly/spouse/other/admin/member
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT Token Schema"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token数据Schema"""
    username: Optional[str] = None


# ============= 药品相关 Schemas =============

class MedicineBase(BaseModel):
    """药品基础Schema"""
    name: str = Field(..., max_length=100, description="药品名称")
    generic_name: Optional[str] = Field(None, max_length=100, description="通用名")
    manufacturer: Optional[str] = Field(None, max_length=100, description="生产厂家")
    ingredients: Optional[str] = Field(None, description="主要成分")
    efficacy: Optional[str] = Field(None, description="功效与作用")
    contraindications: Optional[str] = Field(None, description="禁忌信息")
    side_effects: Optional[str] = Field(None, description="副作用")
    image_url: Optional[str] = Field(None, max_length=500, description="药品图片URL")


class MedicineCreate(MedicineBase):
    """药品创建Schema"""
    pass


class MedicineResponse(MedicineBase):
    """药品响应Schema"""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= 用户药箱相关 Schemas =============

class MedicationStatusEnum(str, Enum):
    """用药状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"


class UserMedicationBase(BaseModel):
    """用户药箱基础Schema"""
    medicine_id: int = Field(..., description="药品ID")
    custom_name: Optional[str] = Field(None, max_length=100, description="自定义名称")
    notes: Optional[str] = Field(None, description="备注")


class UserMedicationCreate(UserMedicationBase):
    """用户药箱创建Schema"""
    pass


class UserMedicationUpdate(BaseModel):
    """用户药箱更新Schema"""
    custom_name: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[MedicationStatusEnum] = None
    # 支持更新关联的药哅信息
    medicine_name: Optional[str] = None
    contraindications: Optional[str] = None
    manufacturer: Optional[str] = None
    image_url: Optional[str] = None


class UserMedicationResponse(UserMedicationBase):
    """用户药箱响应Schema"""
    id: int
    user_id: int
    status: MedicationStatusEnum
    medicine: MedicineResponse
    
    class Config:
        from_attributes = True


# ============= 用药计划相关 Schemas =============

class FrequencyEnum(str, Enum):
    """用药频率枚举"""
    ONCE_DAILY = "once_daily"
    TWICE_DAILY = "twice_daily"
    THREE_TIMES_DAILY = "three_times_daily"
    FOUR_TIMES_DAILY = "four_times_daily"


class MedicationScheduleBase(BaseModel):
    """用药计划基础Schema"""
    user_medication_id: int = Field(..., description="用户药品ID")
    scheduled_times: List[time] = Field(..., description="计划用药时间列表")
    dose: str = Field(..., max_length=50, description="剂量")
    frequency: FrequencyEnum = Field(..., description="频率")
    start_date: date = Field(..., description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")
    purchase_date: Optional[date] = Field(None, description="药品购入日期")
    therapy_duration: Optional[int] = Field(None, description="吃药疗程（天数）")
    remind_advance_days: int = Field(5, description="提前提醒备药天数")
    notes: Optional[str] = Field(None, description="备注")


class MedicationScheduleCreate(MedicationScheduleBase):
    """用药计划创建Schema"""
    
    @validator('scheduled_times')
    def validate_scheduled_times(cls, v, values):
        """验证时间数量与频率匹配"""
        if 'frequency' in values:
            frequency = values['frequency']
            expected_count = {
                FrequencyEnum.ONCE_DAILY: 1,
                FrequencyEnum.TWICE_DAILY: 2,
                FrequencyEnum.THREE_TIMES_DAILY: 3,
                FrequencyEnum.FOUR_TIMES_DAILY: 4
            }
            if len(v) != expected_count.get(frequency, 1):
                raise ValueError(f'频率{frequency.value}需要{expected_count[frequency]}个时间点，但提供了{len(v)}个')
        return v
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        """验证结束日期必须晚于开始日期"""
        if v and 'start_date' in values and v < values['start_date']:
            raise ValueError('结束日期必须晚于开始日期')
        return v


class MedicationScheduleResponse(MedicationScheduleBase):
    """用药计划响应Schema"""
    id: int
    user_medication: 'UserMedicationResponse'  # 关联的用户药品信息，包含药品详情
    
    class Config:
        from_attributes = True


# ============= 用药记录相关 Schemas =============

class RecordStatusEnum(str, Enum):
    """用药记录状态枚举"""
    PENDING = "pending"
    TAKEN = "taken"
    SKIPPED = "skipped"
    DELAYED = "delayed"


class MedicationRecordBase(BaseModel):
    """用药记录基础Schema"""
    schedule_id: int = Field(..., description="用药计划ID")
    scheduled_time: datetime = Field(..., description="计划用药时间")


class MedicationRecordCreate(MedicationRecordBase):
    """用药记录创建Schema"""
    pass


class MedicationRecordUpdate(BaseModel):
    """用药记录更新Schema"""
    actual_time: Optional[datetime] = None
    status: RecordStatusEnum
    skip_reason: Optional[str] = Field(None, max_length=200)


class MedicationRecordResponse(MedicationRecordBase):
    """用药记录响应Schema"""
    id: int
    actual_time: Optional[datetime]
    status: RecordStatusEnum
    skip_reason: Optional[str]
    schedule: MedicationScheduleResponse  # 关联的用药计划信息


# ============= 疾病相关 Schemas =============

class DiseaseBase(BaseModel):
    name: str = Field(..., max_length=100, description="疾病名称")
    aliases: Optional[str] = Field(None, description="别名（逗号分隔）")
    description: Optional[str] = Field(None, description="简介")
    recommended: Optional[str] = Field(None, description="常用药物（逗号分隔）")
    avoid: Optional[str] = Field(None, description="避免搭配（逗号分隔）")

class DiseaseCreate(DiseaseBase):
    pass

class DiseaseResponse(DiseaseBase):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True


# ============= 症状记录相关 Schemas =============

class SymptomRecordBase(BaseModel):
    """症状记录基础Schema"""
    symptom_emoji: Optional[str] = Field(None, max_length=10, description="症状emoji")
    symptom_text: str = Field(..., max_length=100, description="症状描述")
    intensity: int = Field(..., ge=1, le=5, description="强度(1-5)")


class SymptomRecordCreate(SymptomRecordBase):
    """症状记录创建 Schema"""
    pass


class SymptomRecordUpdate(BaseModel):
    """症状记录更新 Schema"""
    symptom_emoji: Optional[str] = Field(None, max_length=10, description="症状emoji")
    symptom_text: Optional[str] = Field(None, max_length=100, description="症状描述")
    intensity: Optional[int] = Field(None, ge=1, le=5, description="强度(1-5)")


class SymptomRecordResponse(SymptomRecordBase):
    """症状记录响应Schema"""
    id: int
    user_id: int
    recorded_time: datetime
    
    class Config:
        from_attributes = True


# ============= 通用响应 Schemas =============

class MessageResponse(BaseModel):
    """通用消息响应"""
    message: str
    detail: Optional[str] = None


class ConflictWarning(BaseModel):
    """用药冲突警告"""
    medicine_1: str
    medicine_2: str
    warning: str
    severity: str = Field(..., description="严重程度: high, medium, low")


# ============= 健康档案相关 Schemas =============

class HealthProfileBase(BaseModel):
    """健康档案基础Schema"""
    real_name: Optional[str] = Field(None, max_length=50, description="真实姓名")
    birth_date: Optional[date] = Field(None, description="出生日期")
    blood_type: Optional[str] = Field(None, max_length=10, description="血型")
    height: Optional[int] = Field(None, ge=0, le=300, description="身高(cm)")
    weight: Optional[int] = Field(None, ge=0, le=500, description="体重(kg)")
    systolic_pressure: Optional[int] = Field(None, ge=0, le=300, description="收缩压(高压) mmHg")
    diastolic_pressure: Optional[int] = Field(None, ge=0, le=200, description="舒张压(低压) mmHg")
    heart_rate: Optional[int] = Field(None, ge=0, le=300, description="心率 次/分")
    blood_glucose: Optional[str] = Field(None, max_length=20, description="血糖 mmol/L")
    temperature: Optional[str] = Field(None, max_length=10, description="体温 ℃")
    chronic_diseases: Optional[str] = Field(None, description="慢性病，逗号分隔")


class HealthProfileCreate(HealthProfileBase):
    """健康档案创建 Schema"""
    pass


class HealthProfileUpdate(HealthProfileBase):
    """健康档案更新 Schema"""
    pass


class HealthProfileResponse(HealthProfileBase):
    """健康档案响应 Schema"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# 过敏史
class AllergyRecordBase(BaseModel):
    allergen: str = Field(..., max_length=100, description="过敏原")
    allergen_type: Optional[str] = Field(None, max_length=50, description="类型：药物/食物/其他")
    reaction: Optional[str] = Field(None, description="过敏反应")
    severity: Optional[str] = Field(None, max_length=20, description="严重程度")
    discovered_date: Optional[date] = Field(None, description="发现日期")
    notes: Optional[str] = None


class AllergyRecordCreate(AllergyRecordBase):
    pass


class AllergyRecordUpdate(BaseModel):
    allergen: Optional[str] = None
    allergen_type: Optional[str] = None
    reaction: Optional[str] = None
    severity: Optional[str] = None
    discovered_date: Optional[date] = None
    notes: Optional[str] = None


class AllergyRecordResponse(AllergyRecordBase):
    id: int
    profile_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# 家族病史
class FamilyHistoryBase(BaseModel):
    relative: str = Field(..., max_length=50, description="亲属关系")
    disease: str = Field(..., max_length=100, description="疾病")
    onset_age: Optional[int] = Field(None, ge=0, le=150, description="发病年龄")
    notes: Optional[str] = None


class FamilyHistoryCreate(FamilyHistoryBase):
    pass


class FamilyHistoryUpdate(BaseModel):
    relative: Optional[str] = None
    disease: Optional[str] = None
    onset_age: Optional[int] = None
    notes: Optional[str] = None


class FamilyHistoryResponse(FamilyHistoryBase):
    id: int
    profile_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# 手术记录
class SurgeryRecordBase(BaseModel):
    surgery_name: str = Field(..., max_length=200, description="手术名称")
    surgery_date: date = Field(..., description="手术日期")
    hospital: Optional[str] = Field(None, max_length=200, description="医院")
    doctor: Optional[str] = Field(None, max_length=100, description="主刀医生")
    notes: Optional[str] = None


class SurgeryRecordCreate(SurgeryRecordBase):
    pass


class SurgeryRecordUpdate(BaseModel):
    surgery_name: Optional[str] = None
    surgery_date: Optional[date] = None
    hospital: Optional[str] = None
    doctor: Optional[str] = None
    notes: Optional[str] = None


class SurgeryRecordResponse(SurgeryRecordBase):
    id: int
    profile_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# 体检报告
class CheckupReportBase(BaseModel):
    checkup_date: date = Field(..., description="体检日期")
    checkup_type: Optional[str] = Field(None, max_length=100, description="体检类型")
    hospital: Optional[str] = Field(None, max_length=200, description="医院")
    summary: Optional[str] = Field(None, description="总结")
    file_url: Optional[str] = Field(None, max_length=500, description="报告文件URL")


class CheckupReportCreate(CheckupReportBase):
    pass


class CheckupReportUpdate(BaseModel):
    checkup_date: Optional[date] = None
    checkup_type: Optional[str] = None
    hospital: Optional[str] = None
    summary: Optional[str] = None
    file_url: Optional[str] = None


class CheckupReportResponse(CheckupReportBase):
    id: int
    profile_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# 疫苗接种记录
class VaccinationRecordBase(BaseModel):
    vaccine_name: str = Field(..., max_length=100, description="疫苗名称")
    vaccination_date: date = Field(..., description="接种日期")
    hospital: Optional[str] = Field(None, max_length=200, description="医院")
    batch_number: Optional[str] = Field(None, max_length=100, description="批次号")
    next_dose_date: Optional[date] = Field(None, description="下次接种日期")
    notes: Optional[str] = None


class VaccinationRecordCreate(VaccinationRecordBase):
    pass


class VaccinationRecordUpdate(BaseModel):
    vaccine_name: Optional[str] = None
    vaccination_date: Optional[date] = None
    hospital: Optional[str] = None
    batch_number: Optional[str] = None
    next_dose_date: Optional[date] = None
    notes: Optional[str] = None


class VaccinationRecordResponse(VaccinationRecordBase):
    id: int
    profile_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= 慢性病相关 Schemas =============

class ControlStatusEnum(str, Enum):
    """控制状态枚举"""
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


class DiseaseIndicatorBase(BaseModel):
    """指标基础Schema"""
    indicator_name: str = Field(..., max_length=100, description="指标名称")
    normal_range_min: Optional[float] = Field(None, description="正常范围最小值")
    normal_range_max: Optional[float] = Field(None, description="正常范围最大值")
    unit: Optional[str] = Field(None, max_length=50, description="单位")
    check_frequency: Optional[str] = Field(None, description="检查频率")


class DiseaseIndicatorResponse(DiseaseIndicatorBase):
    """指标响应Schema"""
    id: int
    disease_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class IndicatorRecordBase(BaseModel):
    """指标记录基础Schema"""
    indicator_id: int = Field(..., description="指标ID")
    value: float = Field(..., description="数值")
    measurement_date: datetime = Field(..., description="测量日期")
    recorded_by: Optional[str] = Field(None, max_length=50, description="记录者")
    notes: Optional[str] = Field(None, description="备注")


class IndicatorRecordCreate(IndicatorRecordBase):
    """指标记录创建 Schema"""
    pass


class IndicatorRecordResponse(IndicatorRecordBase):
    """指标记录响应Schema"""
    id: int
    disease_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class FollowupPlanBase(BaseModel):
    """复查计划基础Schema"""
    frequency: str = Field(..., description="频率: weekly/monthly/quarterly/yearly")
    next_followup_date: date = Field(..., description="下次随访日期")
    responsible_doctor: Optional[str] = Field(None, max_length=100, description="负责医生")
    followup_checklist: Optional[dict] = Field(None, description="随访下拉列表")
    target_values: Optional[dict] = Field(None, description="目标值")
    reminder_days: int = Field(7, description="提前提醒天数")
    notes: Optional[str] = Field(None, description="备注（如随访地址等）")


class FollowupPlanCreate(FollowupPlanBase):
    """复查计划创建 Schema"""
    pass


class FollowupPlanResponse(FollowupPlanBase):
    """复查计划响应Schema"""
    id: int
    disease_id: int
    last_followup_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class FollowupRecordBase(BaseModel):
    """随访记录基础Schema"""
    followup_date: datetime = Field(..., description="随访日期")
    symptoms_assessment: Optional[str] = Field(None, description="症状评估")
    indicator_check: Optional[dict] = Field(None, description="指标检查结果")
    medication_evaluation: Optional[str] = Field(None, description="用药评价")
    lifestyle_guidance: Optional[str] = Field(None, description="生活方式指导")
    doctor_notes: Optional[str] = Field(None, description="医生备注")
    next_plan: Optional[str] = Field(None, description="下一步计划")


class FollowupRecordCreate(FollowupRecordBase):
    """随访记录创建 Schema"""
    pass


class FollowupRecordResponse(FollowupRecordBase):
    """随访记录响应Schema"""
    id: int
    followup_plan_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChronicDiseaseBase(BaseModel):
    """慢性病基础Schema"""
    disease_name: str = Field(..., max_length=100, description="疾病名称")
    icd10_code: Optional[str] = Field(None, max_length=20, description="ICD-10编码")
    diagnosis_date: Optional[date] = Field(None, description="诊断日期")
    diagnosis_hospital: Optional[str] = Field(None, max_length=200, description="诊断医院")
    diagnosis_doctor: Optional[str] = Field(None, max_length=50, description="诊断医生")
    current_treatment: Optional[str] = Field(None, description="当前治疗方案")
    control_status: ControlStatusEnum = Field(ControlStatusEnum.FAIR, description="控制状态")


class ChronicDiseaseCreate(ChronicDiseaseBase):
    """慢性病创建 Schema"""
    pass


class ChronicDiseaseUpdate(BaseModel):
    """慢性病更新 Schema"""
    disease_name: Optional[str] = Field(None, max_length=100)
    icd10_code: Optional[str] = Field(None, max_length=20)
    diagnosis_date: Optional[date] = None
    diagnosis_hospital: Optional[str] = Field(None, max_length=200)
    diagnosis_doctor: Optional[str] = Field(None, max_length=50)
    current_treatment: Optional[str] = None
    control_status: Optional[ControlStatusEnum] = None


class ChronicDiseaseResponse(ChronicDiseaseBase):
    """慢性病响应Schema"""
    id: int
    user_id: int
    is_pinned: bool = False
    indicators: List[DiseaseIndicatorResponse] = []
    followup_plans: List[FollowupPlanResponse] = []
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# 更新前向引用
MedicationScheduleResponse.model_rebuild()


# ============= 异常值预警相关 Schemas =============

class AlertLevelEnum(str, Enum):
    """预警级别枚举"""
    YELLOW = "yellow"
    ORANGE = "orange"
    RED = "red"


class IndicatorAlertBase(BaseModel):
    """指标预警基础Schema"""
    disease_id: int = Field(..., description="慢性病ID")
    indicator_id: int = Field(..., description="指标ID")
    record_id: int = Field(..., description="记录ID")
    alert_level: AlertLevelEnum = Field(..., description="预警级别")
    alert_message: str = Field(..., description="预警信息")
    indicator_value: float = Field(..., description="指标数值")
    normal_range: Optional[str] = Field(None, description="正常范围")
    suggestion: Optional[str] = Field(None, description="建议措施")


class IndicatorAlertCreate(IndicatorAlertBase):
    """指标预警创建 Schema"""
    pass


class IndicatorAlertResponse(IndicatorAlertBase):
    """指标预警响应Schema"""
    id: int
    user_id: int
    is_read: bool = False
    is_handled: bool = False
    handled_at: Optional[datetime] = None
    handler_notes: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class AlertHandleRequest(BaseModel):
    """预警处理请求Schema"""
    handler_notes: Optional[str] = Field(None, description="处理备注")


# ============= 用药依从性相关 Schemas =============

class MedicationAdherenceBase(BaseModel):
    """用药依从性基础Schema"""
    disease_id: int = Field(..., description="慢性病ID")
    user_medication_id: int = Field(..., description="用户药品ID")
    period_start: date = Field(..., description="统计周期开始")
    period_end: date = Field(..., description="统计周期结束")


class MedicationAdherenceCreate(MedicationAdherenceBase):
    """用药依从性创建 Schema"""
    pass


class MedicationAdherenceResponse(MedicationAdherenceBase):
    """用药依从性响应Schema"""
    id: int
    user_id: int
    total_doses: int
    taken_doses: int
    skipped_doses: int
    delayed_doses: int
    adherence_rate: float
    control_status_before: Optional[ControlStatusEnum] = None
    control_status_after: Optional[ControlStatusEnum] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AdherenceStatsResponse(BaseModel):
    """依从性统计响应Schema"""
    disease_id: int
    disease_name: str
    total_medications: int  # 总药品数
    average_adherence_rate: float  # 平均依从率
    recent_adherence: List[MedicationAdherenceResponse]  # 最近的依从性记录
    control_status: ControlStatusEnum  # 当前控制状态


# ============= 慢性病管理扩展 Schemas =============

class MealTypeEnum(str, Enum):
    """餐次类型枚举"""
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


class ComplicationSeverityEnum(str, Enum):
    """并发症严重程度枚举"""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


class ReminderStatusEnum(str, Enum):
    """提醒状态枚举"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


# 疾病模板
class DiseaseTemplateResponse(BaseModel):
    """疾病模板响应"""
    id: int
    disease_type: str
    display_name: str
    icd10_code: Optional[str] = None
    description: Optional[str] = None
    default_indicators: list
    created_at: datetime
    
    class Config:
        from_attributes = True


class CreateFromTemplateRequest(BaseModel):
    """基于模板创建慢性病请求"""
    disease_type: str = Field(..., description="疾病类型: hypertension/hyperlipidemia/diabetes")
    diagnosis_date: Optional[date] = None
    diagnosis_hospital: Optional[str] = Field(None, max_length=200)
    diagnosis_doctor: Optional[str] = Field(None, max_length=50)
    current_treatment: Optional[str] = None


# 批量指标记录
class BatchIndicatorRecordItem(BaseModel):
    """批量指标记录项"""
    indicator_id: int
    value: float
    measurement_date: datetime
    recorded_by: Optional[str] = None
    notes: Optional[str] = None


class BatchIndicatorRecordRequest(BaseModel):
    """批量指标记录请求"""
    records: List[BatchIndicatorRecordItem]


class BatchIndicatorRecordResponse(BaseModel):
    """批量指标记录响应"""
    saved_records: List[IndicatorRecordResponse]
    alerts: List[IndicatorAlertResponse]


# 饮食建议
class DietRecommendationResponse(BaseModel):
    """饮食建议响应"""
    id: int
    disease_type: str
    meal_type: Optional[MealTypeEnum] = None
    title: str
    content: str
    food_suggestions: Optional[list] = None
    food_restrictions: Optional[list] = None
    applicable_conditions: Optional[dict] = None
    priority: int = 0
    created_at: datetime
    
    class Config:
        from_attributes = True


class PersonalizedDietResponse(BaseModel):
    """个性化饮食建议响应"""
    disease_type: str
    breakfast: Optional[List[DietRecommendationResponse]] = None
    lunch: Optional[List[DietRecommendationResponse]] = None
    dinner: Optional[List[DietRecommendationResponse]] = None
    general_tips: List[DietRecommendationResponse] = []


# 并发症
class ComplicationRecordCreate(BaseModel):
    """并发症记录创建"""
    complication_type: str = Field(..., max_length=100)
    severity: ComplicationSeverityEnum
    discovered_date: date
    symptoms: Optional[str] = None
    treatment: Optional[str] = None
    notes: Optional[str] = None


class ComplicationRecordUpdate(BaseModel):
    """并发症记录更新"""
    severity: Optional[ComplicationSeverityEnum] = None
    symptoms: Optional[str] = None
    treatment: Optional[str] = None
    is_resolved: Optional[bool] = None
    resolved_date: Optional[date] = None
    notes: Optional[str] = None


class ComplicationRecordResponse(BaseModel):
    """并发症记录响应"""
    id: int
    disease_id: int
    complication_type: str
    severity: ComplicationSeverityEnum
    discovered_date: date
    symptoms: Optional[str] = None
    treatment: Optional[str] = None
    is_resolved: bool = False
    resolved_date: Optional[date] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# 运动建议
class ExerciseRecommendationResponse(BaseModel):
    """运动建议响应"""
    id: int
    disease_type: str
    title: str
    exercise_type: str
    duration_minutes: Optional[int] = None
    frequency_per_week: Optional[int] = None
    intensity: Optional[str] = None
    description: str
    precautions: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class PersonalizedExerciseResponse(BaseModel):
    """个性化运动建议响应"""
    disease_type: str
    recommended_exercises: List[ExerciseRecommendationResponse]
    current_status: Optional[str] = None
    safety_tips: List[str] = []


# 用药提醒
class MedicationReminderCreate(BaseModel):
    """用药提醒创建"""
    disease_id: int
    user_medication_id: Optional[int] = None
    reminder_time: str = Field(..., description="提醒时间 HH:MM:SS")
    reminder_days: List[int] = Field(..., description="提醒日期 [0-6]，0=周日")
    advance_minutes: int = Field(0, ge=0)
    repeat_interval_minutes: Optional[int] = None


class MedicationReminderUpdate(BaseModel):
    """用药提醒更新"""
    reminder_time: Optional[str] = None
    reminder_days: Optional[List[int]] = None
    status: Optional[ReminderStatusEnum] = None
    advance_minutes: Optional[int] = None
    repeat_interval_minutes: Optional[int] = None


class MedicationReminderResponse(BaseModel):
    """用药提醒响应"""
    id: int
    user_id: int
    disease_id: int
    user_medication_id: Optional[int] = None
    reminder_time: Any
    reminder_days: list
    status: Any
    advance_minutes: int = 0
    repeat_interval_minutes: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# 数据导出
class ExportRequest(BaseModel):
    """导出请求"""
    disease_ids: List[int] = Field(..., description="要导出的慢性病ID列表")
    format: str = Field("csv", description="导出格式: csv/pdf")
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    include_indicators: bool = True
    include_medications: bool = False
    include_complications: bool = False


class ExportTaskResponse(BaseModel):
    """导出任务响应"""
    task_id: str
    status: str
    download_url: Optional[str] = None
    expires_at: Optional[datetime] = None
