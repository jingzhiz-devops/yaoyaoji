"""
数据库迁移脚本：为 users 表添加 avatar 列
运行此脚本以添加新的 avatar 列到现有数据库
"""
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text, inspect
from app.config import settings


def add_avatar_column():
    """为users表添加avatar列"""
    engine = create_engine(settings.DATABASE_URL)
    
    try:
        with engine.connect() as connection:
            # 检查列是否已存在
            inspector = inspect(engine)
            columns = [col['name'] for col in inspector.get_columns('users')]
            
            if 'avatar' in columns:
                print("✅ avatar 列已经存在，无需添加")
                return
            
            # 添加 avatar 列
            print("正在为 users 表添加 avatar 列...")
            
            # SQLite/MySQL 的 ALTER TABLE 语法
            alter_sql = text("""
                ALTER TABLE users 
                ADD COLUMN avatar VARCHAR(500) NULL
            """)
            
            connection.execute(alter_sql)
            connection.commit()
            
            print("✅ avatar 列添加成功！")
            
    except Exception as e:
        print(f"❌ 添加列失败: {str(e)}")
        print("\n如果是 SQLite 数据库，你可能需要手动执行以下命令：")
        print('sqlite3 your_database.db "ALTER TABLE users ADD COLUMN avatar VARCHAR(500) NULL;"')
        raise


if __name__ == "__main__":
    add_avatar_column()
