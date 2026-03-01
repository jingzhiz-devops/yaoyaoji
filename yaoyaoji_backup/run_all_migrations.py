
"""
统一数据库迁移脚本：运行所有待执行的迁移
"""
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text, inspect
from app.config import settings
from app.database import engine, Base
from app.models.models import (
    ChronicDisease, DiseaseIndicator, IndicatorRecord, 
    FollowupPlan, FollowupRecord, IndicatorAlert, MedicationAdherence,
    DiseaseTemplate, DietRecommendation, ComplicationRecord,
    ExerciseRecommendation, MedicationReminder
)


def run_all_migrations():
    """运行所有数据库迁移"""
    print("=" * 60)
    print("🔧 药药记数据库迁移工具")
    print("=" * 60)
    print(f"📍 数据库: {settings.DATABASE_URL.split('@')[1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}\n")
    
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        # 1. 检查并添加 users 表 avatar 字段
        print("\n📋 [1/5] 检查 users 表字段...")
        if 'users' in existing_tables:
            columns = [col['name'] for col in inspector.get_columns('users')]
            if 'avatar' not in columns:
                print("  ➕ 正在添加 avatar 列...")
                with engine.connect() as conn:
                    try:
                        conn.execute(text("ALTER TABLE users ADD COLUMN avatar VARCHAR(500) NULL"))
                        conn.commit()
                        print("  ✅ avatar 列添加成功")
                    except Exception as e:
                        if 'Duplicate column' in str(e):
                            print("  ✅ avatar 列已存在")
                        else:
                            print(f"  ⚠️ avatar 列添加失败: {e}")
            else:
                print("  ✅ avatar 列已存在")
        else:
            print("  ⚠️ users 表不存在")
        
        # 2. 检查并添加 medication_schedules 新字段
        print("\n📋 [2/5] 检查 medication_schedules 表字段...")
        if 'medication_schedules' in existing_tables:
            columns = [col['name'] for col in inspector.get_columns('medication_schedules')]
            fields_to_add = {
                'purchase_date': 'DATE NULL',
                'therapy_duration': 'INTEGER NULL',
                'remind_advance_days': 'INTEGER DEFAULT 5',
                'notes': 'TEXT NULL'
            }
            
            with engine.connect() as conn:
                for field_name, field_type in fields_to_add.items():
                    if field_name not in columns:
                        print(f"  ➕ 正在添加 {field_name} 列...")
                        try:
                            conn.execute(text(f"ALTER TABLE medication_schedules ADD COLUMN {field_name} {field_type}"))
                            conn.commit()
                            print(f"  ✅ {field_name} 列添加成功")
                        except Exception as e:
                            if 'Duplicate column' in str(e):
                                print(f"  ✅ {field_name} 列已存在")
                            else:
                                print(f"  ⚠️ {field_name} 列添加失败: {e}")
                    else:
                        print(f"  ✅ {field_name} 列已存在")
        else:
            print("  ⚠️ medication_schedules 表不存在")
        
        # 3. 检查并添加 health_profiles 的 birth_date 字段
        print("\n📋 [3/5] 检查 health_profiles 表字段...")
        if 'health_profiles' in existing_tables:
            columns = [col['name'] for col in inspector.get_columns('health_profiles')]
            if 'birth_date' not in columns:
                print("  ➕ 正在添加 birth_date 列...")
                with engine.connect() as conn:
                    try:
                        conn.execute(text("ALTER TABLE health_profiles ADD COLUMN birth_date DATE NULL"))
                        conn.commit()
                        print("  ✅ birth_date 列添加成功")
                    except Exception as e:
                        if 'Duplicate column' in str(e):
                            print("  ✅ birth_date 列已存在")
                        else:
                            print(f"  ⚠️ birth_date 列添加失败: {e}")
            else:
                print("  ✅ birth_date 列已存在")
        else:
            print("  ⚠️ health_profiles 表不存在")
        
        # 4. 创建慢性病管理相关表
        print("\n📋 [4/5] 检查慢性病管理模块表...")
        chronic_tables = {
            'chronic_diseases': ChronicDisease,
            'disease_indicators': DiseaseIndicator,
            'indicator_records': IndicatorRecord,
            'followup_plans': FollowupPlan,
            'followup_records': FollowupRecord
        }
        
        for table_name, model in chronic_tables.items():
            if table_name not in existing_tables:
                print(f"  ➕ 正在创建 {table_name} 表...")
                try:
                    model.__table__.create(engine)
                    print(f"  ✅ {table_name} 表创建成功")
                except Exception as e:
                    if 'already exists' in str(e).lower():
                        print(f"  ✅ {table_name} 表已存在")
                    else:
                        print(f"  ⚠️ {table_name} 表创建失败: {e}")
            else:
                print(f"  ✅ {table_name} 表已存在")
        
        # 5. 创建预警和依从性表
        print("\n📋 [5/7] 检查预警和依从性追踪表...")
        alert_tables = {
            'indicator_alerts': IndicatorAlert,
            'medication_adherence': MedicationAdherence
        }
        
        for table_name, model in alert_tables.items():
            if table_name not in existing_tables:
                print(f"  ➕ 正在创建 {table_name} 表...")
                try:
                    model.__table__.create(engine)
                    print(f"  ✅ {table_name} 表创建成功")
                except Exception as e:
                    if 'already exists' in str(e).lower():
                        print(f"  ✅ {table_name} 表已存在")
                    else:
                        print(f"  ⚠️ {table_name} 表创建失败: {e}")
            else:
                print(f"  ✅ {table_name} 表已存在")
        
        # 6. 创建慢性病扩展模块表（模板、饮食、运动、并发症、用药提醒）
        print("\n📋 [6/7] 检查慢性病扩展模块表...")
        extension_tables = {
            'disease_templates': DiseaseTemplate,
            'diet_recommendations': DietRecommendation,
            'exercise_recommendations': ExerciseRecommendation,
            'complication_records': ComplicationRecord,
            'medication_reminders': MedicationReminder
        }
        
        for table_name, model in extension_tables.items():
            if table_name not in existing_tables:
                print(f"  ➕ 正在创建 {table_name} 表...")
                try:
                    model.__table__.create(engine)
                    print(f"  ✅ {table_name} 表创建成功")
                except Exception as e:
                    if 'already exists' in str(e).lower():
                        print(f"  ✅ {table_name} 表已存在")
                    else:
                        print(f"  ⚠️ {table_name} 表创建失败: {e}")
            else:
                print(f"  ✅ {table_name} 表已存在")
        
        # 7. 修复 medication_reminders 表的 user_medication_id 为可空
        print("\n📋 [7/8] 检查 medication_reminders 字段约束...")
        if 'medication_reminders' in inspector.get_table_names():
            columns = {col['name']: col for col in inspector.get_columns('medication_reminders')}
            if 'user_medication_id' in columns and not columns['user_medication_id'].get('nullable', True):
                print("  ➕ 修改 user_medication_id 为可空...")
                with engine.connect() as conn:
                    try:
                        conn.execute(text("ALTER TABLE medication_reminders MODIFY COLUMN user_medication_id INTEGER NULL"))
                        conn.commit()
                        print("  ✅ user_medication_id 已改为可空")
                    except Exception as e:
                        print(f"  ⚠️ 修改失败: {e}")
            else:
                print("  ✅ user_medication_id 已是可空")
        
        # 8. 给 chronic_diseases 表添加 is_pinned 字段
        print("\n📋 [8/8] 检查 chronic_diseases 表 is_pinned 字段...")
        if 'chronic_diseases' in inspector.get_table_names():
            columns = [col['name'] for col in inspector.get_columns('chronic_diseases')]
            if 'is_pinned' not in columns:
                print("  ➕ 正在添加 is_pinned 列...")
                with engine.connect() as conn:
                    try:
                        conn.execute(text("ALTER TABLE chronic_diseases ADD COLUMN is_pinned BOOLEAN DEFAULT FALSE"))
                        conn.commit()
                        print("  ✅ is_pinned 列添加成功")
                    except Exception as e:
                        if 'Duplicate column' in str(e):
                            print("  ✅ is_pinned 列已存在")
                        else:
                            print(f"  ⚠️ is_pinned 列添加失败: {e}")
            else:
                print("  ✅ is_pinned 列已存在")
        
        print("\n" + "=" * 60)
        print("✨ 数据库迁移完成！")
        print("=" * 60)
        
        # 显示最终表结构
        inspector = inspect(engine)
        final_tables = inspector.get_table_names()
        print(f"\n📊 当前数据库共有 {len(final_tables)} 张表:")
        for t in sorted(final_tables):
            print(f"  • {t}")
            
    except Exception as e:
        print(f"\n❌ 迁移过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    run_all_migrations()
