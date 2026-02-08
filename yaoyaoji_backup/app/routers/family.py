# 家庭健康管理路由
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import secrets
import string

from app.database import get_db
from app.models.models import User, Family, FamilyMember, EmergencyContact, MemberRole, MedicationSchedule, UserMedication, HealthProfile
from app.schemas.schemas import MessageResponse
from app.auth import get_current_user
from pydantic import BaseModel, Field
from datetime import date, datetime

router = APIRouter(prefix="/api/family", tags=["家庭管理"])


# ============= 辅助函数 =============

def generate_invite_code(length: int = 8) -> str:
    """生成随机邀请码"""
    characters = string.ascii_uppercase + string.digits  # 大写字母 + 数字
    return ''.join(secrets.choice(characters) for _ in range(length))


# ============= Schemas =============

class FamilyCreate(BaseModel):
    name: str = Field(..., max_length=100, description="家庭名称")


class FamilyUpdate(BaseModel):
    name: str = Field(..., max_length=100, description="家庭名称")


class FamilyResponse(BaseModel):
    id: int
    name: str
    created_by: int
    invite_code: str  # 邀请码
    created_at: datetime
    member_count: int = 0
    
    class Config:
        from_attributes = True


class FamilyMemberCreate(BaseModel):
    user_id: int = Field(..., description="系统用户ID")
    role: str = Field(..., description="角色: parent/child/elderly/spouse/other")
    birth_date: date | None = None
    notes: str | None = None


class FamilyMemberUpdate(BaseModel):
    name: str | None = None
    role: str | None = None
    birth_date: date | None = None
    notes: str | None = None


class FamilyMemberResponse(BaseModel):
    id: int
    family_id: int
    guardian_id: int
    name: str
    role: str
    birth_date: date | None = None
    age: int | None = None
    notes: str | None = None
    
    class Config:
        from_attributes = True


class EmergencyContactCreate(BaseModel):
    name: str = Field(..., max_length=50, description="联系人姓名")
    relationship: str | None = Field(None, max_length=50, description="关系")
    phone: str = Field(..., max_length=20, description="电话")
    is_primary: bool = False


class EmergencyContactUpdate(BaseModel):
    name: str | None = None
    relationship: str | None = None
    phone: str | None = None
    is_primary: bool | None = None


class EmergencyContactResponse(BaseModel):
    id: int
    user_id: int
    name: str
    relationship: str | None
    phone: str
    is_primary: bool
    
    class Config:
        from_attributes = True


# ============= 家庭管理 =============

@router.get("/my-family", response_model=FamilyResponse | None)
async def get_my_family(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取我的家庭信息"""
    if not current_user.family_id:
        return None
    
    family = db.query(Family).filter(Family.id == current_user.family_id).first()
    if not family:
        return None
    
    # 统计成员数量（从User表统计）
    member_count = db.query(User).filter(
        User.family_id == family.id
    ).count()
    
    family_dict = {
        "id": family.id,
        "name": family.name,
        "created_by": family.created_by,
        "invite_code": family.invite_code,
        "created_at": family.created_at,
        "member_count": member_count
    }
    
    return family_dict


@router.post("/create-family", response_model=FamilyResponse, status_code=status.HTTP_201_CREATED)
async def create_family(
    family_data: FamilyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建家庭"""
    # 检查是否已加入家庭
    if current_user.family_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您已加入一个家庭，无法创建新家庭"
        )
    
    # 生成唯一邀请码
    invite_code = generate_invite_code()
    while db.query(Family).filter(Family.invite_code == invite_code).first():
        invite_code = generate_invite_code()  # 如果重复，重新生成
    
    # 创建家庭
    family = Family(
        name=family_data.name,
        created_by=current_user.id,
        invite_code=invite_code
    )
    db.add(family)
    db.commit()
    db.refresh(family)
    
    # 更新用户的家庭ID，自动加入到家庭成员中
    current_user.family_id = family.id
    current_user.is_family_admin = True
    current_user.relation_to_admin = "admin"  # 设置为管理员
    db.commit()
    
    return {
        "id": family.id,
        "name": family.name,
        "created_by": family.created_by,
        "invite_code": family.invite_code,
        "created_at": family.created_at,
        "member_count": 1  # 创建者自动加入
    }


@router.post("/leave-family", response_model=MessageResponse)
async def leave_family(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """退出家庭（管理员退出则解散家庭）"""
    if not current_user.family_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您还未加入任何家庭"
        )
    
    # 查询当前家庭
    family = db.query(Family).filter(Family.id == current_user.family_id).first()
    if not family:
        # 家庭不存在，直接清理当前用户
        current_user.family_id = None
        current_user.is_family_admin = False
        current_user.relation_to_admin = None
        db.commit()
        return MessageResponse(message="已退出家庭")
    
    if family.created_by == current_user.id:
        # 管理员退出：解散家庭，清理所有成员关联
        users_in_family = db.query(User).filter(User.family_id == family.id).all()
        for u in users_in_family:
            u.family_id = None
            u.is_family_admin = False
            u.relation_to_admin = None
        # 删除家庭记录
        db.delete(family)
        db.commit()
        return MessageResponse(message="家庭已解散")
    else:
        # 普通成员退出：仅移除自己的家庭关联
        current_user.family_id = None
        current_user.is_family_admin = False
        current_user.relation_to_admin = None
        db.commit()
        return MessageResponse(message="已退出家庭")


@router.patch("/update-family", response_model=FamilyResponse)
async def update_family(
    family_data: FamilyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新家庭信息"""
    if not current_user.family_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您还未加入任何家庭"
        )
    
    # 获取家庭
    family = db.query(Family).filter(Family.id == current_user.family_id).first()
    if not family:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="家庭不存在"
        )
    
    # 检查是否是创建者（只有创庻者才能修改）
    if family.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有家庭创庻者才能修改家庭信息"
        )
    
    # 更新家庭名称
    family.name = family_data.name
    db.commit()
    db.refresh(family)
    
    # 统计成员数量（从User表统计）
    member_count = db.query(User).filter(
        User.family_id == family.id
    ).count()
    
    return {
        "id": family.id,
        "name": family.name,
        "created_by": family.created_by,
        "invite_code": family.invite_code,
        "created_at": family.created_at,
        "member_count": member_count
    }


class JoinFamilyRequest(BaseModel):
    invite_code: str = Field(..., min_length=6, max_length=20, description="邀请码")


@router.post("/join-family", response_model=MessageResponse)
async def join_family_by_invite_code(
    request: JoinFamilyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """通过邀请码加入家庭"""
    # 检查是否已加入家庭
    if current_user.family_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您已加入一个家庭，请先退出后再加入新家庭"
        )
    
    # 查找家庭
    family = db.query(Family).filter(
        Family.invite_code == request.invite_code.upper()  # 转为大写
    ).first()
    
    if not family:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="邀请码无效，请检查后重试"
        )
    
    # 加入家庭
    current_user.family_id = family.id
    current_user.is_family_admin = False
    current_user.relation_to_admin = "member"  # 普通成员
    db.commit()
    
    return MessageResponse(message=f"成功加入家庭：{family.name}")


# ============= 家庭成员管理 =============

@router.get("/members", response_model=List[FamilyMemberResponse])
async def get_family_members(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取家庭成员列表（从 User 表查询）"""
    if not current_user.family_id:
        return []
    
    # 查询同一家庭的所有成员（包括自己）
    members = db.query(User).filter(
        User.family_id == current_user.family_id
    ).order_by(User.id.asc()).all()
    
    result = []
    today = date.today()
    for member in members:
        # 计算年龄
        age = None
        if member.birth_date:
            age = today.year - member.birth_date.year
            if (today.month, today.day) < (member.birth_date.month, member.birth_date.day):
                age -= 1
        
        member_dict = {
            "id": member.id,
            "family_id": member.family_id,
            "guardian_id": current_user.id,  # 当前用户作为查看者
            "name": member.username,  # 使用系统账号名
            "role": member.relation_to_admin or "other",
            "birth_date": member.birth_date,
            "age": age,
            "notes": member.member_notes
        }
        
        result.append(member_dict)
    
    return result


@router.patch("/members/{member_id}", response_model=FamilyMemberResponse)
async def update_family_member(
    member_id: int,
    update_data: FamilyMemberUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """编辑家庭成员信息（更新出生日期、备注等）"""
    # 查找目标用户
    target_user = db.query(User).filter(
        User.id == member_id,
        User.family_id == current_user.family_id
    ).first()
    
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="成员不存在"
        )
    
    # 更新字段
    if update_data.role is not None:
        target_user.relation_to_admin = update_data.role
    if update_data.birth_date is not None:
        target_user.birth_date = update_data.birth_date
        # 同步更新健康档案的出生日期
        health_profile = db.query(HealthProfile).filter(
            HealthProfile.user_id == target_user.id
        ).first()
        if health_profile:
            health_profile.birth_date = update_data.birth_date
    if update_data.notes is not None:
        target_user.member_notes = update_data.notes
    
    db.commit()
    db.refresh(target_user)
    
    # 计算年龄
    age = None
    if target_user.birth_date:
        today = date.today()
        age = today.year - target_user.birth_date.year
        if (today.month, today.day) < (target_user.birth_date.month, target_user.birth_date.day):
            age -= 1
    
    return {
        "id": target_user.id,
        "family_id": target_user.family_id,
        "guardian_id": current_user.id,
        "name": target_user.username,
        "role": target_user.relation_to_admin or "other",
        "birth_date": target_user.birth_date,
        "age": age,
        "notes": target_user.member_notes
    }


@router.delete("/members/{member_id}", response_model=MessageResponse)
async def remove_family_member(
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """移除家庭成员（将用户从家庭中移除）"""
    # 查找目标用户
    target_user = db.query(User).filter(
        User.id == member_id,
        User.family_id == current_user.family_id
    ).first()
    
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="成员不存在"
        )
    
    # 不能移除自己
    if target_user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能移除自己，请使用退出家庭功能"
        )
    
    # 将用户从家庭中移除
    target_user.family_id = None
    target_user.relation_to_admin = None
    target_user.is_family_admin = False
    
    db.commit()
    
    return MessageResponse(message=f"已将 {target_user.real_name or target_user.username} 移除出家庭")


# ============= 紧急联系人 =============

@router.get("/emergency-contacts", response_model=List[EmergencyContactResponse])
async def get_emergency_contacts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取紧急联系人列表"""
    contacts = db.query(EmergencyContact).filter(
        EmergencyContact.user_id == current_user.id
    ).order_by(EmergencyContact.is_primary.desc(), EmergencyContact.id.asc()).all()
    
    return contacts


@router.post("/emergency-contacts", response_model=EmergencyContactResponse, status_code=status.HTTP_201_CREATED)
async def add_emergency_contact(
    contact_data: EmergencyContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """添加紧急联系人"""
    # 如果设为主联系人，取消其他主联系人
    if contact_data.is_primary:
        db.query(EmergencyContact).filter(
            EmergencyContact.user_id == current_user.id,
            EmergencyContact.is_primary == True
        ).update({"is_primary": False})
    
    contact = EmergencyContact(
        user_id=current_user.id,
        **contact_data.model_dump()
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    
    return contact


@router.patch("/emergency-contacts/{contact_id}", response_model=EmergencyContactResponse)
async def update_emergency_contact(
    contact_id: int,
    update_data: EmergencyContactUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新紧急联系人"""
    contact = db.query(EmergencyContact).filter(
        EmergencyContact.id == contact_id,
        EmergencyContact.user_id == current_user.id
    ).first()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="联系人不存在"
        )
    
    # 如果设为主联系人，取消其他主联系人
    if update_data.is_primary:
        db.query(EmergencyContact).filter(
            EmergencyContact.user_id == current_user.id,
            EmergencyContact.id != contact_id,
            EmergencyContact.is_primary == True
        ).update({"is_primary": False})
    
    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(contact, key, value)
    
    db.commit()
    db.refresh(contact)
    
    return contact


@router.delete("/emergency-contacts/{contact_id}", response_model=MessageResponse)
async def delete_emergency_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除紧急联系人"""
    contact = db.query(EmergencyContact).filter(
        EmergencyContact.id == contact_id,
        EmergencyContact.user_id == current_user.id
    ).first()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="联系人不存在"
        )
    
    db.delete(contact)
    db.commit()
    
    return MessageResponse(message="联系人已删除")


# ============= 家庭用药信息 =============

class FamilyMemberMedication(BaseModel):
    """家庭成员用药信息"""
    user_id: int
    username: str
    real_name: str | None
    relation: str | None
    medication_count: int  # 用药种类数
    today_schedules: int  # 今日用药计划数
    
    class Config:
        from_attributes = True


class SwitchAccountRequest(BaseModel):
    """切换账号请求"""
    target_user_id: int


class SwitchAccountResponse(BaseModel):
    """切换账号响应"""
    access_token: str
    token_type: str = "bearer"
    user: dict
    
    class Config:
        from_attributes = True


@router.get("/members-medication", response_model=List[FamilyMemberMedication])
async def get_family_members_medication(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取家庭成员的用药信息（排除自己）"""
    if not current_user.family_id:
        return []
    
    # 获取同一家庭的其他成员（排除自己）
    family_members = db.query(User).filter(
        User.family_id == current_user.family_id,
        User.id != current_user.id  # 排除自己
    ).all()
    
    result = []
    today = date.today()
    
    for member in family_members:
        # 统计用药种类
        from app.models.models import UserMedication, MedicationSchedule
        medication_count = db.query(UserMedication).filter(
            UserMedication.user_id == member.id
        ).count()
        
        # 统计今日用药计划
        today_schedules_count = db.query(MedicationSchedule).join(
            UserMedication
        ).filter(
            UserMedication.user_id == member.id,
            MedicationSchedule.start_date <= today,
            (MedicationSchedule.end_date >= today) | (MedicationSchedule.end_date == None)
        ).count()
        
        result.append({
            "user_id": member.id,
            "username": member.username,
            "real_name": member.real_name,
            "relation": member.relation_to_admin,
            "medication_count": medication_count,
            "today_schedules": today_schedules_count
        })
    
    return result


@router.post("/switch-account", response_model=SwitchAccountResponse)
async def switch_to_family_member(
    request: SwitchAccountRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """切换到家庭成员账号"""
    # 检查是否有家庭
    if not current_user.family_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您还未加入家庭"
        )
    
    # 获取目标用户
    target_user = db.query(User).filter(User.id == request.target_user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="目标用户不存在"
        )
    
    # 检查是否同一家庭
    if target_user.family_id != current_user.family_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只能切换到同一家庭的成员账号"
        )
    
    # 生成新的token
    from app.auth import create_access_token
    from datetime import timedelta
    from app.config import settings
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": target_user.username}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": target_user.id,
            "username": target_user.username,
            "real_name": target_user.real_name,
            "relation_to_admin": target_user.relation_to_admin,
            "email": target_user.email
        }
    }
