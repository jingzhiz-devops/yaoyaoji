"""
用药计划和记录管理路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from datetime import datetime, date

from app.database import get_db
from app.models.models import (
    User, UserMedication, MedicationSchedule, MedicationRecord, Medicine
)
from app.schemas.schemas import (
    MedicationScheduleCreate, MedicationScheduleResponse,
    MedicationRecordCreate, MedicationRecordUpdate, MedicationRecordResponse,
    MessageResponse
)
from app.auth import get_current_user

schedule_router = APIRouter(prefix="/api/schedules", tags=["用药计划"])
record_router = APIRouter(prefix="/api/records", tags=["用药记录"])


# ============= 用药计划管理 =============

@schedule_router.post("/", response_model=MedicationScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    schedule: MedicationScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建用药计划"""
    # 验证用户药品是否存在且属于当前用户
    user_med = db.query(UserMedication).filter(
        UserMedication.id == schedule.user_medication_id,
        UserMedication.user_id == getattr(current_user, 'id'),
        UserMedication.status == "active"
    ).first()
    
    if not user_med:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="该药品不在您的药箱中或已失效"
        )
    
    # 将 time 对象转换为字符串列表存储到 JSON 字段
    schedule_data = schedule.model_dump()
    schedule_data['scheduled_times'] = [t.strftime('%H:%M:%S') for t in schedule.scheduled_times]
    
    db_schedule = MedicationSchedule(**schedule_data)
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    
    return db_schedule


@schedule_router.get("/", response_model=List[MedicationScheduleResponse])
async def get_my_schedules(
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取我的用药计划"""
    query = db.query(MedicationSchedule).join(UserMedication).options(
        joinedload(MedicationSchedule.user_medication).joinedload(UserMedication.medicine)
    ).filter(
        UserMedication.user_id == getattr(current_user, 'id')
    )
    
    if active_only:
        today = date.today()
        query = query.filter(
            MedicationSchedule.start_date <= today,
            (MedicationSchedule.end_date.is_(None)) | (MedicationSchedule.end_date >= today)
        )
    
    schedules = query.all()
    return schedules


@schedule_router.get("/{schedule_id}", response_model=MedicationScheduleResponse)
async def get_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用药计划详情"""
    schedule = db.query(MedicationSchedule).join(UserMedication).options(
        joinedload(MedicationSchedule.user_medication).joinedload(UserMedication.medicine)
    ).filter(
        MedicationSchedule.id == schedule_id,
        UserMedication.user_id == getattr(current_user, 'id')
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用药计划不存在"
        )
    
    return schedule


@schedule_router.delete("/{schedule_id}", response_model=MessageResponse)
async def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除用药计划"""
    schedule = db.query(MedicationSchedule).join(UserMedication).filter(
        MedicationSchedule.id == schedule_id,
        UserMedication.user_id == getattr(current_user, 'id')
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用药计划不存在"
        )
    
    db.delete(schedule)
    db.commit()
    
    return MessageResponse(message="用药计划已删除")


@schedule_router.patch("/{schedule_id}", response_model=MedicationScheduleResponse)
async def update_schedule(
    schedule_id: int,
    schedule: MedicationScheduleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新用药计划"""
    # 验证计划是否存在且属于当前用户
    db_schedule = db.query(MedicationSchedule).join(UserMedication).filter(
        MedicationSchedule.id == schedule_id,
        UserMedication.user_id == getattr(current_user, 'id')
    ).first()
    
    if not db_schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用药计划不存在"
        )
    
    # 验证用户药品是否存在且属于当前用户
    user_med = db.query(UserMedication).filter(
        UserMedication.id == schedule.user_medication_id,
        UserMedication.user_id == getattr(current_user, 'id'),
        UserMedication.status == "active"
    ).first()
    
    if not user_med:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="该药品不在您的药箱中或已失效"
        )
    
    # 更新数据
    schedule_data = schedule.model_dump()
    schedule_data['scheduled_times'] = [t.strftime('%H:%M:%S') for t in schedule.scheduled_times]
    
    for key, value in schedule_data.items():
        setattr(db_schedule, key, value)
    
    db.commit()
    db.refresh(db_schedule)
    
    return db_schedule


# ============= 用药记录管理 =============

@record_router.post("/", response_model=MedicationRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_record(
    record: MedicationRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建用药记录"""
    # 验证计划是否存在且属于当前用户
    schedule = db.query(MedicationSchedule).join(UserMedication).filter(
        MedicationSchedule.id == record.schedule_id,
        UserMedication.user_id == getattr(current_user, 'id')
    ).first()
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用药计划不存在"
        )
    
    db_record = MedicationRecord(**record.model_dump())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    
    return db_record


@record_router.get("/", response_model=List[MedicationRecordResponse])
async def get_my_records(
    start_date: date | None = None,
    end_date: date | None = None,
    status_filter: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取我的用药记录"""
    query = db.query(MedicationRecord).join(MedicationSchedule).join(UserMedication).options(
        joinedload(MedicationRecord.schedule).joinedload(MedicationSchedule.user_medication).joinedload(UserMedication.medicine)
    ).filter(
        UserMedication.user_id == getattr(current_user, 'id')
    )
    
    if start_date:
        query = query.filter(MedicationRecord.scheduled_time >= start_date)
    
    if end_date:
        query = query.filter(MedicationRecord.scheduled_time <= end_date)
    
    if status_filter:
        query = query.filter(MedicationRecord.status == status_filter)
    
    records = query.order_by(MedicationRecord.scheduled_time.desc()).all()
    return records


@record_router.get("/today", response_model=List[MedicationRecordResponse])
async def get_today_records(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取今日用药记录"""
    today = date.today()
    records = db.query(MedicationRecord).join(MedicationSchedule).join(UserMedication).options(
        joinedload(MedicationRecord.schedule).joinedload(MedicationSchedule.user_medication).joinedload(UserMedication.medicine)
    ).filter(
        UserMedication.user_id == getattr(current_user, 'id'),
        MedicationRecord.scheduled_time >= today,
        MedicationRecord.scheduled_time < datetime(today.year, today.month, today.day, 23, 59, 59)
    ).order_by(MedicationRecord.scheduled_time).all()
    
    return records


@record_router.get("/{record_id}", response_model=MedicationRecordResponse)
async def get_record(
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用药记录详情"""
    record = db.query(MedicationRecord).join(MedicationSchedule).join(UserMedication).options(
        joinedload(MedicationRecord.schedule).joinedload(MedicationSchedule.user_medication).joinedload(UserMedication.medicine)
    ).filter(
        MedicationRecord.id == record_id,
        UserMedication.user_id == getattr(current_user, 'id')
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用药记录不存在"
        )
    
    return record


@record_router.patch("/{record_id}", response_model=MedicationRecordResponse)
async def update_record(
    record_id: int,
    update_data: MedicationRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新用药记录（标记已服用/跳过等）"""
    record = db.query(MedicationRecord).join(MedicationSchedule).join(UserMedication).filter(
        MedicationRecord.id == record_id,
        UserMedication.user_id == getattr(current_user, 'id')
    ).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用药记录不存在"
        )
    
    # 更新字段
    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(record, key, value)
    
    # 如果标记为已服用且没有指定实际时间，自动设置为当前时间
    if update_data.status == "taken" and update_data.actual_time is None:
        setattr(record, 'actual_time', datetime.now())
    
    db.commit()
    db.refresh(record)
    
    return record
