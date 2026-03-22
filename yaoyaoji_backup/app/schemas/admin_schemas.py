"""
管理员后台 Schemas - 数据验证和序列化
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any, TypeVar, Generic
from datetime import datetime


T = TypeVar("T")


# ============= 查询参数 Schemas =============

class AdminUserListParams(BaseModel):
    """用户列表查询参数"""
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    search: Optional[str] = None
    is_admin: Optional[bool] = None
    is_active: Optional[bool] = None


# ============= 用户管理 Schemas =============

class AdminUserUpdate(BaseModel):
    """管理员更新用户"""
    is_admin: Optional[bool] = None
    is_active: Optional[bool] = None
    email: Optional[str] = None
    real_name: Optional[str] = None


class AdminUserResponse(BaseModel):
    """管理员视角的用户信息"""
    id: int
    username: str
    email: Optional[str] = None
    real_name: Optional[str] = None
    is_admin: bool
    is_active: bool
    created_at: Optional[datetime] = None
    medication_count: int = 0
    schedule_count: int = 0
    family_name: Optional[str] = None

    model_config = {"from_attributes": True}


# ============= 分页响应 Schemas =============

class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应"""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int


# ============= 仪表盘 Schemas =============

class OnlineUserInfo(BaseModel):
    """在线用户信息"""
    id: int
    username: str
    real_name: Optional[str] = None
    avatar: Optional[str] = None
    is_admin: bool = False
    connected_at: Optional[datetime] = None


class DashboardStats(BaseModel):
    """仪表盘统计"""
    total_users: int
    active_users: int
    online_users: int = 0
    total_medicines: int
    total_diseases: int
    total_schedules: int
    new_users_today: int
    new_users_this_week: int
    user_growth_trend: List[dict]


# ============= 药品管理 Schemas =============

class MedicineCreate(BaseModel):
    """创建药品"""
    name: str
    generic_name: Optional[str] = None
    manufacturer: Optional[str] = None
    ingredients: Optional[str] = None
    efficacy: Optional[str] = None
    contraindications: Optional[str] = None
    side_effects: Optional[str] = None
    image_url: Optional[str] = None


class MedicineUpdate(BaseModel):
    """更新药品"""
    name: Optional[str] = None
    generic_name: Optional[str] = None
    manufacturer: Optional[str] = None
    ingredients: Optional[str] = None
    efficacy: Optional[str] = None
    contraindications: Optional[str] = None
    side_effects: Optional[str] = None
    image_url: Optional[str] = None


class MedicineResponse(BaseModel):
    """药品响应"""
    id: int
    name: str
    generic_name: Optional[str] = None
    manufacturer: Optional[str] = None
    ingredients: Optional[str] = None
    efficacy: Optional[str] = None
    contraindications: Optional[str] = None
    side_effects: Optional[str] = None
    image_url: Optional[str] = None
    created_at: datetime
    users: List[str] = []

    model_config = {"from_attributes": True}


# ============= 疾病管理 Schemas =============

class DiseaseCreate(BaseModel):
    """创建疾病"""
    name: str
    aliases: Optional[str] = None
    description: Optional[str] = None
    recommended: Optional[str] = None
    avoid: Optional[str] = None


class DiseaseUpdate(BaseModel):
    """更新疾病"""
    name: Optional[str] = None
    aliases: Optional[str] = None
    description: Optional[str] = None
    recommended: Optional[str] = None
    avoid: Optional[str] = None


class DiseaseResponse(BaseModel):
    """疾病响应"""
    id: int
    name: str
    aliases: Optional[str] = None
    description: Optional[str] = None
    recommended: Optional[str] = None
    avoid: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ============= 系统监控 Schemas =============

class SystemHealth(BaseModel):
    """系统健康状态"""
    status: str
    database: str
    uptime: str


class DbStats(BaseModel):
    """数据库统计"""
    users: int
    medicines: int
    diseases: int
    user_medications: int
    medication_schedules: int
    medication_records: int


# ============= 慢性病模板管理 Schemas =============

class DiseaseTemplateCreate(BaseModel):
    """创建疾病模板"""
    disease_type: str = Field(..., max_length=50)
    display_name: str = Field(..., max_length=100)
    icd10_code: Optional[str] = Field(None, max_length=20)
    description: Optional[str] = None
    default_indicators: List[dict] = Field(default_factory=list)


class DiseaseTemplateUpdate(BaseModel):
    """更新疾病模板"""
    disease_type: Optional[str] = None
    display_name: Optional[str] = None
    icd10_code: Optional[str] = None
    description: Optional[str] = None
    default_indicators: Optional[List[dict]] = None


class DiseaseTemplateResponse(BaseModel):
    """疾病模板响应"""
    id: int
    disease_type: str
    display_name: str
    icd10_code: Optional[str] = None
    description: Optional[str] = None
    default_indicators: Any = None
    created_at: datetime

    model_config = {"from_attributes": True}
