"""
数据库迁移脚本：为 users 表添加 is_admin 和 is_active 字段
"""
from sqlalchemy import create_engine, text
from app.config import settings

def migrate():
    """执行迁移"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # 检查 is_admin 字段是否存在
        result = conn.execute(text("""
            SELECT COUNT(*) as cnt FROM information_schema.columns 
            WHERE table_schema = DATABASE() 
            AND table_name = 'users' 
            AND column_name = 'is_admin'
        """))
        if result.fetchone()[0] == 0:
            print("添加 is_admin 字段...")
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN is_admin BOOLEAN DEFAULT FALSE,
                ADD INDEX idx_users_is_admin (is_admin)
            """))
            conn.commit()
            print("is_admin 字段添加成功")
        else:
            print("is_admin 字段已存在，跳过")

        # 检查 is_active 字段是否存在
        result = conn.execute(text("""
            SELECT COUNT(*) as cnt FROM information_schema.columns 
            WHERE table_schema = DATABASE() 
            AND table_name = 'users' 
            AND column_name = 'is_active'
        """))
        if result.fetchone()[0] == 0:
            print("添加 is_active 字段...")
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN is_active BOOLEAN DEFAULT TRUE,
                ADD INDEX idx_users_is_active (is_active)
            """))
            conn.commit()
            print("is_active 字段添加成功")
        else:
            print("is_active 字段已存在，跳过")

    print("迁移完成！")

if __name__ == "__main__":
    migrate()
