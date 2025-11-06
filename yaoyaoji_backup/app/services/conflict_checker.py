"""
用药冲突检测服务
"""
from typing import List
from sqlalchemy.orm import Session

from app.models.models import UserMedication, Medicine
from app.schemas.schemas import ConflictWarning


def check_drug_interactions(
    db: Session,
    user_id: int,
    new_medicine_id: int | None = None
) -> List[ConflictWarning]:
    """
    检测用药冲突
    
    Args:
        db: 数据库会话
        user_id: 用户ID
        new_medicine_id: 新添加的药品ID（可选）
    
    Returns:
        冲突警告列表
    """
    warnings = []
    
    # 获取用户当前活跃的药品列表
    user_meds = db.query(UserMedication).filter(
        UserMedication.user_id == user_id,
        UserMedication.status == "active"
    ).all()
    
    # 获取药品详情
    medicines = []
    for um in user_meds:
        med = db.query(Medicine).filter(Medicine.id == um.medicine_id).first()
        if med:
            medicines.append(med)
    
    # 如果有新药品，也加入检测
    if new_medicine_id:
        new_med = db.query(Medicine).filter(Medicine.id == new_medicine_id).first()
        if new_med:
            medicines.append(new_med)
    
    # 简单的冲突检测逻辑（实际应用需要接入专业的药品数据库）
    # 这里仅做示例演示
    for i, med1 in enumerate(medicines):
        for med2 in medicines[i+1:]:
            # 检测禁忌信息中是否包含对方药品名称
            conflict = _check_contraindication(med1, med2)
            if conflict:
                warnings.append(conflict)
    
    return warnings


def _check_contraindication(med1: Medicine, med2: Medicine) -> ConflictWarning | None:
    """
    检查两个药品之间是否存在禁忌
    
    实际应用中应该：
    1. 接入专业的药品相互作用数据库
    2. 使用药品成分进行精准匹配
    3. 考虑剂量、用药时间等因素
    """
    # 示例：简单的文本匹配检测
    contraindication1 = str(getattr(med1, 'contraindications', ''))
    contraindication2 = str(getattr(med2, 'contraindications', ''))
    
    if not contraindication1 or not contraindication2:
        return None
    
    name1 = str(getattr(med1, 'name', ''))
    name2 = str(getattr(med2, 'name', ''))
    generic_name1 = str(getattr(med1, 'generic_name', ''))
    generic_name2 = str(getattr(med2, 'generic_name', ''))
    
    # 检查med1的禁忌中是否提到med2
    if name2 in contraindication1 or generic_name2 in contraindication1:
        return ConflictWarning(
            medicine_1=name1,
            medicine_2=name2,
            warning=f"{name1} 的禁忌信息中提到了 {name2}，请咨询医生！",
            severity="high"
        )
    
    # 检查med2的禁忌中是否提到med1
    if name1 in contraindication2 or generic_name1 in contraindication2:
        return ConflictWarning(
            medicine_1=name1,
            medicine_2=name2,
            warning=f"{name2} 的禁忌信息中提到了 {name1}，请咨询医生！",
            severity="high"
        )
    
    # 检查一些常见的危险组合关键词
    dangerous_keywords = [
        ("抗凝", "阿司匹林"),
        ("降压", "降压"),
        ("镇静", "镇静"),
        ("抗生素", "抗生素"),
    ]
    
    for keyword1, keyword2 in dangerous_keywords:
        if (keyword1 in name1 or keyword1 in contraindication1) and \
           (keyword2 in name2 or keyword2 in contraindication2):
            return ConflictWarning(
                medicine_1=name1,
                medicine_2=name2,
                warning=f"{name1} 和 {name2} 可能存在相互作用，建议咨询医生",
                severity="medium"
            )
    
    return None


def get_conflict_check_endpoint(
    user_id: int,
    medicine_id: int,
    db: Session
) -> dict:
    """
    用于API端点的冲突检测
    """
    warnings = check_drug_interactions(db, user_id, medicine_id)
    
    return {
        "has_conflicts": len(warnings) > 0,
        "conflict_count": len(warnings),
        "warnings": warnings
    }
