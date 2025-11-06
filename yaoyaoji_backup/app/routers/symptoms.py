"""
症状记录管理路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date

from app.database import get_db
from app.models.models import User, SymptomRecord
from app.schemas.schemas import (
    SymptomRecordCreate, SymptomRecordUpdate, SymptomRecordResponse, MessageResponse
)
from app.auth import get_current_user

router = APIRouter(prefix="/api/symptoms", tags=["症状记录"])


@router.post("/", response_model=SymptomRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_symptom_record(
    symptom: SymptomRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建症状记录"""
    db_symptom = SymptomRecord(
        user_id=getattr(current_user, 'id'),
        **symptom.model_dump()
    )
    db.add(db_symptom)
    db.commit()
    db.refresh(db_symptom)
    
    return db_symptom


@router.get("/", response_model=List[SymptomRecordResponse])
async def get_my_symptoms(
    start_date: date | None = None,
    end_date: date | None = None,
    min_intensity: int | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取我的症状记录"""
    query = db.query(SymptomRecord).filter(
        SymptomRecord.user_id == getattr(current_user, 'id')
    )
    
    if start_date:
        query = query.filter(SymptomRecord.recorded_time >= start_date)
    
    if end_date:
        query = query.filter(SymptomRecord.recorded_time <= end_date)
    
    if min_intensity:
        query = query.filter(SymptomRecord.intensity >= min_intensity)
    
    symptoms = query.order_by(SymptomRecord.recorded_time.desc()).all()
    return symptoms


@router.get("/today", response_model=List[SymptomRecordResponse])
async def get_today_symptoms(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取今日症状记录"""
    today = date.today()
    symptoms = db.query(SymptomRecord).filter(
        SymptomRecord.user_id == getattr(current_user, 'id'),
        SymptomRecord.recorded_time >= today
    ).order_by(SymptomRecord.recorded_time.desc()).all()
    
    return symptoms


@router.get("/timeline", response_model=List[SymptomRecordResponse])
async def get_symptom_timeline(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取症状时间轴（默认最近7天）"""
    from datetime import timedelta
    start_date = datetime.now() - timedelta(days=days)
    
    symptoms = db.query(SymptomRecord).filter(
        SymptomRecord.user_id == getattr(current_user, 'id'),
        SymptomRecord.recorded_time >= start_date
    ).order_by(SymptomRecord.recorded_time.asc()).all()
    
    return symptoms


@router.get("/{symptom_id}", response_model=SymptomRecordResponse)
async def get_symptom(
    symptom_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取症状记录详情"""
    symptom = db.query(SymptomRecord).filter(
        SymptomRecord.id == symptom_id,
        SymptomRecord.user_id == getattr(current_user, 'id')
    ).first()
    
    if not symptom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="症状记录不存在"
        )
    
    return symptom


@router.patch("/{symptom_id}", response_model=SymptomRecordResponse)
async def update_symptom(
    symptom_id: int,
    update_data: SymptomRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新症状记录"""
    symptom = db.query(SymptomRecord).filter(
        SymptomRecord.id == symptom_id,
        SymptomRecord.user_id == getattr(current_user, 'id')
    ).first()
    
    if not symptom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="症状记录不存在"
        )
    
    # 更新字段
    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(symptom, key, value)
    
    db.commit()
    db.refresh(symptom)
    
    return symptom


@router.delete("/{symptom_id}", response_model=MessageResponse)
async def delete_symptom(
    symptom_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除症状记录"""
    symptom = db.query(SymptomRecord).filter(
        SymptomRecord.id == symptom_id,
        SymptomRecord.user_id == getattr(current_user, 'id')
    ).first()
    
    if not symptom:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="症状记录不存在"
        )
    
    db.delete(symptom)
    db.commit()
    
    return MessageResponse(message="症状记录已删除")
