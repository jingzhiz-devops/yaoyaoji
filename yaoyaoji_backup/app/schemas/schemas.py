"""
Pydantic Schemas - 数据验证和序列化
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
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


class UserLogin(BaseModel):
    """用户登录Schema"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserResponse(UserBase):
    """用户响应Schema"""
    id: int
    created_at: datetime
    
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


# 更新前向引用
MedicationScheduleResponse.model_rebuild()
