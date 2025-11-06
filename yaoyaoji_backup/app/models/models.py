"""  
数据库模型定义
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, Date, Time, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import enum


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)  # 手机号
    avatar = Column(String(500), nullable=True)  # 头像
    real_name = Column(String(50), nullable=True)  # 真实姓名
    birth_date = Column(Date, nullable=True)  # 出生日期
    member_notes = Column(Text, nullable=True)  # 成员备注
    relation_to_admin = Column(String(50), nullable=True)  # 与管理员的关系（父亲、母亲、配偶等）
    is_family_admin = Column(Boolean, default=True)  # 是否家庭管理员
    family_id = Column(Integer, ForeignKey("families.id"), nullable=True)  # 所属家庭
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    user_medications = relationship("UserMedication", back_populates="user")
    symptom_records = relationship("SymptomRecord", foreign_keys="SymptomRecord.user_id", back_populates="user")
    health_profile = relationship("HealthProfile", back_populates="user", uselist=False)
    family = relationship("Family", back_populates="members")
    managed_members = relationship("FamilyMember", foreign_keys="FamilyMember.guardian_id", back_populates="guardian")


class Medicine(Base):
    """药品库表"""
    __tablename__ = "medicines"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    generic_name = Column(String(100), nullable=True)  # 通用名
    manufacturer = Column(String(100), nullable=True)  # 生产厂家
    ingredients = Column(Text, nullable=True)  # 主要成分
    efficacy = Column(Text, nullable=True)  # 功效与作用
    contraindications = Column(Text, nullable=True)  # 禁忌信息
    side_effects = Column(Text, nullable=True)  # 副作用
    image_url = Column(String(500), nullable=True)  # 药品图片
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    user_medications = relationship("UserMedication", back_populates="medicine")


class MedicationStatus(str, enum.Enum):
    """用药状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"


class UserMedication(Base):
    """用户药箱表"""
    __tablename__ = "user_medications"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    medicine_id = Column(Integer, ForeignKey("medicines.id"), nullable=False)
    custom_name = Column(String(100), nullable=True)  # 自定义名称
    notes = Column(Text, nullable=True)  # 备注
    status = Column(Enum(MedicationStatus), default=MedicationStatus.ACTIVE)
    
    # 关系
    user = relationship("User", back_populates="user_medications")
    medicine = relationship("Medicine", back_populates="user_medications")
    schedules = relationship("MedicationSchedule", back_populates="user_medication")


class FrequencyType(str, enum.Enum):
    """用药频率枚举"""
    ONCE_DAILY = "once_daily"
    TWICE_DAILY = "twice_daily"
    THREE_TIMES_DAILY = "three_times_daily"
    FOUR_TIMES_DAILY = "four_times_daily"


class MedicationSchedule(Base):
    """用药计划表"""
    __tablename__ = "medication_schedules"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_medication_id = Column(Integer, ForeignKey("user_medications.id"), nullable=False)
    scheduled_times = Column(JSON, nullable=False)  # 存储多个时间的JSON数组，如["08:00:00", "12:00:00", "20:00:00"]
    dose = Column(String(50), nullable=False)  # 剂量
    frequency = Column(Enum(FrequencyType), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    
    # 关系
    user_medication = relationship("UserMedication", back_populates="schedules")
    records = relationship("MedicationRecord", back_populates="schedule")


class RecordStatus(str, enum.Enum):
    """用药记录状态枚举"""
    PENDING = "pending"
    TAKEN = "taken"
    SKIPPED = "skipped"
    DELAYED = "delayed"


class MedicationRecord(Base):
    """用药记录表"""
    __tablename__ = "medication_records"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    schedule_id = Column(Integer, ForeignKey("medication_schedules.id"), nullable=False)
    scheduled_time = Column(DateTime, nullable=False)
    actual_time = Column(DateTime, nullable=True)
    status = Column(Enum(RecordStatus), default=RecordStatus.PENDING)
    skip_reason = Column(String(200), nullable=True)
    recorded_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # 代记录人（如果为空说明是自己记录）
    
    # 关系
    schedule = relationship("MedicationSchedule", back_populates="records")


class SymptomRecord(Base):
    """症状记录表"""
    __tablename__ = "symptom_records"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    symptom_emoji = Column(String(10), nullable=True)
    symptom_text = Column(String(100), nullable=False)
    intensity = Column(Integer, nullable=False)  # 1-5级强度
    recorded_time = Column(DateTime, default=datetime.now)
    recorded_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # 代记录人（如果为空说明是自己记录）
    
    # 关系（明确指定foreign_keys避免歧义）
    user = relationship("User", foreign_keys=[user_id], back_populates="symptom_records")


class Disease(Base):
    """疾病库表"""
    __tablename__ = "diseases"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False, index=True)
    aliases = Column(Text, nullable=True)  # 别名，逗号分隔
    description = Column(Text, nullable=True)
    recommended = Column(Text, nullable=True)  # 常用药物，逗号分隔
    avoid = Column(Text, nullable=True)  # 避免搭配，逗号分隔
    created_at = Column(DateTime, default=datetime.now)


# ============= 家庭管理模块 =============

class Family(Base):
    """家庭表"""
    __tablename__ = "families"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)  # 家庭名称
    created_by = Column(Integer, nullable=False)  # 创建者ID
    invite_code = Column(String(20), unique=True, nullable=False, index=True)  # 邀请码
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    members = relationship("User", back_populates="family")
    family_members = relationship("FamilyMember", back_populates="family")


class MemberRole(str, enum.Enum):
    """成员角色枚举"""
    PARENT = "parent"  # 家长
    CHILD = "child"  # 儿童
    ELDERLY = "elderly"  # 老人
    SPOUSE = "spouse"  # 配偶
    OTHER = "other"  # 其他


class FamilyMember(Base):
    """家庭成员表（用于管理非注册用户）"""
    __tablename__ = "family_members"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False)
    guardian_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 监护人
    name = Column(String(50), nullable=False)
    role = Column(Enum(MemberRole), nullable=False)
    birth_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    family = relationship("Family", back_populates="family_members")
    guardian = relationship("User", foreign_keys=[guardian_id], back_populates="managed_members")


class EmergencyContact(Base):
    """紧急联系人表"""
    __tablename__ = "emergency_contacts"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(50), nullable=False)
    relationship = Column(String(50), nullable=True)  # 关系
    phone = Column(String(20), nullable=False)
    is_primary = Column(Boolean, default=False)  # 是否主联系人
    created_at = Column(DateTime, default=datetime.now)


# ============= 健康档案模块 =============

class HealthProfile(Base):
    """健康档案主表"""
    __tablename__ = "health_profiles"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # 基本信息
    real_name = Column(String(50), nullable=True)  # 真实姓名
    blood_type = Column(String(10), nullable=True)  # 血型
    height = Column(Integer, nullable=True)  # 身高(cm)
    weight = Column(Integer, nullable=True)  # 体重(kg)
    
    # 新增常用医学信息
    systolic_pressure = Column(Integer, nullable=True)  # 收缩压(高压) mmHg
    diastolic_pressure = Column(Integer, nullable=True)  # 舒张压(低压) mmHg
    heart_rate = Column(Integer, nullable=True)  # 心率 次/分
    blood_glucose = Column(String(20), nullable=True)  # 血糖 mmol/L
    temperature = Column(String(10), nullable=True)  # 体温 ℃
    
    chronic_diseases = Column(Text, nullable=True)  # 慢性病，逗号分隔
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    user = relationship("User", back_populates="health_profile")
    allergies = relationship("AllergyRecord", back_populates="profile")
    family_histories = relationship("FamilyHistory", back_populates="profile")
    surgeries = relationship("SurgeryRecord", back_populates="profile")
    checkups = relationship("CheckupReport", back_populates="profile")
    vaccinations = relationship("VaccinationRecord", back_populates="profile")


class AllergyRecord(Base):
    """过敏史记录"""
    __tablename__ = "allergy_records"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey("health_profiles.id"), nullable=False)
    allergen = Column(String(100), nullable=False)  # 过敏原
    allergen_type = Column(String(50), nullable=True)  # 类型：药物/食物/其他
    reaction = Column(Text, nullable=True)  # 过敏反应
    severity = Column(String(20), nullable=True)  # 严重程度
    discovered_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    profile = relationship("HealthProfile", back_populates="allergies")


class FamilyHistory(Base):
    """家族病史"""
    __tablename__ = "family_histories"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey("health_profiles.id"), nullable=False)
    relative = Column(String(50), nullable=False)  # 亲属关系
    disease = Column(String(100), nullable=False)  # 疾病
    onset_age = Column(Integer, nullable=True)  # 发病年龄
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    profile = relationship("HealthProfile", back_populates="family_histories")


class SurgeryRecord(Base):
    """手术记录"""
    __tablename__ = "surgery_records"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey("health_profiles.id"), nullable=False)
    surgery_name = Column(String(200), nullable=False)  # 手术名称
    surgery_date = Column(Date, nullable=False)
    hospital = Column(String(200), nullable=True)  # 医院
    doctor = Column(String(100), nullable=True)  # 主刀医生
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    profile = relationship("HealthProfile", back_populates="surgeries")


class CheckupReport(Base):
    """体检报告"""
    __tablename__ = "checkup_reports"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey("health_profiles.id"), nullable=False)
    checkup_date = Column(Date, nullable=False)
    checkup_type = Column(String(100), nullable=True)  # 体检类型
    hospital = Column(String(200), nullable=True)
    summary = Column(Text, nullable=True)  # 总结
    file_url = Column(String(500), nullable=True)  # 报告文件
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    profile = relationship("HealthProfile", back_populates="checkups")


class VaccinationRecord(Base):
    """疫苗接种记录"""
    __tablename__ = "vaccination_records"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey("health_profiles.id"), nullable=False)
    vaccine_name = Column(String(100), nullable=False)  # 疫苗名称
    vaccination_date = Column(Date, nullable=False)
    hospital = Column(String(200), nullable=True)
    batch_number = Column(String(100), nullable=True)  # 批次号
    next_dose_date = Column(Date, nullable=True)  # 下次接种日期
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    profile = relationship("HealthProfile", back_populates="vaccinations")


# ============= AI智能助手模块 =============

class ChatSession(Base):
    """聊天会话表"""
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=True)  # 会话标题
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    messages = relationship("ChatMessage", back_populates="session")


class ChatMessage(Base):
    """聊天消息表"""
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String(20), nullable=False)  # user/assistant
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    session = relationship("ChatSession", back_populates="messages")


class KnowledgeBase(Base):
    """知识库表"""
    __tablename__ = "knowledge_base"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    category = Column(String(50), nullable=False)  # 分类：用药/疾病/常见问题
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    keywords = Column(Text, nullable=True)  # 关键词，逗号分隔
    view_count = Column(Integer, default=0)  # 查看次数
    helpful_count = Column(Integer, default=0)  # 有帮助评价数
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
