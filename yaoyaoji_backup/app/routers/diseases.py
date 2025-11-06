# 疾病查询路由（AI医生：疾病检索）
# 简化实现：使用数据库数据并支持模糊搜索
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.auth import get_current_user
from app.models.models import User, Disease
from app.schemas.schemas import DiseaseResponse

router = APIRouter(prefix="/api/diseases", tags=["疾病查询"])

# 使用数据库数据

@router.get("/", response_model=List[DiseaseResponse])
async def list_diseases(
    search: str | None = None,
    medicine_name: str | None = None,
    db: Session = Depends(get_db)
):
    """
    疾病列表查询（支持多种搜索方式）
    - search: 按疾病名称/别名/简介/推荐药物/避免搭配模糊搜索
    - medicine_name: 按药品名称反向搜索相关疾病（在推荐药物字段中匹配）
    """
    query = db.query(Disease)
    
    if search:
        s = search.strip()
        query = query.filter(
            (Disease.name.contains(s)) |
            (Disease.aliases.contains(s)) |
            (Disease.description.contains(s)) |
            (Disease.recommended.contains(s)) |
            (Disease.avoid.contains(s))
        )
    
    if medicine_name:
        # 通过药品名称反向查询：在推荐药物字段中匹配
        m = medicine_name.strip()
        query = query.filter(Disease.recommended.contains(m))
    
    return query.order_by(Disease.name.asc()).all()
