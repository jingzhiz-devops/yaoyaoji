"""
给 users 表添加 last_login 字段
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import engine
from sqlalchemy import text

def migrate():
    with engine.connect() as conn:
        # 检查字段是否已存在
        try:
            conn.execute(text("SELECT last_login FROM users LIMIT 1"))
            print("last_login 字段已存在，跳过")
            return
        except Exception:
            pass

        conn.execute(text("ALTER TABLE users ADD COLUMN last_login DATETIME NULL"))
        conn.commit()
        print("已添加 last_login 字段")

if __name__ == "__main__":
    migrate()
