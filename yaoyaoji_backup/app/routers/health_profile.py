# 健康档案管理路由
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.models import User, HealthProfile, AllergyRecord, FamilyHistory, SurgeryRecord, CheckupReport, VaccinationRecord
from app.schemas.schemas import (
    HealthProfileCreate, HealthProfileUpdate, HealthProfileResponse,
    AllergyRecordCreate, AllergyRecordUpdate, AllergyRecordResponse,
    FamilyHistoryCreate, FamilyHistoryUpdate, FamilyHistoryResponse,
    SurgeryRecordCreate, SurgeryRecordUpdate, SurgeryRecordResponse,
    CheckupReportCreate, CheckupReportUpdate, CheckupReportResponse,
    VaccinationRecordCreate, VaccinationRecordUpdate, VaccinationRecordResponse,
    MessageResponse
)
from app.auth import get_current_user

router = APIRouter(prefix="/api/health-profile", tags=["健康档案"])


# ============= 健康档案主表 =============

@router.get("/", response_model=HealthProfileResponse)
async def get_my_health_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取我的健康档案"""
    profile = db.query(HealthProfile).filter(
        HealthProfile.user_id == current_user.id
    ).first()
    
    if not profile:
        # 如果不存在，自动创建一个空档案
        profile = HealthProfile(user_id=current_user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
    
    return profile


@router.post("/", response_model=HealthProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_or_update_health_profile(
    profile_data: HealthProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建或更新健康档案"""
    try:
        existing = db.query(HealthProfile).filter(
            HealthProfile.user_id == current_user.id
        ).first()
        
        # 不再同步姓名到User表，健康档案姓名与User表姓名分开管理
        
        if existing:
            # 更新
            for key, value in profile_data.model_dump(exclude_unset=True).items():
                setattr(existing, key, value)
            db.commit()
            db.refresh(existing)
            return existing
        else:
            # 创建
            profile = HealthProfile(
                user_id=current_user.id,
                **profile_data.model_dump()
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)
            return profile
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"保存失败: {str(e)}"
        )


# ============= 过敏史记录 =============

@router.get("/allergies", response_model=List[AllergyRecordResponse])
async def get_allergy_records(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取过敏史记录列表"""
    profile = await get_my_health_profile(db, current_user)
    return db.query(AllergyRecord).filter(
        AllergyRecord.profile_id == profile.id
    ).order_by(AllergyRecord.created_at.desc()).all()


@router.post("/allergies", response_model=AllergyRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_allergy_record(
    allergy: AllergyRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """添加过敏史记录"""
    profile = await get_my_health_profile(db, current_user)
    
    record = AllergyRecord(
        profile_id=profile.id,
        **allergy.model_dump()
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.patch("/allergies/{record_id}", response_model=AllergyRecordResponse)
async def update_allergy_record(
    record_id: int,
    update_data: AllergyRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新过敏史记录"""
    profile = await get_my_health_profile(db, current_user)
    
    record = db.query(AllergyRecord).filter(
        AllergyRecord.id == record_id,
        AllergyRecord.profile_id == profile.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记录不存在"
        )
    
    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    
    db.commit()
    db.refresh(record)
    return record


@router.delete("/allergies/{record_id}", response_model=MessageResponse)
async def delete_allergy_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除过敏史记录"""
    profile = await get_my_health_profile(db, current_user)
    
    record = db.query(AllergyRecord).filter(
        AllergyRecord.id == record_id,
        AllergyRecord.profile_id == profile.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记录不存在"
        )
    
    db.delete(record)
    db.commit()
    return MessageResponse(message="记录已删除")


# ============= 家族病史 =============

@router.get("/family-history", response_model=List[FamilyHistoryResponse])
async def get_family_histories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取家族病史列表"""
    profile = await get_my_health_profile(db, current_user)
    return db.query(FamilyHistory).filter(
        FamilyHistory.profile_id == profile.id
    ).order_by(FamilyHistory.created_at.desc()).all()


@router.post("/family-history", response_model=FamilyHistoryResponse, status_code=status.HTTP_201_CREATED)
async def create_family_history(
    history: FamilyHistoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """添加家族病史"""
    profile = await get_my_health_profile(db, current_user)
    
    record = FamilyHistory(
        profile_id=profile.id,
        **history.model_dump()
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.patch("/family-history/{record_id}", response_model=FamilyHistoryResponse)
async def update_family_history(
    record_id: int,
    update_data: FamilyHistoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新家族病史"""
    profile = await get_my_health_profile(db, current_user)
    
    record = db.query(FamilyHistory).filter(
        FamilyHistory.id == record_id,
        FamilyHistory.profile_id == profile.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记录不存在"
        )
    
    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    
    db.commit()
    db.refresh(record)
    return record


@router.delete("/family-history/{record_id}", response_model=MessageResponse)
async def delete_family_history(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除家族病史"""
    profile = await get_my_health_profile(db, current_user)
    
    record = db.query(FamilyHistory).filter(
        FamilyHistory.id == record_id,
        FamilyHistory.profile_id == profile.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记录不存在"
        )
    
    db.delete(record)
    db.commit()
    return MessageResponse(message="记录已删除")


# ============= 手术记录 =============

@router.get("/surgeries", response_model=List[SurgeryRecordResponse])
async def get_surgery_records(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取手术记录列表"""
    profile = await get_my_health_profile(db, current_user)
    return db.query(SurgeryRecord).filter(
        SurgeryRecord.profile_id == profile.id
    ).order_by(SurgeryRecord.surgery_date.desc()).all()


@router.post("/surgeries", response_model=SurgeryRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_surgery_record(
    surgery: SurgeryRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """添加手术记录"""
    profile = await get_my_health_profile(db, current_user)
    
    record = SurgeryRecord(
        profile_id=profile.id,
        **surgery.model_dump()
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.patch("/surgeries/{record_id}", response_model=SurgeryRecordResponse)
async def update_surgery_record(
    record_id: int,
    update_data: SurgeryRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新手术记录"""
    profile = await get_my_health_profile(db, current_user)
    
    record = db.query(SurgeryRecord).filter(
        SurgeryRecord.id == record_id,
        SurgeryRecord.profile_id == profile.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记录不存在"
        )
    
    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    
    db.commit()
    db.refresh(record)
    return record


@router.delete("/surgeries/{record_id}", response_model=MessageResponse)
async def delete_surgery_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除手术记录"""
    profile = await get_my_health_profile(db, current_user)
    
    record = db.query(SurgeryRecord).filter(
        SurgeryRecord.id == record_id,
        SurgeryRecord.profile_id == profile.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记录不存在"
        )
    
    db.delete(record)
    db.commit()
    return MessageResponse(message="记录已删除")


# ============= 体检报告 =============

@router.get("/checkups", response_model=List[CheckupReportResponse])
async def get_checkup_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取体检报告列表"""
    profile = await get_my_health_profile(db, current_user)
    return db.query(CheckupReport).filter(
        CheckupReport.profile_id == profile.id
    ).order_by(CheckupReport.checkup_date.desc()).all()


@router.post("/checkups", response_model=CheckupReportResponse, status_code=status.HTTP_201_CREATED)
async def create_checkup_report(
    checkup: CheckupReportCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """添加体检报告"""
    profile = await get_my_health_profile(db, current_user)
    
    record = CheckupReport(
        profile_id=profile.id,
        **checkup.model_dump()
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.patch("/checkups/{record_id}", response_model=CheckupReportResponse)
async def update_checkup_report(
    record_id: int,
    update_data: CheckupReportUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新体检报告"""
    profile = await get_my_health_profile(db, current_user)
    
    record = db.query(CheckupReport).filter(
        CheckupReport.id == record_id,
        CheckupReport.profile_id == profile.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记录不存在"
        )
    
    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    
    db.commit()
    db.refresh(record)
    return record


@router.delete("/checkups/{record_id}", response_model=MessageResponse)
async def delete_checkup_report(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除体检报告"""
    profile = await get_my_health_profile(db, current_user)
    
    record = db.query(CheckupReport).filter(
        CheckupReport.id == record_id,
        CheckupReport.profile_id == profile.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记录不存在"
        )
    
    db.delete(record)
    db.commit()
    return MessageResponse(message="记录已删除")


# ============= 疫苗接种记录 =============

@router.get("/vaccinations", response_model=List[VaccinationRecordResponse])
async def get_vaccination_records(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取疫苗接种记录列表"""
    profile = await get_my_health_profile(db, current_user)
    return db.query(VaccinationRecord).filter(
        VaccinationRecord.profile_id == profile.id
    ).order_by(VaccinationRecord.vaccination_date.desc()).all()


@router.post("/vaccinations", response_model=VaccinationRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_vaccination_record(
    vaccination: VaccinationRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """添加疫苗接种记录"""
    profile = await get_my_health_profile(db, current_user)
    
    record = VaccinationRecord(
        profile_id=profile.id,
        **vaccination.model_dump()
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.patch("/vaccinations/{record_id}", response_model=VaccinationRecordResponse)
async def update_vaccination_record(
    record_id: int,
    update_data: VaccinationRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新疫苗接种记录"""
    profile = await get_my_health_profile(db, current_user)
    
    record = db.query(VaccinationRecord).filter(
        VaccinationRecord.id == record_id,
        VaccinationRecord.profile_id == profile.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记录不存在"
        )
    
    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    
    db.commit()
    db.refresh(record)
    return record


@router.delete("/vaccinations/{record_id}", response_model=MessageResponse)
async def delete_vaccination_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除疫苗接种记录"""
    profile = await get_my_health_profile(db, current_user)
    
    record = db.query(VaccinationRecord).filter(
        VaccinationRecord.id == record_id,
        VaccinationRecord.profile_id == profile.id
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记录不存在"
        )
    
    db.delete(record)
    db.commit()
    return MessageResponse(message="记录已删除")
