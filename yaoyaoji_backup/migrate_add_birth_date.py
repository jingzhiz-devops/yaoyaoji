"""
数据库迁移脚本：为 health_profiles 表添加 birth_date 列
运行此脚本以添加新的 birth_date 列到现有数据库
"""
import sys
import os
from datetime import date

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text, inspect
from app.config import settings


def add_birth_date_column():
    """为health_profiles表添加birth_date列"""
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as connection:
            # 检查列是否已存在
            inspector = inspect(engine)
            columns = [col['name'] for col in inspector.get_columns('health_profiles')]
            
            if 'birth_date' in columns:
                print("✅ birth_date 列已经存在，无需添加")
                return
            
            # 添加 birth_date 列
            print("正在为 health_profiles 表添加 birth_date 列...")
            
            # SQLite 的 ALTER TABLE 语法
            alter_sql = text("""
                ALTER TABLE health_profiles 
                ADD COLUMN birth_date DATE NULL
            """)
            
            connection.execute(alter_sql)
            connection.commit()
            
            print("✅ birth_date 列添加成功！")
            
    except Exception as e:
        print(f"❌ 添加列失败: {str(e)}")
        print("\n如果是 SQLite 数据库，你可能需要手动执行以下命令：")
        print("sqlite3 your_database.db \"ALTER TABLE health_profiles ADD COLUMN birth_date DATE NULL;\"")
        raise


if __name__ == "__main__":
    add_birth_date_column()
