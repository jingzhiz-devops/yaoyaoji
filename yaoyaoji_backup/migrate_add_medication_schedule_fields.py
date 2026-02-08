"""
数据库迁移脚本：为 medication_schedules 表添加新字段
- purchase_date: 药品购入日期
- therapy_duration: 吃药疗程（天数）
- remind_advance_days: 提前提醒备药天数（默认5天）
"""
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text, inspect
from app.config import settings


def add_medication_schedule_fields():
    """为 medication_schedules 表添加新字段"""
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as connection:
            # 检查列是否已存在
            inspector = inspect(engine)
            columns = [col['name'] for col in inspector.get_columns('medication_schedules')]
            
            fields_to_add = {
                'purchase_date': 'DATE NULL',
                'therapy_duration': 'INTEGER NULL',
                'remind_advance_days': 'INTEGER DEFAULT 5'
            }
            
            fields_added = []
            for field_name, field_type in fields_to_add.items():
                if field_name not in columns:
                    print(f"正在添加 {field_name} 列...")
                    alter_sql = text(f"""
                        ALTER TABLE medication_schedules 
                        ADD COLUMN {field_name} {field_type}
                    """)
                    connection.execute(alter_sql)
                    fields_added.append(field_name)
                else:
                    print(f"✅ {field_name} 列已存在")
            
            if fields_added:
                connection.commit()
                print(f"\n✅ 成功添加了以下列：{', '.join(fields_added)}")
            else:
                print("\n✅ 所有列都已存在，无需添加")
            
    except Exception as e:
        print(f"❌ 添加列失败: {str(e)}")
        print("\n如果是 MySQL 数据库，你可能需要手动执行以下命令：")
        print("""
        ALTER TABLE medication_schedules ADD COLUMN purchase_date DATE NULL;
        ALTER TABLE medication_schedules ADD COLUMN therapy_duration INTEGER NULL;
        ALTER TABLE medication_schedules ADD COLUMN remind_advance_days INTEGER DEFAULT 5;
        """)
        raise


if __name__ == "__main__":
    add_medication_schedule_fields()
