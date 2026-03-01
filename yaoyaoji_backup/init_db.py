"""
数据库初始化脚本
运行此脚本以创建所有数据库表
"""
import sys
import os

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base, engine
from app.models.models import (
    User, Medicine, UserMedication, 
    MedicationSchedule, MedicationRecord, SymptomRecord,
    Disease, Family, FamilyMember, EmergencyContact,
    HealthProfile, AllergyRecord, FamilyHistory, SurgeryRecord,
    CheckupReport, VaccinationRecord,
    ChatSession, ChatMessage, KnowledgeBase,
    ChronicDisease, DiseaseIndicator, IndicatorRecord,
    FollowupPlan, FollowupRecord, IndicatorAlert, MedicationAdherence,
    DiseaseTemplate, DietRecommendation, ComplicationRecord,
    ExerciseRecommendation, MedicationReminder
)


def init_db():
    """初始化数据库，创建所有表"""
    print("开始创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建成功！")
    
    # 打印已创建的表
    print("\n已创建的表:")
    for table in Base.metadata.sorted_tables:
        print(f"  - {table.name}")


def drop_all_tables():
    """删除所有表（慎用）"""
    print("⚠️  警告：即将删除所有数据库表...")
    confirm = input("确认删除吗？(yes/no): ")
    if confirm.lower() == "yes":
        Base.metadata.drop_all(bind=engine)
        print("✅ 所有表已删除")
    else:
        print("❌ 操作已取消")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--drop":
        drop_all_tables()
    else:
        init_db()
