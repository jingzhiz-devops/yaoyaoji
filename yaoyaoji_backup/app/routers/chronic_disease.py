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
    IndicatorAlert, AlertLevel
)
from app.schemas.schemas import (
    ChronicDiseaseCreate, ChronicDiseaseUpdate, ChronicDiseaseResponse,
    DiseaseIndicatorBase, DiseaseIndicatorResponse,
    IndicatorRecordCreate, IndicatorRecordResponse,
    FollowupPlanCreate, FollowupPlanResponse,
    FollowupRecordCreate, FollowupRecordResponse,
    IndicatorAlertResponse, AlertHandleRequest
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
    
    return query.order_by(ChronicDisease.is_pinned.desc(), ChronicDisease.updated_at.desc()).all()


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
    
    try:
        # 删除关联的预警记录（引用 indicator_records 和 disease_indicators）
        db.query(IndicatorAlert).filter(IndicatorAlert.disease_id == disease_id).delete()
        # 删除关联的用药依从性记录
        from app.models.models import MedicationAdherence
        db.query(MedicationAdherence).filter(MedicationAdherence.disease_id == disease_id).delete()
        # 删除关联的并发症记录
        from app.models.models import ComplicationRecord, MedicationReminder
        db.query(ComplicationRecord).filter(ComplicationRecord.disease_id == disease_id).delete()
        # 删除关联的用药提醒
        db.query(MedicationReminder).filter(MedicationReminder.disease_id == disease_id).delete()
        # 删除慢性病本身（indicators, indicator_records, followup_plans 通过 cascade 自动删除）
        db.delete(disease)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")
    
    return {"message": "删除成功"}


@router.put("/{disease_id}/pin")
async def toggle_pin_disease(
    disease_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """切换收藏/置顶状态"""
    disease = db.query(ChronicDisease).filter(
        ChronicDisease.id == disease_id,
        ChronicDisease.user_id == current_user.id
    ).first()
    
    if not disease:
        raise HTTPException(status_code=404, detail="慢性病记录不存在")
    
    disease.is_pinned = not disease.is_pinned
    db.commit()
    db.refresh(disease)
    return {"message": "已收藏" if disease.is_pinned else "已取消收藏", "is_pinned": disease.is_pinned}


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



# ============= 疾病模板 API =============

from app.models.models import (
    DiseaseTemplate, DietRecommendation, MealType,
    ComplicationRecord, ComplicationSeverity,
    ExerciseRecommendation, MedicationReminder, ReminderStatus
)
from app.schemas.schemas import (
    DiseaseTemplateResponse, CreateFromTemplateRequest,
    BatchIndicatorRecordRequest, BatchIndicatorRecordResponse,
    DietRecommendationResponse, PersonalizedDietResponse,
    ComplicationRecordCreate, ComplicationRecordUpdate, ComplicationRecordResponse,
    ExerciseRecommendationResponse, PersonalizedExerciseResponse,
    MedicationReminderCreate, MedicationReminderUpdate, MedicationReminderResponse,
    ExportRequest, ExportTaskResponse
)
import uuid
import csv
import io
import os
from datetime import time as time_type

# 独立路由器用于非嵌套路径
template_router = APIRouter(prefix="/api", tags=["慢性病管理-扩展"])


@template_router.get("/disease-templates", response_model=List[DiseaseTemplateResponse])
async def get_disease_templates(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取疾病类型模板列表"""
    return db.query(DiseaseTemplate).all()


@router.post("/from-template", response_model=ChronicDiseaseResponse)
async def create_from_template(
    data: CreateFromTemplateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """基于模板创建慢性病记录"""
    template = db.query(DiseaseTemplate).filter(
        DiseaseTemplate.disease_type == data.disease_type
    ).first()
    
    if not template:
        raise HTTPException(status_code=400, detail=f"不支持的疾病类型: {data.disease_type}")
    
    try:
        disease = ChronicDisease(
            user_id=current_user.id,
            disease_name=template.display_name,
            icd10_code=template.icd10_code,
            diagnosis_date=data.diagnosis_date,
            diagnosis_hospital=data.diagnosis_hospital,
            diagnosis_doctor=data.diagnosis_doctor,
            current_treatment=data.current_treatment
        )
        db.add(disease)
        db.flush()
        
        # 自动创建指标配置
        for ind in template.default_indicators:
            indicator = DiseaseIndicator(
                disease_id=disease.id,
                indicator_name=ind["name"],
                normal_range_min=ind.get("normal_min"),
                normal_range_max=ind.get("normal_max"),
                unit=ind.get("unit"),
                check_frequency=ind.get("check_frequency")
            )
            db.add(indicator)
        
        db.commit()
        db.refresh(disease)
        return disease
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建失败: {str(e)}")


# ============= 批量指标记录 API =============

@router.post("/{disease_id}/indicators/batch-record", response_model=BatchIndicatorRecordResponse)
async def batch_record_indicators(
    disease_id: int,
    data: BatchIndicatorRecordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """批量记录指标（支持多次测量）"""
    disease = db.query(ChronicDisease).filter(
        ChronicDisease.id == disease_id,
        ChronicDisease.user_id == current_user.id
    ).first()
    
    if not disease:
        raise HTTPException(status_code=404, detail="慢性病记录不存在")
    
    saved_records = []
    alerts = []
    
    try:
        for item in data.records:
            indicator = db.query(DiseaseIndicator).filter(
                DiseaseIndicator.id == item.indicator_id,
                DiseaseIndicator.disease_id == disease_id
            ).first()
            
            if not indicator:
                raise HTTPException(status_code=404, detail=f"指标ID {item.indicator_id} 不存在")
            
            record = IndicatorRecord(
                disease_id=disease_id,
                indicator_id=item.indicator_id,
                value=item.value,
                measurement_date=item.measurement_date,
                recorded_by=item.recorded_by or "self",
                notes=item.notes
            )
            db.add(record)
            db.flush()
            saved_records.append(record)
            
            alert = check_and_create_alert(db, current_user.id, disease_id, indicator, record)
            if alert:
                db.flush()
                alerts.append(alert)
        
        db.commit()
        
        # Refresh all records
        for r in saved_records:
            db.refresh(r)
        for a in alerts:
            db.refresh(a)
        
        return BatchIndicatorRecordResponse(
            saved_records=saved_records,
            alerts=alerts
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"批量记录失败: {str(e)}")


# ============= 饮食建议 API =============

@template_router.get("/diet-recommendations", response_model=List[DietRecommendationResponse])
async def get_diet_recommendations(
    disease_type: Optional[str] = Query(None),
    meal_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取饮食建议"""
    query = db.query(DietRecommendation).filter(DietRecommendation.is_active == True)
    
    if disease_type:
        query = query.filter(DietRecommendation.disease_type == disease_type)
    if meal_type:
        query = query.filter(DietRecommendation.meal_type == meal_type)
    
    return query.order_by(DietRecommendation.priority.desc()).all()


@router.get("/{disease_id}/personalized-diet", response_model=PersonalizedDietResponse)
async def get_personalized_diet(
    disease_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取个性化饮食建议"""
    disease = db.query(ChronicDisease).filter(
        ChronicDisease.id == disease_id,
        ChronicDisease.user_id == current_user.id
    ).first()
    
    if not disease:
        raise HTTPException(status_code=404, detail="慢性病记录不存在")
    
    # 根据疾病名称推断类型
    disease_type = _infer_disease_type(disease.disease_name)
    
    base_query = db.query(DietRecommendation).filter(
        DietRecommendation.disease_type == disease_type,
        DietRecommendation.is_active == True
    )
    
    general = base_query.filter(DietRecommendation.meal_type == None).all()
    breakfast = base_query.filter(DietRecommendation.meal_type == MealType.BREAKFAST).all()
    lunch = base_query.filter(DietRecommendation.meal_type == MealType.LUNCH).all()
    dinner = base_query.filter(DietRecommendation.meal_type == MealType.DINNER).all()
    
    return PersonalizedDietResponse(
        disease_type=disease_type,
        breakfast=breakfast if breakfast else None,
        lunch=lunch if lunch else None,
        dinner=dinner if dinner else None,
        general_tips=general
    )


# ============= 并发症管理 API =============

@router.post("/{disease_id}/complications", response_model=ComplicationRecordResponse)
async def create_complication(
    disease_id: int,
    data: ComplicationRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """记录并发症"""
    disease = db.query(ChronicDisease).filter(
        ChronicDisease.id == disease_id,
        ChronicDisease.user_id == current_user.id
    ).first()
    
    if not disease:
        raise HTTPException(status_code=404, detail="慢性病记录不存在")
    
    complication = ComplicationRecord(
        disease_id=disease_id,
        complication_type=data.complication_type,
        severity=data.severity,
        discovered_date=data.discovered_date,
        symptoms=data.symptoms,
        treatment=data.treatment,
        notes=data.notes
    )
    db.add(complication)
    db.commit()
    db.refresh(complication)
    return complication


@router.get("/{disease_id}/complications", response_model=List[ComplicationRecordResponse])
async def get_complications(
    disease_id: int,
    severity: Optional[str] = Query(None),
    is_resolved: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取并发症列表"""
    disease = db.query(ChronicDisease).filter(
        ChronicDisease.id == disease_id,
        ChronicDisease.user_id == current_user.id
    ).first()
    
    if not disease:
        raise HTTPException(status_code=404, detail="慢性病记录不存在")
    
    query = db.query(ComplicationRecord).filter(ComplicationRecord.disease_id == disease_id)
    
    if severity:
        query = query.filter(ComplicationRecord.severity == severity)
    if is_resolved is not None:
        query = query.filter(ComplicationRecord.is_resolved == is_resolved)
    
    return query.order_by(ComplicationRecord.discovered_date.desc()).all()


@template_router.put("/complications/{complication_id}", response_model=ComplicationRecordResponse)
async def update_complication(
    complication_id: int,
    data: ComplicationRecordUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新并发症状态"""
    complication = db.query(ComplicationRecord).filter(
        ComplicationRecord.id == complication_id
    ).first()
    
    if not complication:
        raise HTTPException(status_code=404, detail="并发症记录不存在")
    
    # 验证权限
    disease = db.query(ChronicDisease).filter(
        ChronicDisease.id == complication.disease_id,
        ChronicDisease.user_id == current_user.id
    ).first()
    
    if not disease:
        raise HTTPException(status_code=403, detail="无权限操作")
    
    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(complication, field, value)
    
    complication.updated_at = datetime.now()
    db.commit()
    db.refresh(complication)
    return complication


# ============= 运动建议 API =============

@template_router.get("/exercise-recommendations", response_model=List[ExerciseRecommendationResponse])
async def get_exercise_recommendations(
    disease_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取运动建议"""
    query = db.query(ExerciseRecommendation).filter(ExerciseRecommendation.is_active == True)
    
    if disease_type:
        query = query.filter(ExerciseRecommendation.disease_type == disease_type)
    
    return query.order_by(ExerciseRecommendation.priority.desc()).all()


@router.get("/{disease_id}/personalized-exercise", response_model=PersonalizedExerciseResponse)
async def get_personalized_exercise(
    disease_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取个性化运动建议"""
    disease = db.query(ChronicDisease).filter(
        ChronicDisease.id == disease_id,
        ChronicDisease.user_id == current_user.id
    ).first()
    
    if not disease:
        raise HTTPException(status_code=404, detail="慢性病记录不存在")
    
    disease_type = _infer_disease_type(disease.disease_name)
    
    exercises = db.query(ExerciseRecommendation).filter(
        ExerciseRecommendation.disease_type == disease_type,
        ExerciseRecommendation.is_active == True
    ).order_by(ExerciseRecommendation.priority.desc()).all()
    
    # 获取最新血糖状态（如果是糖尿病）
    current_status = None
    safety_tips = []
    
    if disease_type == "diabetes":
        latest_record = db.query(IndicatorRecord).filter(
            IndicatorRecord.disease_id == disease_id
        ).order_by(IndicatorRecord.measurement_date.desc()).first()
        
        if latest_record:
            current_status = f"最近一次测量值: {latest_record.value}"
        
        safety_tips = [
            "运动前检测血糖，低于5.6mmol/L时先补充食物",
            "随身携带糖果或含糖饮料以防低血糖",
            "避免空腹运动",
            "运动后注意监测血糖变化"
        ]
    elif disease_type == "hypertension":
        safety_tips = [
            "血压超过180/110mmHg时不宜运动",
            "运动中如感到头晕应立即停止",
            "避免憋气用力的运动",
            "运动前后注意测量血压"
        ]
    
    return PersonalizedExerciseResponse(
        disease_type=disease_type,
        recommended_exercises=exercises,
        current_status=current_status,
        safety_tips=safety_tips
    )


# ============= 用药提醒 API =============

@template_router.post("/medication-reminders")
async def create_medication_reminder(
    data: MedicationReminderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建用药提醒"""
    # 验证疾病归属
    disease = db.query(ChronicDisease).filter(
        ChronicDisease.id == data.disease_id,
        ChronicDisease.user_id == current_user.id
    ).first()
    
    if not disease:
        raise HTTPException(status_code=404, detail="慢性病记录不存在")
    
    try:
        # 解析时间
        parts = data.reminder_time.split(":")
        reminder_time = time_type(int(parts[0]), int(parts[1]), int(parts[2]) if len(parts) > 2 else 0)
        
        reminder = MedicationReminder(
            user_id=current_user.id,
            disease_id=data.disease_id,
            user_medication_id=data.user_medication_id if data.user_medication_id else None,
            reminder_time=reminder_time,
            reminder_days=data.reminder_days,
            advance_minutes=data.advance_minutes,
            repeat_interval_minutes=data.repeat_interval_minutes
        )
        db.add(reminder)
        db.commit()
        db.refresh(reminder)
        
        # 手动构建响应避免序列化问题
        return {
            "id": reminder.id,
            "user_id": reminder.user_id,
            "disease_id": reminder.disease_id,
            "user_medication_id": reminder.user_medication_id,
            "reminder_time": str(reminder.reminder_time),
            "reminder_days": reminder.reminder_days,
            "status": reminder.status.value if reminder.status else "active",
            "advance_minutes": reminder.advance_minutes or 0,
            "repeat_interval_minutes": reminder.repeat_interval_minutes,
            "created_at": reminder.created_at,
            "updated_at": reminder.updated_at
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"创建提醒失败: {str(e)}")


@template_router.get("/medication-reminders")
async def get_medication_reminders(
    disease_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用药提醒列表"""
    query = db.query(MedicationReminder).filter(MedicationReminder.user_id == current_user.id)
    
    if disease_id:
        query = query.filter(MedicationReminder.disease_id == disease_id)
    if status:
        query = query.filter(MedicationReminder.status == status)
    
    reminders = query.order_by(MedicationReminder.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "user_id": r.user_id,
            "disease_id": r.disease_id,
            "user_medication_id": r.user_medication_id,
            "reminder_time": str(r.reminder_time),
            "reminder_days": r.reminder_days,
            "status": r.status.value if r.status else "active",
            "advance_minutes": r.advance_minutes or 0,
            "repeat_interval_minutes": r.repeat_interval_minutes,
            "created_at": r.created_at,
            "updated_at": r.updated_at
        }
        for r in reminders
    ]


@template_router.put("/medication-reminders/{reminder_id}")
async def update_medication_reminder(
    reminder_id: int,
    data: MedicationReminderUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新提醒状态"""
    reminder = db.query(MedicationReminder).filter(
        MedicationReminder.id == reminder_id,
        MedicationReminder.user_id == current_user.id
    ).first()
    
    if not reminder:
        raise HTTPException(status_code=404, detail="提醒不存在")
    
    update_data = data.dict(exclude_unset=True)
    
    if "reminder_time" in update_data and update_data["reminder_time"]:
        parts = update_data["reminder_time"].split(":")
        update_data["reminder_time"] = time_type(int(parts[0]), int(parts[1]), int(parts[2]) if len(parts) > 2 else 0)
    
    # 将 schema 枚举转为 model 枚举
    if "status" in update_data and update_data["status"]:
        status_val = update_data["status"]
        if hasattr(status_val, 'value'):
            status_val = status_val.value
        update_data["status"] = ReminderStatus(status_val)
    
    try:
        for field, value in update_data.items():
            setattr(reminder, field, value)
        
        reminder.updated_at = datetime.now()
        db.commit()
        db.refresh(reminder)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")
    return {
        "id": reminder.id,
        "user_id": reminder.user_id,
        "disease_id": reminder.disease_id,
        "user_medication_id": reminder.user_medication_id,
        "reminder_time": str(reminder.reminder_time),
        "reminder_days": reminder.reminder_days,
        "status": reminder.status.value if reminder.status else "active",
        "advance_minutes": reminder.advance_minutes or 0,
        "repeat_interval_minutes": reminder.repeat_interval_minutes,
        "created_at": reminder.created_at,
        "updated_at": reminder.updated_at
    }


@template_router.delete("/medication-reminders/{reminder_id}")
async def delete_medication_reminder(
    reminder_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除用药提醒"""
    reminder = db.query(MedicationReminder).filter(
        MedicationReminder.id == reminder_id,
        MedicationReminder.user_id == current_user.id
    ).first()
    
    if not reminder:
        raise HTTPException(status_code=404, detail="提醒不存在")
    
    db.delete(reminder)
    db.commit()
    return {"message": "删除成功"}


# ============= 搜索和筛选增强 =============
# 已在现有 list_chronic_diseases 中支持 search 和 control_status
# 添加 disease_type 和日期范围筛选

@router.get("/search/advanced", response_model=List[ChronicDiseaseResponse])
async def advanced_search(
    search: Optional[str] = Query(None),
    disease_type: Optional[str] = Query(None),
    control_status: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """增强搜索和筛选"""
    query = db.query(ChronicDisease).filter(ChronicDisease.user_id == current_user.id)
    
    if search:
        query = query.filter(
            (ChronicDisease.disease_name.ilike(f"%{search}%")) |
            (ChronicDisease.diagnosis_hospital.ilike(f"%{search}%")) |
            (ChronicDisease.current_treatment.ilike(f"%{search}%"))
        )
    
    if disease_type:
        # 根据类型映射到疾病名称
        type_name_map = {
            "hypertension": "高血压",
            "hyperlipidemia": "高血脂",
            "diabetes": "糖尿病"
        }
        name = type_name_map.get(disease_type)
        if name:
            query = query.filter(ChronicDisease.disease_name == name)
    
    if control_status:
        query = query.filter(ChronicDisease.control_status == control_status)
    
    if start_date:
        query = query.filter(ChronicDisease.diagnosis_date >= start_date)
    
    if end_date:
        query = query.filter(ChronicDisease.diagnosis_date <= end_date)
    
    return query.order_by(ChronicDisease.is_pinned.desc(), ChronicDisease.updated_at.desc()).all()


# ============= 数据导出 API =============

# 简单的内存导出任务存储
_export_tasks = {}


@template_router.post("/chronic-diseases/export", response_model=ExportTaskResponse)
async def create_export_task(
    data: ExportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建导出任务"""
    task_id = f"export_{uuid.uuid4().hex[:12]}"
    
    # 验证疾病归属
    diseases = db.query(ChronicDisease).filter(
        ChronicDisease.id.in_(data.disease_ids),
        ChronicDisease.user_id == current_user.id
    ).all()
    
    if not diseases:
        raise HTTPException(status_code=404, detail="未找到可导出的慢性病记录")
    
    if data.format == "csv":
        # 同步生成CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 写入头部
        headers = ["疾病名称", "ICD-10编码", "诊断日期", "诊断医院", "控制状态"]
        if data.include_indicators:
            headers.extend(["指标名称", "测量值", "单位", "测量日期"])
        writer.writerow(headers)
        
        for disease in diseases:
            base_row = [
                disease.disease_name,
                disease.icd10_code or "",
                str(disease.diagnosis_date) if disease.diagnosis_date else "",
                disease.diagnosis_hospital or "",
                disease.control_status.value if disease.control_status else ""
            ]
            
            if data.include_indicators:
                records_query = db.query(IndicatorRecord).filter(
                    IndicatorRecord.disease_id == disease.id
                )
                if data.start_date:
                    records_query = records_query.filter(IndicatorRecord.measurement_date >= datetime.combine(data.start_date, datetime.min.time()))
                if data.end_date:
                    records_query = records_query.filter(IndicatorRecord.measurement_date <= datetime.combine(data.end_date, datetime.max.time()))
                
                records = records_query.order_by(IndicatorRecord.measurement_date.desc()).all()
                
                if records:
                    for record in records:
                        indicator = db.query(DiseaseIndicator).filter(
                            DiseaseIndicator.id == record.indicator_id
                        ).first()
                        row = base_row + [
                            indicator.indicator_name if indicator else "",
                            str(record.value),
                            indicator.unit if indicator else "",
                            str(record.measurement_date)
                        ]
                        writer.writerow(row)
                else:
                    writer.writerow(base_row + ["", "", "", ""])
            else:
                writer.writerow(base_row)
        
        # 保存文件
        export_dir = os.path.join("uploads", "exports")
        os.makedirs(export_dir, exist_ok=True)
        filename = f"{task_id}.csv"
        filepath = os.path.join(export_dir, filename)
        
        with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
            f.write(output.getvalue())
        
        _export_tasks[task_id] = {
            "status": "completed",
            "download_url": f"/api/downloads/{filename}",
            "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
        }
        
        return ExportTaskResponse(
            task_id=task_id,
            status="completed",
            download_url=f"/api/downloads/{filename}",
            expires_at=datetime.now() + timedelta(hours=24)
        )
    else:
        raise HTTPException(status_code=400, detail="暂不支持PDF格式导出")


@template_router.get("/export-tasks/{task_id}", response_model=ExportTaskResponse)
async def get_export_task(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """查询导出任务状态"""
    task = _export_tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="导出任务不存在")
    
    return ExportTaskResponse(
        task_id=task_id,
        status=task["status"],
        download_url=task.get("download_url"),
        expires_at=task.get("expires_at")
    )


@template_router.get("/downloads/{filename}")
async def download_file(
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """下载导出文件"""
    from fastapi.responses import FileResponse
    
    filepath = os.path.join("uploads", "exports", filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    return FileResponse(
        path=filepath,
        filename=filename,
        media_type="text/csv"
    )


# ============= 辅助函数 =============

def _infer_disease_type(disease_name: str) -> str:
    """根据疾病名称推断疾病类型"""
    name_type_map = {
        "高血压": "hypertension",
        "高血脂": "hyperlipidemia",
        "糖尿病": "diabetes"
    }
    for name, dtype in name_type_map.items():
        if name in disease_name:
            return dtype
    return "unknown"
