"""
管理员后台路由
"""
import math
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import func, or_, text
from sqlalchemy.orm import Session

from app.auth import require_admin
from app.database import get_db
from app.models.models import (
    User, Medicine, Disease, MedicationSchedule, MedicationRecord, UserMedication, MedicationStatus,
    DiseaseTemplate, ChronicDisease,
    SymptomRecord, EmergencyContact, HealthProfile, AllergyRecord, FamilyHistory, SurgeryRecord,
    CheckupReport, VaccinationRecord, ChatSession, ChatMessage, FamilyMember,
    IndicatorAlert, MedicationAdherence, MedicationReminder,
    DiseaseIndicator, IndicatorRecord, FollowupPlan, FollowupRecord, ComplicationRecord
)
from app.schemas.admin_schemas import (
    DashboardStats, AdminUserResponse, AdminUserUpdate, PaginatedResponse,
    MedicineCreate, MedicineUpdate, MedicineResponse,
    DiseaseCreate, DiseaseUpdate, DiseaseResponse,
    DiseaseTemplateCreate, DiseaseTemplateUpdate, DiseaseTemplateResponse,
    DbStats, OnlineUserInfo
)

from app.websocket.manager import manager

admin_router = APIRouter(prefix="/api/admin", tags=["管理员后台"])


@admin_router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
) -> DashboardStats:
    """
    获取仪表盘统计数据
    
    返回:
    - 用户总数、活跃用户数、药品总数、疾病总数、用药计划总数
    - 今日新增用户数和本周新增用户数
    - 最近 30 天用户增长趋势数据（按日期升序排列）
    
    活跃用户定义: 最近 7 天内有用药记录的独立用户
    """
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=7)
    month_start = today_start - timedelta(days=30)

    # Step 1: 基础计数
    total_users = db.query(func.count(User.id)).scalar() or 0
    total_medicines = db.query(func.count(Medicine.id)).scalar() or 0
    total_diseases = db.query(func.count(Disease.id)).scalar() or 0
    total_schedules = db.query(func.count(MedicationSchedule.id)).scalar() or 0

    # Step 2: 活跃用户（7天内有登录的独立用户）
    active_users = db.query(func.count(User.id)).filter(
        User.last_login >= week_start,
        User.last_login.isnot(None)
    ).scalar() or 0

    # 在线用户（通过 WebSocket 心跳实时检测）
    online_users = manager.get_online_count()

    # Step 3: 新增用户
    new_users_today = db.query(func.count(User.id)).filter(
        User.created_at >= today_start
    ).scalar() or 0
    
    new_users_this_week = db.query(func.count(User.id)).filter(
        User.created_at >= week_start
    ).scalar() or 0

    # Step 4: 用户增长趋势（近30天）
    trend_query = (
        db.query(
            func.date(User.created_at).label('date'),
            func.count(User.id).label('count')
        )
        .filter(User.created_at >= month_start)
        .group_by(func.date(User.created_at))
        .order_by(func.date(User.created_at).asc())
        .all()
    )

    user_growth_trend = [
        {"date": str(row.date), "count": row.count} 
        for row in trend_query
    ]

    return DashboardStats(
        total_users=total_users,
        active_users=active_users,
        online_users=online_users,
        total_medicines=total_medicines,
        total_diseases=total_diseases,
        total_schedules=total_schedules,
        new_users_today=new_users_today,
        new_users_this_week=new_users_this_week,
        user_growth_trend=user_growth_trend
    )


@admin_router.get("/online-users", response_model=list[OnlineUserInfo])
async def get_online_users(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
) -> list[OnlineUserInfo]:
    """获取当前在线用户列表"""
    details = manager.get_online_user_details()
    if not details:
        return []

    user_ids = [d["user_id"] for d in details]
    users = db.query(User).filter(User.id.in_(user_ids)).all()
    user_map = {u.id: u for u in users}

    connected_map = {d["user_id"]: d["connected_at"] for d in details}

    result = []
    for uid in user_ids:
        u = user_map.get(uid)
        if u:
            result.append(OnlineUserInfo(
                id=u.id,
                username=u.username,
                real_name=u.real_name,
                avatar=u.avatar,
                is_admin=u.is_admin,
                connected_at=connected_map.get(uid)
            ))
    return result


@admin_router.get("/users", response_model=PaginatedResponse[AdminUserResponse])
async def admin_list_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词（用户名/邮箱/真实姓名）"),
    is_admin: Optional[bool] = Query(None, description="筛选管理员"),
    is_active: Optional[bool] = Query(None, description="筛选启用状态"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
) -> PaginatedResponse[AdminUserResponse]:
    """
    获取用户列表（分页、搜索、筛选）
    
    - 支持分页（page, page_size）
    - 支持搜索（username/email/real_name 模糊匹配）
    - 支持筛选（is_admin, is_active）
    - 返回每个用户的药箱药品数和用药计划数
    - 按 created_at 降序排列
    """
    query = db.query(User)

    # Step 1: 应用搜索条件
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                User.username.ilike(search_pattern),
                User.email.ilike(search_pattern),
                User.real_name.ilike(search_pattern)
            )
        )

    # Step 2: 应用筛选条件
    if is_admin is not None:
        query = query.filter(User.is_admin == is_admin)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    # Step 3: 计算总数
    total = query.count()
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    # Step 4: 分页查询，按 created_at 降序排列
    users = (
        query.order_by(User.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    # Step 5: 附加统计信息
    items = []
    for user in users:
        # 药箱药品数（活跃状态）
        medication_count = db.query(func.count(UserMedication.id)).filter(
            UserMedication.user_id == user.id,
            UserMedication.status == MedicationStatus.ACTIVE
        ).scalar() or 0

        # 用药计划数
        schedule_count = db.query(func.count(MedicationSchedule.id)).join(
            UserMedication, MedicationSchedule.user_medication_id == UserMedication.id
        ).filter(
            UserMedication.user_id == user.id
        ).scalar() or 0

        # 家庭名称
        family_name = user.family.name if user.family else None

        items.append(AdminUserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            real_name=user.real_name,
            is_admin=user.is_admin,
            is_active=user.is_active,
            created_at=user.created_at,
            medication_count=medication_count,
            schedule_count=schedule_count,
            family_name=family_name
        ))

    return PaginatedResponse[AdminUserResponse](
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@admin_router.get("/users/{user_id}", response_model=AdminUserResponse)
async def admin_get_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
) -> AdminUserResponse:
    """
    获取用户详情
    
    返回用户完整信息，包含药箱药品数、用药计划数和所属家庭名称
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 药箱药品数（活跃状态）
    medication_count = db.query(func.count(UserMedication.id)).filter(
        UserMedication.user_id == user.id,
        UserMedication.status == MedicationStatus.ACTIVE
    ).scalar() or 0

    # 用药计划数
    schedule_count = db.query(func.count(MedicationSchedule.id)).join(
        UserMedication, MedicationSchedule.user_medication_id == UserMedication.id
    ).filter(
        UserMedication.user_id == user.id
    ).scalar() or 0

    # 家庭名称
    family_name = user.family.name if user.family else None

    return AdminUserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        real_name=user.real_name,
        is_admin=user.is_admin,
        is_active=user.is_active,
        created_at=user.created_at,
        medication_count=medication_count,
        schedule_count=schedule_count,
        family_name=family_name
    )


@admin_router.patch("/users/{user_id}", response_model=AdminUserResponse)
async def admin_update_user(
    user_id: int,
    update_data: AdminUserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
) -> AdminUserResponse:
    """
    更新用户信息
    
    支持更新 is_active、is_admin、email、real_name 字段
    
    校验规则:
    - 不能禁用自己的账号
    - 系统至少保留一个管理员
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 校验：不能禁用自己的账号
    if update_data.is_active is False and user.id == admin.id:
        raise HTTPException(status_code=400, detail="不能禁用自己的账号")

    # 校验：系统至少保留一个管理员
    if update_data.is_admin is False and user.is_admin:
        admin_count = db.query(func.count(User.id)).filter(
            User.is_admin == True,
            User.id != user_id
        ).scalar() or 0
        if admin_count == 0:
            raise HTTPException(status_code=400, detail="系统至少需要保留一个管理员")

    # 更新字段
    if update_data.is_admin is not None:
        user.is_admin = update_data.is_admin
    if update_data.is_active is not None:
        user.is_active = update_data.is_active
    if update_data.email is not None:
        user.email = update_data.email
    if update_data.real_name is not None:
        user.real_name = update_data.real_name

    db.commit()
    db.refresh(user)

    # 返回更新后的用户信息
    medication_count = db.query(func.count(UserMedication.id)).filter(
        UserMedication.user_id == user.id,
        UserMedication.status == MedicationStatus.ACTIVE
    ).scalar() or 0

    schedule_count = db.query(func.count(MedicationSchedule.id)).join(
        UserMedication, MedicationSchedule.user_medication_id == UserMedication.id
    ).filter(
        UserMedication.user_id == user.id
    ).scalar() or 0

    family_name = user.family.name if user.family else None

    return AdminUserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        real_name=user.real_name,
        is_admin=user.is_admin,
        is_active=user.is_active,
        created_at=user.created_at,
        medication_count=medication_count,
        schedule_count=schedule_count,
        family_name=family_name
    )


@admin_router.delete("/users/{user_id}")
async def admin_delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    删除用户
    
    级联处理关联的 user_medications、schedules 和 records 数据
    
    校验规则:
    - 不能删除自己的账号
    - 系统至少保留一个管理员
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 校验：不能删除自己的账号
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="不能删除自己的账号")

    # 校验：系统至少保留一个管理员
    if user.is_admin:
        admin_count = db.query(func.count(User.id)).filter(
            User.is_admin == True,
            User.id != user_id
        ).scalar() or 0
        if admin_count == 0:
            raise HTTPException(status_code=400, detail="系统至少需要保留一个管理员")

    # 级联删除关联数据
    # 1. 删除用药记录 → 用药计划 → 用户药箱
    user_medication_ids = db.query(UserMedication.id).filter(
        UserMedication.user_id == user_id
    ).subquery()
    
    schedule_ids = db.query(MedicationSchedule.id).filter(
        MedicationSchedule.user_medication_id.in_(user_medication_ids)
    ).subquery()
    
    db.query(MedicationRecord).filter(
        MedicationRecord.schedule_id.in_(schedule_ids)
    ).delete(synchronize_session=False)

    db.query(MedicationSchedule).filter(
        MedicationSchedule.user_medication_id.in_(user_medication_ids)
    ).delete(synchronize_session=False)

    # 删除用药提醒
    db.query(MedicationReminder).filter(
        MedicationReminder.user_id == user_id
    ).delete(synchronize_session=False)

    # 删除用药依从性记录
    db.query(MedicationAdherence).filter(
        MedicationAdherence.user_id == user_id
    ).delete(synchronize_session=False)

    db.query(UserMedication).filter(
        UserMedication.user_id == user_id
    ).delete(synchronize_session=False)

    # 2. 删除慢性病相关数据
    chronic_disease_ids = db.query(ChronicDisease.id).filter(
        ChronicDisease.user_id == user_id
    ).subquery()

    db.query(IndicatorAlert).filter(
        IndicatorAlert.user_id == user_id
    ).delete(synchronize_session=False)

    followup_plan_ids = db.query(FollowupPlan.id).filter(
        FollowupPlan.disease_id.in_(chronic_disease_ids)
    ).subquery()
    db.query(FollowupRecord).filter(
        FollowupRecord.followup_plan_id.in_(followup_plan_ids)
    ).delete(synchronize_session=False)
    db.query(FollowupPlan).filter(
        FollowupPlan.disease_id.in_(chronic_disease_ids)
    ).delete(synchronize_session=False)

    db.query(IndicatorRecord).filter(
        IndicatorRecord.disease_id.in_(chronic_disease_ids)
    ).delete(synchronize_session=False)
    db.query(DiseaseIndicator).filter(
        DiseaseIndicator.disease_id.in_(chronic_disease_ids)
    ).delete(synchronize_session=False)

    db.query(ComplicationRecord).filter(
        ComplicationRecord.disease_id.in_(chronic_disease_ids)
    ).delete(synchronize_session=False)

    db.query(ChronicDisease).filter(
        ChronicDisease.user_id == user_id
    ).delete(synchronize_session=False)

    # 3. 删除症状记录
    db.query(SymptomRecord).filter(
        SymptomRecord.user_id == user_id
    ).delete(synchronize_session=False)

    # 4. 删除健康档案及子表
    profile = db.query(HealthProfile).filter(HealthProfile.user_id == user_id).first()
    if profile:
        db.query(AllergyRecord).filter(AllergyRecord.profile_id == profile.id).delete(synchronize_session=False)
        db.query(FamilyHistory).filter(FamilyHistory.profile_id == profile.id).delete(synchronize_session=False)
        db.query(SurgeryRecord).filter(SurgeryRecord.profile_id == profile.id).delete(synchronize_session=False)
        db.query(CheckupReport).filter(CheckupReport.profile_id == profile.id).delete(synchronize_session=False)
        db.query(VaccinationRecord).filter(VaccinationRecord.profile_id == profile.id).delete(synchronize_session=False)
        db.delete(profile)

    # 5. 删除聊天记录
    session_ids = db.query(ChatSession.id).filter(ChatSession.user_id == user_id).subquery()
    db.query(ChatMessage).filter(ChatMessage.session_id.in_(session_ids)).delete(synchronize_session=False)
    db.query(ChatSession).filter(ChatSession.user_id == user_id).delete(synchronize_session=False)

    # 6. 删除紧急联系人
    db.query(EmergencyContact).filter(
        EmergencyContact.user_id == user_id
    ).delete(synchronize_session=False)

    # 7. 删除家庭成员（被监护人）
    db.query(FamilyMember).filter(
        FamilyMember.guardian_id == user_id
    ).delete(synchronize_session=False)

    # 8. 清除代记录人引用（置空而非删除）
    db.query(MedicationRecord).filter(
        MedicationRecord.recorded_by == user_id
    ).update({"recorded_by": None}, synchronize_session=False)
    db.query(SymptomRecord).filter(
        SymptomRecord.recorded_by == user_id
    ).update({"recorded_by": None}, synchronize_session=False)

    # 9. 删除用户
    db.delete(user)
    db.commit()

    return {"message": "用户删除成功"}


# ============= 药品管理 API =============

@admin_router.get("/medicines", response_model=PaginatedResponse)
async def admin_list_medicines(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词（药品名称）"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    获取药品列表（分页、搜索）
    """
    query = db.query(Medicine)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(Medicine.name.ilike(search_pattern))

    total = query.count()
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    medicines = (
        query.order_by(Medicine.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    items = []
    for m in medicines:
        data = MedicineResponse.model_validate(m)
        # 查询使用该药品的用户
        user_names = (
            db.query(User.username)
            .join(UserMedication, UserMedication.user_id == User.id)
            .filter(UserMedication.medicine_id == m.id)
            .all()
        )
        data.users = [u[0] for u in user_names]
        items.append(data)

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@admin_router.post("/medicines", response_model=MedicineResponse, status_code=201)
async def admin_create_medicine(
    medicine_data: MedicineCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    创建药品
    """
    medicine = Medicine(
        name=medicine_data.name,
        generic_name=medicine_data.generic_name,
        manufacturer=medicine_data.manufacturer,
        ingredients=medicine_data.ingredients,
        efficacy=medicine_data.efficacy,
        contraindications=medicine_data.contraindications,
        side_effects=medicine_data.side_effects,
        image_url=medicine_data.image_url
    )
    db.add(medicine)
    db.commit()
    db.refresh(medicine)

    return MedicineResponse.model_validate(medicine)


@admin_router.patch("/medicines/{medicine_id}", response_model=MedicineResponse)
async def admin_update_medicine(
    medicine_id: int,
    update_data: MedicineUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    更新药品
    """
    medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="药品不存在")

    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        if value is not None:
            setattr(medicine, key, value)

    db.commit()
    db.refresh(medicine)

    return MedicineResponse.model_validate(medicine)


@admin_router.delete("/medicines/{medicine_id}")
async def admin_delete_medicine(
    medicine_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    删除药品
    
    检查是否有活跃用户药箱引用，有则拒绝删除
    """
    medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
    if not medicine:
        raise HTTPException(status_code=404, detail="药品不存在")

    # 检查是否有活跃用户药箱引用
    active_refs = db.query(func.count(UserMedication.id)).filter(
        UserMedication.medicine_id == medicine_id,
        UserMedication.status == MedicationStatus.ACTIVE
    ).scalar() or 0

    if active_refs > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"该药品正在被 {active_refs} 个用户使用，无法删除"
        )

    # 删除所有非活跃的用户药箱引用，避免外键约束阻止删除
    inactive_refs = db.query(UserMedication).filter(
        UserMedication.medicine_id == medicine_id,
        UserMedication.status != MedicationStatus.ACTIVE
    ).all()
    for ref in inactive_refs:
        # 先删除关联的用药计划
        for schedule in ref.schedules:
            db.query(MedicationRecord).filter(
                MedicationRecord.schedule_id == schedule.id
            ).delete()
            db.delete(schedule)
        db.delete(ref)

    db.delete(medicine)
    db.commit()

    return {"message": "药品删除成功"}


# ============= 疾病管理 API =============

@admin_router.get("/diseases", response_model=PaginatedResponse)
async def admin_list_diseases(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    search: Optional[str] = Query(None, description="搜索关键词（疾病名称）"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    获取疾病列表（分页、搜索）
    """
    query = db.query(Disease)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(Disease.name.ilike(search_pattern))

    total = query.count()
    total_pages = math.ceil(total / page_size) if total > 0 else 1

    diseases = (
        query.order_by(Disease.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    items = [DiseaseResponse.model_validate(d) for d in diseases]

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@admin_router.post("/diseases", response_model=DiseaseResponse, status_code=201)
async def admin_create_disease(
    disease_data: DiseaseCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    创建疾病
    """
    disease = Disease(
        name=disease_data.name,
        aliases=disease_data.aliases,
        description=disease_data.description,
        recommended=disease_data.recommended,
        avoid=disease_data.avoid
    )
    db.add(disease)
    db.commit()
    db.refresh(disease)

    return DiseaseResponse.model_validate(disease)


@admin_router.patch("/diseases/{disease_id}", response_model=DiseaseResponse)
async def admin_update_disease(
    disease_id: int,
    update_data: DiseaseUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    更新疾病
    """
    disease = db.query(Disease).filter(Disease.id == disease_id).first()
    if not disease:
        raise HTTPException(status_code=404, detail="疾病不存在")

    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        if value is not None:
            setattr(disease, key, value)

    db.commit()
    db.refresh(disease)

    return DiseaseResponse.model_validate(disease)


@admin_router.delete("/diseases/{disease_id}")
async def admin_delete_disease(
    disease_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    删除疾病
    """
    disease = db.query(Disease).filter(Disease.id == disease_id).first()
    if not disease:
        raise HTTPException(status_code=404, detail="疾病不存在")

    db.delete(disease)
    db.commit()

    return {"message": "疾病删除成功"}


# ============= 慢性病模板管理 API =============

@admin_router.get("/chronic/templates", response_model=PaginatedResponse)
async def admin_list_disease_templates(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, description="搜索关键词"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """获取疾病模板列表（分页、搜索）"""
    query = db.query(DiseaseTemplate)
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            or_(DiseaseTemplate.display_name.ilike(pattern), DiseaseTemplate.disease_type.ilike(pattern))
        )
    total = query.count()
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    items = query.order_by(DiseaseTemplate.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedResponse(
        items=[DiseaseTemplateResponse.model_validate(t) for t in items],
        total=total, page=page, page_size=page_size, total_pages=total_pages
    )


@admin_router.post("/chronic/templates", response_model=DiseaseTemplateResponse, status_code=201)
async def admin_create_disease_template(
    data: DiseaseTemplateCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """创建疾病模板"""
    existing = db.query(DiseaseTemplate).filter_by(disease_type=data.disease_type).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"疾病类型 '{data.disease_type}' 已存在")
    template = DiseaseTemplate(
        disease_type=data.disease_type,
        display_name=data.display_name,
        icd10_code=data.icd10_code,
        description=data.description,
        default_indicators=data.default_indicators
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    return DiseaseTemplateResponse.model_validate(template)


@admin_router.patch("/chronic/templates/{template_id}", response_model=DiseaseTemplateResponse)
async def admin_update_disease_template(
    template_id: int,
    data: DiseaseTemplateUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """更新疾病模板"""
    template = db.query(DiseaseTemplate).filter(DiseaseTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="疾病模板不存在")
    for key, value in data.model_dump(exclude_unset=True).items():
        if value is not None:
            setattr(template, key, value)
    db.commit()
    db.refresh(template)
    return DiseaseTemplateResponse.model_validate(template)


@admin_router.delete("/chronic/templates/{template_id}")
async def admin_delete_disease_template(
    template_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """删除疾病模板"""
    template = db.query(DiseaseTemplate).filter(DiseaseTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="疾病模板不存在")
    db.delete(template)
    db.commit()
    return {"message": "疾病模板删除成功"}


# ============= 用户慢性病记录 API =============

@admin_router.get("/chronic/records", response_model=PaginatedResponse)
async def admin_list_chronic_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None, description="按疾病名称或用户名搜索"),
    control_status: Optional[str] = Query(None, description="按控制状态筛选"),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """获取所有用户的慢性病记录（含用户名）"""
    query = db.query(ChronicDisease, User.username).join(User, ChronicDisease.user_id == User.id)
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            or_(ChronicDisease.disease_name.ilike(pattern), User.username.ilike(pattern))
        )
    if control_status:
        query = query.filter(ChronicDisease.control_status == control_status)
    total = query.count()
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    rows = query.order_by(ChronicDisease.updated_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    items = []
    for disease, username in rows:
        items.append({
            "id": disease.id,
            "user_id": disease.user_id,
            "username": username,
            "disease_name": disease.disease_name,
            "icd10_code": disease.icd10_code,
            "diagnosis_date": disease.diagnosis_date.isoformat() if disease.diagnosis_date else None,
            "diagnosis_hospital": disease.diagnosis_hospital,
            "diagnosis_doctor": disease.diagnosis_doctor,
            "current_treatment": disease.current_treatment,
            "control_status": disease.control_status.value if disease.control_status else None,
            "created_at": disease.created_at.isoformat() if disease.created_at else None,
            "updated_at": disease.updated_at.isoformat() if disease.updated_at else None,
        })
    return PaginatedResponse(items=items, total=total, page=page, page_size=page_size, total_pages=total_pages)


# ============= 系统监控 API =============

@admin_router.get("/system/health")
async def admin_system_health(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    系统健康检查
    """
    import time
    start_time = time.time()
    
    # 检查数据库连接
    try:
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"

    return {
        "status": "running",
        "database": db_status,
        "timestamp": datetime.now().isoformat()
    }


@admin_router.get("/system/db-stats")
async def admin_db_stats(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    数据库统计
    """
    return DbStats(
        users=db.query(func.count(User.id)).scalar() or 0,
        medicines=db.query(func.count(Medicine.id)).scalar() or 0,
        diseases=db.query(func.count(Disease.id)).scalar() or 0,
        user_medications=db.query(func.count(UserMedication.id)).scalar() or 0,
        medication_schedules=db.query(func.count(MedicationSchedule.id)).scalar() or 0,
        medication_records=db.query(func.count(MedicationRecord.id)).scalar() or 0
    )
