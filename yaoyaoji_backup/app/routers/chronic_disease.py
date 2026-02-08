"""  
慢性病管理模块 API 路由
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import date, datetime, timedelta
from typing import List, Optional

from app.database import get_db
from app.auth import get_current_user
from app.models.models import (
    User, ChronicDisease, DiseaseIndicator, IndicatorRecord,
    FollowupPlan, FollowupRecord, ControlStatus,
    IndicatorAlert, AlertLevel, MedicationAdherence,
    UserMedication, MedicationSchedule, MedicationRecord, RecordStatus
)
from app.schemas.schemas import (
    ChronicDiseaseCreate, ChronicDiseaseUpdate, ChronicDiseaseResponse,
    DiseaseIndicatorBase, DiseaseIndicatorResponse,
    IndicatorRecordCreate, IndicatorRecordResponse,
    FollowupPlanCreate, FollowupPlanResponse,
    FollowupRecordCreate, FollowupRecordResponse,
    IndicatorAlertResponse, AlertHandleRequest,
    MedicationAdherenceResponse, AdherenceStatsResponse
)

router = APIRouter(prefix="/api/chronic-diseases", tags=["慢性病管理"])


# ============= 慢性病管理 API =============

@router.post("", response_model=ChronicDiseaseResponse)
async def create_chronic_disease(
    data: ChronicDiseaseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建慢性病记录"""
    disease = ChronicDisease(
        user_id=current_user.id,
        disease_name=data.disease_name,
        icd10_code=data.icd10_code,
        diagnosis_date=data.diagnosis_date,
        diagnosis_hospital=data.diagnosis_hospital,
        diagnosis_doctor=data.diagnosis_doctor,
        current_treatment=data.current_treatment,
        control_status=data.control_status
    )
    db.add(disease)
    db.commit()
    db.refresh(disease)
    return disease


@router.get("", response_model=List[ChronicDiseaseResponse])
async def list_chronic_diseases(
    search: Optional[str] = Query(None, description="按疾病名称搜索"),
    control_status: Optional[str] = Query(None, description="按控制状态筛选"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的慢性病列表"""
    query = db.query(ChronicDisease).filter(ChronicDisease.user_id == current_user.id)
    
    if search:
        query = query.filter(ChronicDisease.disease_name.ilike(f"%{search}%"))
    
    if control_status:
        query = query.filter(ChronicDisease.control_status == control_status)
    
    return query.order_by(ChronicDisease.updated_at.desc()).all()


@router.get("/{disease_id}", response_model=ChronicDiseaseResponse)
async def get_chronic_disease(
    disease_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取慢性病详情"""
    disease = db.query(ChronicDisease).filter(
        ChronicDisease.id == disease_id,
        ChronicDisease.user_id == current_user.id
    ).first()
    
    if not disease:
        raise HTTPException(status_code=404, detail="慢性病记录不存在")
    
    return disease


@router.put("/{disease_id}", response_model=ChronicDiseaseResponse)
async def update_chronic_disease(
    disease_id: int,
    data: ChronicDiseaseUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新慢性病信息"""
    disease = db.query(ChronicDisease).filter(
        ChronicDisease.id == disease_id,
        ChronicDisease.user_id == current_user.id
    ).first()
    
    if not disease:
        raise HTTPException(status_code=404, detail="慢性病记录不存在")
    
    # 仅更新提供的字段
    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(disease, field, value)
    
    disease.updated_at = datetime.now()
    db.commit()
    db.refresh(disease)
    return disease


@router.delete("/{disease_id}")
async def delete_chronic_disease(
    disease_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除慢性病记录"""
    disease = db.query(ChronicDisease).filter(
        ChronicDisease.id == disease_id,
        ChronicDisease.user_id == current_user.id
    ).first()
    
    if not disease:
        raise HTTPException(status_code=404, detail="慢性病记录不存在")
    
    db.delete(disease)
    db.commit()
    return {"message": "删除成功"}


# ============= 关键指标管理 API =============

@router.get("/{disease_id}/indicators", response_model=List[DiseaseIndicatorResponse])
async def get_indicators(
    disease_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取慢性病的关键指标列表"""
    # 验证用户权限
    disease = db.query(ChronicDisease).filter(
        ChronicDisease.id == disease_id,
        ChronicDisease.user_id == current_user.id
    ).first()
    
    if not disease:
        raise HTTPException(status_code=404, detail="慢性病记录不存在")
    
    indicators = db.query(DiseaseIndicator).filter(
        DiseaseIndicator.disease_id == disease_id
    ).all()
    
    return indicators


@router.post("/{disease_id}/indicators", response_model=DiseaseIndicatorResponse)
async def add_indicator(
    disease_id: int,
    data: DiseaseIndicatorBase,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """为慢性病添加关键指标"""
    # 验证用户权限
    disease = db.query(ChronicDisease).filter(
        ChronicDisease.id == disease_id,
        ChronicDisease.user_id == current_user.id
    ).first()
    
    if not disease:
        raise HTTPException(status_code=404, detail="慢性病记录不存在")
    
    indicator = DiseaseIndicator(
        disease_id=disease_id,
        indicator_name=data.indicator_name,
        normal_range_min=data.normal_range_min,
        normal_range_max=data.normal_range_max,
        unit=data.unit,
        check_frequency=data.check_frequency
    )
    db.add(indicator)
    db.commit()
    db.refresh(indicator)
    return indicator


# ============= 指标记录管理 API =============

@router.post("/{disease_id}/indicator-records", response_model=IndicatorRecordResponse)
async def record_indicator(
    disease_id: int,
    data: IndicatorRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """记录指标数据（自动检测异常并生成预警）"""
    # 验证用户权限
    disease = db.query(ChronicDisease).filter(
        ChronicDisease.id == disease_id,
        ChronicDisease.user_id == current_user.id
    ).first()
    
    if not disease:
        raise HTTPException(status_code=404, detail="慢性病记录不存在")
    
    # 获取指标信息
    indicator = db.query(DiseaseIndicator).filter(
        DiseaseIndicator.id == data.indicator_id,
        DiseaseIndicator.disease_id == disease_id
    ).first()
    
    if not indicator:
        raise HTTPException(status_code=404, detail="指标不存在")
    
    # 创建记录
    record = IndicatorRecord(
        disease_id=disease_id,
        indicator_id=data.indicator_id,
        value=data.value,
        measurement_date=data.measurement_date,
        recorded_by=data.recorded_by or "self",
        notes=data.notes
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    
    # 自动检测异常并生成预警
    alert = check_and_create_alert(db, current_user.id, disease_id, indicator, record)
    if alert:
        db.commit()
    
    return record


@router.get("/{disease_id}/indicator-records", response_model=List[IndicatorRecordResponse])
async def get_indicator_records(
    disease_id: int,
    indicator_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取指标记录历史"""
    # 验证用户权限
    disease = db.query(ChronicDisease).filter(
        ChronicDisease.id == disease_id,
        ChronicDisease.user_id == current_user.id
    ).first()
    
    if not disease:
        raise HTTPException(status_code=404, detail="慢性病记录不存在")
    
    query = db.query(IndicatorRecord).filter(
        IndicatorRecord.disease_id == disease_id
    )
    
    if indicator_id:
        query = query.filter(IndicatorRecord.indicator_id == indicator_id)
    
    if start_date:
        query = query.filter(IndicatorRecord.measurement_date >= start_date)
    
    if end_date:
        query = query.filter(IndicatorRecord.measurement_date <= end_date)
    
    return query.order_by(IndicatorRecord.measurement_date.desc()).all()


# ============= 随访计划管理 API =============

@router.post("/{disease_id}/followup-plans", response_model=FollowupPlanResponse)
async def create_followup_plan(
    disease_id: int,
    data: FollowupPlanCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建随访计划"""
    # 验证用户权限
    disease = db.query(ChronicDisease).filter(
        ChronicDisease.id == disease_id,
        ChronicDisease.user_id == current_user.id
    ).first()
    
    if not disease:
        raise HTTPException(status_code=404, detail="慢性病记录不存在")
    
    plan = FollowupPlan(
        disease_id=disease_id,
        frequency=data.frequency,
        next_followup_date=data.next_followup_date,
        responsible_doctor=data.responsible_doctor,
        followup_checklist=data.followup_checklist,
        target_values=data.target_values,
        reminder_days=data.reminder_days
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


@router.get("/{disease_id}/followup-plans", response_model=List[FollowupPlanResponse])
async def get_followup_plans(
    disease_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取随访计划"""
    # 验证用户权限
    disease = db.query(ChronicDisease).filter(
        ChronicDisease.id == disease_id,
        ChronicDisease.user_id == current_user.id
    ).first()
    
    if not disease:
        raise HTTPException(status_code=404, detail="慢性病记录不存在")
    
    return db.query(FollowupPlan).filter(
        FollowupPlan.disease_id == disease_id
    ).order_by(FollowupPlan.next_followup_date).all()


@router.put("/{disease_id}/followup-plans/{plan_id}", response_model=FollowupPlanResponse)
async def update_followup_plan(
    disease_id: int,
    plan_id: int,
    data: FollowupPlanCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新随访计划"""
    # 验证用户权限
    disease = db.query(ChronicDisease).filter(
        ChronicDisease.id == disease_id,
        ChronicDisease.user_id == current_user.id
    ).first()
    
    if not disease:
        raise HTTPException(status_code=404, detail="慢性病记录不存在")
    
    plan = db.query(FollowupPlan).filter(
        FollowupPlan.id == plan_id,
        FollowupPlan.disease_id == disease_id
    ).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="随访计划不存在")
    
    plan.frequency = data.frequency
    plan.next_followup_date = data.next_followup_date
    plan.responsible_doctor = data.responsible_doctor
    plan.followup_checklist = data.followup_checklist
    plan.target_values = data.target_values
    plan.reminder_days = data.reminder_days
    plan.updated_at = datetime.now()
    
    db.commit()
    db.refresh(plan)
    return plan


@router.delete("/{disease_id}/followup-plans/{plan_id}")
async def delete_followup_plan(
    disease_id: int,
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除随访计划"""
    # 验证用户权限
    disease = db.query(ChronicDisease).filter(
        ChronicDisease.id == disease_id,
        ChronicDisease.user_id == current_user.id
    ).first()
    
    if not disease:
        raise HTTPException(status_code=404, detail="慢性病记录不存在")
    
    plan = db.query(FollowupPlan).filter(
        FollowupPlan.id == plan_id,
        FollowupPlan.disease_id == disease_id
    ).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="随访计划不存在")
    
    db.delete(plan)
    db.commit()
    return {"message": "删除成功"}


# ============= 随访记录管理 API =============

@router.post("/{disease_id}/followup-plans/{plan_id}/records", response_model=FollowupRecordResponse)
async def create_followup_record(
    disease_id: int,
    plan_id: int,
    data: FollowupRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """记录随访结果"""
    # 验证用户权限
    disease = db.query(ChronicDisease).filter(
        ChronicDisease.id == disease_id,
        ChronicDisease.user_id == current_user.id
    ).first()
    
    if not disease:
        raise HTTPException(status_code=404, detail="慢性病记录不存在")
    
    plan = db.query(FollowupPlan).filter(
        FollowupPlan.id == plan_id,
        FollowupPlan.disease_id == disease_id
    ).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="随访计划不存在")
    
    record = FollowupRecord(
        followup_plan_id=plan_id,
        followup_date=data.followup_date,
        symptoms_assessment=data.symptoms_assessment,
        indicator_check=data.indicator_check,
        medication_evaluation=data.medication_evaluation,
        lifestyle_guidance=data.lifestyle_guidance,
        doctor_notes=data.doctor_notes,
        next_plan=data.next_plan
    )
    
    # 更新随访计划的最后随访日期
    plan.last_followup_date = data.followup_date.date()
    
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/{disease_id}/followup-plans/{plan_id}/records", response_model=List[FollowupRecordResponse])
async def get_followup_records(
    disease_id: int,
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取随访记录历史"""
    # 验证用户权限
    disease = db.query(ChronicDisease).filter(
        ChronicDisease.id == disease_id,
        ChronicDisease.user_id == current_user.id
    ).first()
    
    if not disease:
        raise HTTPException(status_code=404, detail="慢性病记录不存在")
    
    plan = db.query(FollowupPlan).filter(
        FollowupPlan.id == plan_id,
        FollowupPlan.disease_id == disease_id
    ).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="随访计划不存在")
    
    return db.query(FollowupRecord).filter(
        FollowupRecord.followup_plan_id == plan_id
    ).order_by(FollowupRecord.created_at.desc()).all()


# ============= 异常值预警 API =============

def check_and_create_alert(
    db: Session,
    user_id: int,
    disease_id: int,
    indicator: DiseaseIndicator,
    record: IndicatorRecord
) -> Optional[IndicatorAlert]:
    """检查指标是否异常并生成预警"""
    value = record.value
    min_val = indicator.normal_range_min
    max_val = indicator.normal_range_max
    
    # 如果没有设置正常范围，不生成预警
    if min_val is None and max_val is None:
        return None
    
    alert_level = None
    alert_message = ""
    suggestion = ""
    
    # 判断异常程度
    if min_val is not None and value < min_val:
        deviation = ((min_val - value) / min_val) * 100
        if deviation > 20:
            alert_level = AlertLevel.RED
            alert_message = f"{indicator.indicator_name}严重偏低：{value}{indicator.unit}，低于正常范围{deviation:.1f}%"
            suggestion = "建议立即咨询医生，可能需要调整用药或治疗方案。"
        elif deviation > 10:
            alert_level = AlertLevel.ORANGE
            alert_message = f"{indicator.indicator_name}偏低：{value}{indicator.unit}，低于正常范围{deviation:.1f}%"
            suggestion = "建议密切监测，如持续偏低请及时就医。"
        else:
            alert_level = AlertLevel.YELLOW
            alert_message = f"{indicator.indicator_name}轻微偏低：{value}{indicator.unit}"
            suggestion = "建议注意观察，保持健康生活方式。"
    
    elif max_val is not None and value > max_val:
        deviation = ((value - max_val) / max_val) * 100
        if deviation > 20:
            alert_level = AlertLevel.RED
            alert_message = f"{indicator.indicator_name}严重超标：{value}{indicator.unit}，超出正常范围{deviation:.1f}%"
            suggestion = "建议立即咨询医生，可能需要调整用药或治疗方案。"
        elif deviation > 10:
            alert_level = AlertLevel.ORANGE
            alert_message = f"{indicator.indicator_name}超标：{value}{indicator.unit}，超出正常范围{deviation:.1f}%"
            suggestion = "建议密切监测，如持续超标请及时就医。"
        else:
            alert_level = AlertLevel.YELLOW
            alert_message = f"{indicator.indicator_name}轻微超标：{value}{indicator.unit}"
            suggestion = "建议注意观察，保持健康生活方式。"
    
    # 如果有异常，创建预警
    if alert_level:
        normal_range_str = ""
        if min_val and max_val:
            normal_range_str = f"{min_val}-{max_val}{indicator.unit}"
        elif min_val:
            normal_range_str = f">{min_val}{indicator.unit}"
        elif max_val:
            normal_range_str = f"<{max_val}{indicator.unit}"
        
        alert = IndicatorAlert(
            user_id=user_id,
            disease_id=disease_id,
            indicator_id=indicator.id,
            record_id=record.id,
            alert_level=alert_level,
            alert_message=alert_message,
            indicator_value=value,
            normal_range=normal_range_str,
            suggestion=suggestion
        )
        db.add(alert)
        return alert
    
    return None


@router.get("/alerts", response_model=List[IndicatorAlertResponse])
async def get_alerts(
    unread_only: bool = Query(False, description="仅显示未读"),
    unhandled_only: bool = Query(False, description="仅显示未处理"),
    alert_level: Optional[str] = Query(None, description="按预警级别筛选"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的异常值预警列表"""
    query = db.query(IndicatorAlert).filter(IndicatorAlert.user_id == current_user.id)
    
    if unread_only:
        query = query.filter(IndicatorAlert.is_read == False)
    
    if unhandled_only:
        query = query.filter(IndicatorAlert.is_handled == False)
    
    if alert_level:
        query = query.filter(IndicatorAlert.alert_level == alert_level)
    
    return query.order_by(IndicatorAlert.created_at.desc()).all()


@router.put("/alerts/{alert_id}/read")
async def mark_alert_read(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """标记预警为已读"""
    alert = db.query(IndicatorAlert).filter(
        IndicatorAlert.id == alert_id,
        IndicatorAlert.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="预警不存在")
    
    alert.is_read = True
    db.commit()
    return {"message": "已标记为已读"}


@router.put("/alerts/{alert_id}/handle", response_model=IndicatorAlertResponse)
async def handle_alert(
    alert_id: int,
    data: AlertHandleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """处理预警"""
    alert = db.query(IndicatorAlert).filter(
        IndicatorAlert.id == alert_id,
        IndicatorAlert.user_id == current_user.id
    ).first()
    
    if not alert:
        raise HTTPException(status_code=404, detail="预警不存在")
    
    alert.is_handled = True
    alert.handled_at = datetime.now()
    alert.handler_notes = data.handler_notes
    
    db.commit()
    db.refresh(alert)
    return alert


@router.get("/alerts/stats")
async def get_alert_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取预警统计信息"""
    total = db.query(IndicatorAlert).filter(IndicatorAlert.user_id == current_user.id).count()
    unread = db.query(IndicatorAlert).filter(
        IndicatorAlert.user_id == current_user.id,
        IndicatorAlert.is_read == False
    ).count()
    unhandled = db.query(IndicatorAlert).filter(
        IndicatorAlert.user_id == current_user.id,
        IndicatorAlert.is_handled == False
    ).count()
    
    red_count = db.query(IndicatorAlert).filter(
        IndicatorAlert.user_id == current_user.id,
        IndicatorAlert.alert_level == AlertLevel.RED,
        IndicatorAlert.is_handled == False
    ).count()
    
    return {
        "total": total,
        "unread": unread,
        "unhandled": unhandled,
        "critical": red_count
    }


# ============= 用药依从性跟踪 API =============

@router.post("/{disease_id}/adherence/calculate")
async def calculate_adherence(
    disease_id: int,
    period_days: int = Query(7, description="统计周期天数"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """计算指定慢性病的用药依从性"""
    # 验证病情
    disease = db.query(ChronicDisease).filter(
        ChronicDisease.id == disease_id,
        ChronicDisease.user_id == current_user.id
    ).first()
    
    if not disease:
        raise HTTPException(status_code=404, detail="慢性病记录不存在")
    
    # 计算时间范围
    period_end = date.today()
    period_start = period_end - timedelta(days=period_days)
    
    # 获取用户所有活跃的药品
    medications = db.query(UserMedication).filter(
        UserMedication.user_id == current_user.id,
        UserMedication.status == "active"
    ).all()
    
    adherence_records = []
    
    for medication in medications:
        # 获取该药品的计划
        schedules = db.query(MedicationSchedule).filter(
            MedicationSchedule.user_medication_id == medication.id,
            MedicationSchedule.start_date <= period_end
        ).all()
        
        if not schedules:
            continue
        
        total_doses = 0
        taken_doses = 0
        skipped_doses = 0
        delayed_doses = 0
        
        for schedule in schedules:
            # 统计该周期内的用药记录
            records = db.query(MedicationRecord).filter(
                MedicationRecord.schedule_id == schedule.id,
                func.date(MedicationRecord.scheduled_time) >= period_start,
                func.date(MedicationRecord.scheduled_time) <= period_end
            ).all()
            
            total_doses += len(records)
            for record in records:
                if record.status == RecordStatus.TAKEN:
                    taken_doses += 1
                elif record.status == RecordStatus.SKIPPED:
                    skipped_doses += 1
                elif record.status == RecordStatus.DELAYED:
                    delayed_doses += 1
        
        if total_doses == 0:
            continue
        
        adherence_rate = (taken_doses / total_doses) * 100 if total_doses > 0 else 0
        
        # 创建或更新依从性记录
        existing = db.query(MedicationAdherence).filter(
            MedicationAdherence.user_id == current_user.id,
            MedicationAdherence.disease_id == disease_id,
            MedicationAdherence.user_medication_id == medication.id,
            MedicationAdherence.period_start == period_start,
            MedicationAdherence.period_end == period_end
        ).first()
        
        if existing:
            existing.total_doses = total_doses
            existing.taken_doses = taken_doses
            existing.skipped_doses = skipped_doses
            existing.delayed_doses = delayed_doses
            existing.adherence_rate = adherence_rate
            existing.control_status_after = disease.control_status
            existing.updated_at = datetime.now()
            adherence_records.append(existing)
        else:
            adherence = MedicationAdherence(
                user_id=current_user.id,
                disease_id=disease_id,
                user_medication_id=medication.id,
                period_start=period_start,
                period_end=period_end,
                total_doses=total_doses,
                taken_doses=taken_doses,
                skipped_doses=skipped_doses,
                delayed_doses=delayed_doses,
                adherence_rate=adherence_rate,
                control_status_before=disease.control_status,
                control_status_after=disease.control_status
            )
            db.add(adherence)
            adherence_records.append(adherence)
    
    db.commit()
    
    return {
        "message": "依从性计算完成",
        "period_start": period_start,
        "period_end": period_end,
        "medications_count": len(adherence_records)
    }


@router.get("/{disease_id}/adherence", response_model=List[MedicationAdherenceResponse])
async def get_adherence(
    disease_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取指定慢性病的用药依从性记录"""
    # 验证权限
    disease = db.query(ChronicDisease).filter(
        ChronicDisease.id == disease_id,
        ChronicDisease.user_id == current_user.id
    ).first()
    
    if not disease:
        raise HTTPException(status_code=404, detail="慢性病记录不存在")
    
    return db.query(MedicationAdherence).filter(
        MedicationAdherence.disease_id == disease_id
    ).order_by(MedicationAdherence.period_end.desc()).all()


@router.get("/{disease_id}/adherence/stats", response_model=AdherenceStatsResponse)
async def get_adherence_stats(
    disease_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用药依从性统计"""
    # 验证权限
    disease = db.query(ChronicDisease).filter(
        ChronicDisease.id == disease_id,
        ChronicDisease.user_id == current_user.id
    ).first()
    
    if not disease:
        raise HTTPException(status_code=404, detail="慢性病记录不存在")
    
    # 获取最近的依从性记录
    recent_adherence = db.query(MedicationAdherence).filter(
        MedicationAdherence.disease_id == disease_id
    ).order_by(MedicationAdherence.period_end.desc()).limit(10).all()
    
    # 计算平均依从率
    if recent_adherence:
        avg_rate = sum(a.adherence_rate for a in recent_adherence) / len(recent_adherence)
    else:
        avg_rate = 0.0
    
    # 统计总药品数
    total_meds = len(set(a.user_medication_id for a in recent_adherence))
    
    return AdherenceStatsResponse(
        disease_id=disease.id,
        disease_name=disease.disease_name,
        total_medications=total_meds,
        average_adherence_rate=avg_rate,
        recent_adherence=recent_adherence,
        control_status=disease.control_status
    )
