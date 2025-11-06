# 药品管理路由
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.models import User, Medicine, UserMedication
from app.schemas.schemas import (
    MedicineCreate, MedicineResponse,
    UserMedicationCreate, UserMedicationUpdate, UserMedicationResponse,
    MessageResponse
)
from app.auth import get_current_user
from app.services.conflict_checker import check_drug_interactions

router = APIRouter(prefix="/api/medicines", tags=["药品管理"])
user_med_router = APIRouter(prefix="/api/user-medications", tags=["用户药箱"])


# ============= 药品库管理 =============

@router.post("/", response_model=MedicineResponse, status_code=status.HTTP_201_CREATED)
async def create_medicine(
    medicine: MedicineCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 创建药品信息
    # 检查药品是否已存在
    existing = db.query(Medicine).filter(
        Medicine.name == medicine.name,
        Medicine.manufacturer == medicine.manufacturer
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该药品已存在"
        )
    
    db_medicine = Medicine(**medicine.model_dump())
    db.add(db_medicine)
    db.commit()
    db.refresh(db_medicine)
    
    return db_medicine


@router.get("/", response_model=List[MedicineResponse])
async def get_medicines(
    skip: int = 0,
    limit: int = 100,
    search: str | None = None,
    db: Session = Depends(get_db)
):
    # 获取药品列表（支持搜索）
    query = db.query(Medicine)
    
    if search:
        query = query.filter(
            (Medicine.name.contains(search)) |
            (Medicine.generic_name.contains(search)) |
            (Medicine.manufacturer.contains(search)) |
            (Medicine.ingredients.contains(search)) |
            (Medicine.efficacy.contains(search)) |
            (Medicine.contraindications.contains(search))
        )
    
    medicines = query.offset(skip).limit(limit).all()
    return medicines


@router.get("/{medicine_id}", response_model=MedicineResponse)
async def get_medicine(
    medicine_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 获取药品详情
    medicine = db.query(Medicine).filter(Medicine.id == medicine_id).first()
    if not medicine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="药品不存在"
        )
    
    return medicine


# ============= 用户药箱管理 =============

@user_med_router.post("/", response_model=UserMedicationResponse, status_code=status.HTTP_201_CREATED)
async def add_to_medication_box(
    user_med: UserMedicationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 添加药品到用户药箱（会检测冲突）
    # 检查药品是否存在
    medicine = db.query(Medicine).filter(Medicine.id == user_med.medicine_id).first()
    if not medicine:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="药品不存在"
        )
    
    # 检查是否已添加
    existing = db.query(UserMedication).filter(
        UserMedication.user_id == getattr(current_user, 'id'),
        UserMedication.medicine_id == user_med.medicine_id,
        UserMedication.status == "active"
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该药品已在药箱中"
        )
    
    # 检测用药冲突
    warnings = check_drug_interactions(db, getattr(current_user, 'id'), user_med.medicine_id)
    if warnings:
        # 如果有高危冲突，阻止添加
        high_warnings = [w for w in warnings if w.severity == "high"]
        if high_warnings:
            warning_msg = "; ".join([w.warning for w in high_warnings])
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"⚠️ 用药冲突警告：{warning_msg}"
            )
    
    db_user_med = UserMedication(
        user_id=getattr(current_user, 'id'),
        **user_med.model_dump()
    )
    db.add(db_user_med)
    db.commit()
    db.refresh(db_user_med)
    
    return db_user_med


@user_med_router.get("/", response_model=List[UserMedicationResponse])
async def get_my_medications(
    status_filter: str = "active",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 获取我的药箱
    query = db.query(UserMedication).filter(
        UserMedication.user_id == getattr(current_user, 'id')
    )
    
    if status_filter:
        query = query.filter(UserMedication.status == status_filter)
    
    medications = query.all()
    return medications


@user_med_router.get("/{user_med_id}", response_model=UserMedicationResponse)
async def get_user_medication(
    user_med_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 获取药箱中的单个药品详情
    user_med = db.query(UserMedication).filter(
        UserMedication.id == user_med_id,
        UserMedication.user_id == getattr(current_user, 'id')
    ).first()
    
    if not user_med:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="药品不在您的药箱中"
        )
    
    return user_med


@user_med_router.patch("/{user_med_id}", response_model=UserMedicationResponse)
async def update_user_medication(
    user_med_id: int,
    update_data: UserMedicationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 更新药箱中的药哅信息
    user_med = db.query(UserMedication).filter(
        UserMedication.id == user_med_id,
        UserMedication.user_id == getattr(current_user, 'id')
    ).first()
    
    if not user_med:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="药哅不在您的药箱中"
        )
    
    update_dict = update_data.model_dump(exclude_unset=True)
    
    # 分离药哅信息和用户药箱信息
    medicine_fields = {}
    user_med_fields = {}
    
    for key, value in update_dict.items():
        if key in ['medicine_name', 'contraindications', 'manufacturer', 'image_url']:
            # 药哅信息字段
            if key == 'medicine_name':
                medicine_fields['name'] = value
            else:
                medicine_fields[key] = value
        else:
            # 用户药箱字段
            user_med_fields[key] = value
    
    # 更新关联的药哅信息
    if medicine_fields and user_med.medicine:
        for key, value in medicine_fields.items():
            setattr(user_med.medicine, key, value)
    
    # 更新用户药箱信息
    for key, value in user_med_fields.items():
        setattr(user_med, key, value)
    
    db.commit()
    db.refresh(user_med)
    
    return user_med


@user_med_router.delete("/{user_med_id}", response_model=MessageResponse)
async def remove_from_medication_box(
    user_med_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 从药箱中移除药品（软删除）
    user_med = db.query(UserMedication).filter(
        UserMedication.id == user_med_id,
        UserMedication.user_id == getattr(current_user, 'id')
    ).first()
    
    if not user_med:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="药品不在您的药箱中"
        )
    
    # 软删除：标记为inactive
    from app.models.models import MedicationStatus
    setattr(user_med, 'status', MedicationStatus.INACTIVE)
    db.commit()
    
    return MessageResponse(message="药品已从药箱中移除")
