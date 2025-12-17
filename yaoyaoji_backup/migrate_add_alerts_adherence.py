"""
数据库迁移脚本：添加异常值预警和用药依从性追踪表
"""
import logging
from app.database import engine, Base
from app.models.models import IndicatorAlert, MedicationAdherence, AlertLevel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate():
    """执行迁移"""
    try:
        logger.info("开始创建异常值预警和用药依从性追踪表...")
        
        # 创建新表
        Base.metadata.create_all(bind=engine, tables=[
            IndicatorAlert.__table__,
            MedicationAdherence.__table__
        ])
        
        logger.info("✓ 成功创建以下表：")
        logger.info("  - indicator_alerts (指标异常预警表)")
        logger.info("  - medication_adherence (用药依从性追踪表)")
        logger.info("迁移完成！")
        
    except Exception as e:
        logger.error(f"迁移失败: {str(e)}")
        raise


if __name__ == "__main__":
    migrate()
