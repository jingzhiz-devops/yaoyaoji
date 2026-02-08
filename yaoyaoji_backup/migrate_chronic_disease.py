"""
数据库迁移脚本：为慢性病管理模块创建表
"""
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, inspect
from app.config import settings
from app.models.models import Base


def create_chronic_disease_tables():
    """创建慢性病管理相关的所有表"""
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        # 获取数据库检查器
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        # 需要创建的表
        required_tables = {
            'chronic_diseases',
            'disease_indicators',
            'indicator_records',
            'followup_plans',
            'followup_records'
        }
        
        # 检查哪些表已存在
        missing_tables = required_tables - set(existing_tables)
        
        if not missing_tables:
            print("✅ 所有慢性病管理表都已存在，无需创建")
            return
        
        print(f"📋 需要创建的表：{', '.join(missing_tables)}")
        
        # 创建缺失的表
        Base.metadata.create_all(engine)
        
        print("✅ 慢性病管理表创建成功！")
        
        # 验证表是否已创建
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        print("\n📊 已创建的慢性病管理表：")
        for table_name in sorted(required_tables):
            if table_name in tables:
                columns = [col['name'] for col in inspector.get_columns(table_name)]
                print(f"  ✓ {table_name}")
                print(f"    列: {', '.join(columns[:5])}" + ("..." if len(columns) > 5 else ""))
        
    except Exception as e:
        print(f"❌ 创建表失败: {str(e)}")
        raise


if __name__ == "__main__":
    print("🔧 开始创建慢性病管理模块的数据库表...")
    print(f"📍 数据库: {settings.DATABASE_URL}\n")
    
    create_chronic_disease_tables()
    
    print("\n✨ 迁移完成！")
