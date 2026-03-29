"""  
数据库模型定义
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, Date, Time, ForeignKey, JSON, Boolean, Float
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
    is_admin = Column(Boolean, default=False, index=True)  # 是否管理员
    is_active = Column(Boolean, default=True, index=True)  # 账号是否启用
    is_family_admin = Column(Boolean, default=True)  # 是否家庭管理员
    family_id = Column(Integer, ForeignKey("families.id"), nullable=True)  # 所属家庭
    feishu_webhook = Column(String(500), nullable=True)  # 飞书机器人Webhook地址
    created_at = Column(DateTime, default=datetime.now)
    last_login = Column(DateTime, nullable=True)  # 最后登录时间
    
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
    purchase_date = Column(Date, nullable=True)  # 药品购入日期
    therapy_duration = Column(Integer, nullable=True)  # 吃药疗程（天数）
    remind_advance_days = Column(Integer, default=5)  # 提前提醒备药天数，默认5天
    notes = Column(Text, nullable=True)  # 备注
    
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
    birth_date = Column(Date, nullable=True)  # 出生日期
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


# ============= 慢性病管理模块 =============

class ControlStatus(str, enum.Enum):
    """慢性病控制状态枚举"""
    GOOD = "good"      # 控制良好
    FAIR = "fair"      # 控制中等
    POOR = "poor"      # 控制不良


class ChronicDisease(Base):
    """慢性病表"""
    __tablename__ = "chronic_diseases"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # 基本信息
    disease_name = Column(String(100), nullable=False)  # 疾病名称
    icd10_code = Column(String(20), nullable=True)  # ICD-10编码
    diagnosis_date = Column(Date, nullable=True)  # 诊断日期
    diagnosis_hospital = Column(String(200), nullable=True)  # 诊断医院
    diagnosis_doctor = Column(String(50), nullable=True)  # 诊断医生
    
    # 治疗信息
    current_treatment = Column(Text, nullable=True)  # 当前治疗方案
    control_status = Column(Enum(ControlStatus), default=ControlStatus.FAIR)  # 控制状态
    is_pinned = Column(Boolean, default=False)  # 是否收藏/置顶
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系（级联删除）
    user = relationship("User", foreign_keys=[user_id])
    indicators = relationship("DiseaseIndicator", back_populates="disease", cascade="all, delete-orphan")
    indicator_records = relationship("IndicatorRecord", back_populates="disease", cascade="all, delete-orphan")
    followup_plans = relationship("FollowupPlan", back_populates="disease", cascade="all, delete-orphan")


class DiseaseIndicator(Base):
    """疾病关键指标表"""
    __tablename__ = "disease_indicators"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    disease_id = Column(Integer, ForeignKey("chronic_diseases.id"), nullable=False)
    
    indicator_name = Column(String(100), nullable=False)  # 指标名称（如"收缩压"）
    normal_range_min = Column(Float, nullable=True)  # 正常范围最小值
    normal_range_max = Column(Float, nullable=True)  # 正常范围最大值
    unit = Column(String(50), nullable=True)  # 单位（如 mmHg）
    check_frequency = Column(String(50), nullable=True)  # 检查频率（daily/weekly/monthly）
    
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    disease = relationship("ChronicDisease", back_populates="indicators")
    records = relationship("IndicatorRecord", back_populates="indicator", cascade="all, delete-orphan")


class IndicatorRecord(Base):
    """指标记录表（用户填写的具体数据）"""
    __tablename__ = "indicator_records"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    disease_id = Column(Integer, ForeignKey("chronic_diseases.id"), nullable=False)
    indicator_id = Column(Integer, ForeignKey("disease_indicators.id"), nullable=False)
    
    value = Column(Float, nullable=False)  # 记录的数值
    measurement_date = Column(DateTime, nullable=False)  # 测量日期时间
    recorded_by = Column(String(50), nullable=True)  # 记录者（self/caregiver等）
    notes = Column(Text, nullable=True)  # 备注
    
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    disease = relationship("ChronicDisease", back_populates="indicator_records")
    indicator = relationship("DiseaseIndicator", back_populates="records")


class FollowupPlan(Base):
    """复查计划表"""
    __tablename__ = "followup_plans"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    disease_id = Column(Integer, ForeignKey("chronic_diseases.id"), nullable=False)
    
    frequency = Column(String(50), nullable=False)  # 频率：weekly/monthly/quarterly/yearly
    last_followup_date = Column(Date, nullable=True)  # 最后随访日期
    next_followup_date = Column(Date, nullable=False)  # 下次随访日期
    responsible_doctor = Column(String(100), nullable=True)  # 负责医生
    
    # 随访内容清单（JSON格式）
    followup_checklist = Column(JSON, nullable=True)  # [{"item": "症状评估", "done": false}]
    
    # 目标值（JSON格式）
    target_values = Column(JSON, nullable=True)  # {"血压": "<140/90", "血糖": "<7.0"}
    
    reminder_days = Column(Integer, default=7)  # 提前几天提醒
    notes = Column(Text, nullable=True)  # 备注（如随访地址等）
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    disease = relationship("ChronicDisease", back_populates="followup_plans")
    records = relationship("FollowupRecord", back_populates="plan", cascade="all, delete-orphan")


class FollowupRecord(Base):
    """随访记录表（具体的随访执行记录）"""
    __tablename__ = "followup_records"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    followup_plan_id = Column(Integer, ForeignKey("followup_plans.id"), nullable=False)
    
    followup_date = Column(DateTime, nullable=False)  # 随访日期
    symptoms_assessment = Column(Text, nullable=True)  # 症状评估
    indicator_check = Column(JSON, nullable=True)  # 指标检查结果
    medication_evaluation = Column(Text, nullable=True)  # 用药评价
    lifestyle_guidance = Column(Text, nullable=True)  # 生活方式指导
    doctor_notes = Column(Text, nullable=True)  # 医生备注
    next_plan = Column(Text, nullable=True)  # 下一步计划
    
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    plan = relationship("FollowupPlan", back_populates="records")


class AlertLevel(str, enum.Enum):
    """预警级别枚举"""
    YELLOW = "yellow"  # 黄色预警：轻微异常
    ORANGE = "orange"  # 橙色预警：中度异常
    RED = "red"        # 红色预警：严重异常


class IndicatorAlert(Base):
    """指标异常预警表"""
    __tablename__ = "indicator_alerts"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    disease_id = Column(Integer, ForeignKey("chronic_diseases.id"), nullable=False)
    indicator_id = Column(Integer, ForeignKey("disease_indicators.id"), nullable=False)
    record_id = Column(Integer, ForeignKey("indicator_records.id"), nullable=False)
    
    alert_level = Column(Enum(AlertLevel), nullable=False)  # 预警级别
    alert_message = Column(Text, nullable=False)  # 预警信息
    indicator_value = Column(Float, nullable=False)  # 触发预警的数值
    normal_range = Column(String(50), nullable=True)  # 正常范围描述
    suggestion = Column(Text, nullable=True)  # 建议措施
    
    is_read = Column(Boolean, default=False)  # 是否已读
    is_handled = Column(Boolean, default=False)  # 是否已处理
    handled_at = Column(DateTime, nullable=True)  # 处理时间
    handler_notes = Column(Text, nullable=True)  # 处理备注
    
    created_at = Column(DateTime, default=datetime.now)
    
    # 关系
    user = relationship("User", foreign_keys=[user_id])
    disease = relationship("ChronicDisease", foreign_keys=[disease_id])
    indicator = relationship("DiseaseIndicator", foreign_keys=[indicator_id])
    record = relationship("IndicatorRecord", foreign_keys=[record_id])


class MedicationAdherence(Base):
    """用药依从性追踪表"""
    __tablename__ = "medication_adherence"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    disease_id = Column(Integer, ForeignKey("chronic_diseases.id"), nullable=False)
    user_medication_id = Column(Integer, ForeignKey("user_medications.id"), nullable=False)
    
    # 统计周期（如2024-01-01到2024-01-07）
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    
    # 依从性统计
    total_doses = Column(Integer, default=0)  # 应服药次数
    taken_doses = Column(Integer, default=0)  # 实际服药次数
    skipped_doses = Column(Integer, default=0)  # 漏服次数
    delayed_doses = Column(Integer, default=0)  # 延迟服药次数
    adherence_rate = Column(Float, default=0.0)  # 依从率（0-100）
    
    # 关联的病情控制状态
    control_status_before = Column(Enum(ControlStatus), nullable=True)  # 周期开始时的控制状态
    control_status_after = Column(Enum(ControlStatus), nullable=True)  # 周期结束时的控制状态
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 关系
    user = relationship("User", foreign_keys=[user_id])
    disease = relationship("ChronicDisease", foreign_keys=[disease_id])
    user_medication = relationship("UserMedication", foreign_keys=[user_medication_id])


# ============= 慢性病管理扩展模块 =============

class DiseaseTemplate(Base):
    """疾病类型模板表"""
    __tablename__ = "disease_templates"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    disease_type = Column(String(50), unique=True, nullable=False)  # hypertension/hyperlipidemia/diabetes
    display_name = Column(String(100), nullable=False)
    icd10_code = Column(String(20), nullable=True)
    description = Column(Text, nullable=True)
    default_indicators = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.now)


class MealType(str, enum.Enum):
    """餐次类型"""
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


class DietRecommendation(Base):
    """饮食建议表"""
    __tablename__ = "diet_recommendations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    disease_type = Column(String(50), nullable=False)
    meal_type = Column(Enum(MealType), nullable=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    food_suggestions = Column(JSON, nullable=True)
    food_restrictions = Column(JSON, nullable=True)
    applicable_conditions = Column(JSON, nullable=True)
    priority = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class ComplicationSeverity(str, enum.Enum):
    """并发症严重程度"""
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


class ComplicationRecord(Base):
    """并发症记录表"""
    __tablename__ = "complication_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    disease_id = Column(Integer, ForeignKey("chronic_diseases.id"), nullable=False)
    complication_type = Column(String(100), nullable=False)
    severity = Column(Enum(ComplicationSeverity), nullable=False)
    discovered_date = Column(Date, nullable=False)
    symptoms = Column(Text, nullable=True)
    treatment = Column(Text, nullable=True)
    is_resolved = Column(Boolean, default=False)
    resolved_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    disease = relationship("ChronicDisease", foreign_keys=[disease_id])


class ExerciseRecommendation(Base):
    """运动建议表"""
    __tablename__ = "exercise_recommendations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    disease_type = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    exercise_type = Column(String(100), nullable=False)
    duration_minutes = Column(Integer, nullable=True)
    frequency_per_week = Column(Integer, nullable=True)
    intensity = Column(String(50), nullable=True)
    description = Column(Text, nullable=False)
    precautions = Column(Text, nullable=True)
    applicable_conditions = Column(JSON, nullable=True)
    priority = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)


class ReminderStatus(str, enum.Enum):
    """提醒状态"""
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


class MedicationReminder(Base):
    """用药提醒表"""
    __tablename__ = "medication_reminders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    disease_id = Column(Integer, ForeignKey("chronic_diseases.id"), nullable=False)
    user_medication_id = Column(Integer, ForeignKey("user_medications.id"), nullable=True)
    reminder_time = Column(Time, nullable=False)
    reminder_days = Column(JSON, nullable=False)
    status = Column(Enum(ReminderStatus), default=ReminderStatus.ACTIVE)
    advance_minutes = Column(Integer, default=0)
    repeat_interval_minutes = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    user = relationship("User", foreign_keys=[user_id])
    disease = relationship("ChronicDisease", foreign_keys=[disease_id])
    medication = relationship("UserMedication", foreign_keys=[user_medication_id])

