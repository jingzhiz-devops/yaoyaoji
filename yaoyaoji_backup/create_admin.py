"""
创建默认管理员账户
用户名: admin
密码: admin
"""
from sqlalchemy import create_engine, text
from passlib.context import CryptContext
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin():
    """创建默认管理员账户"""
    engine = create_engine(settings.DATABASE_URL)
    password_hash = pwd_context.hash("admin")
    
    with engine.connect() as conn:
        # 检查 admin 用户是否存在
        result = conn.execute(text(
            "SELECT id FROM users WHERE username = 'admin'"
        ))
        existing = result.fetchone()
        
        if existing:
            # 更新为管理员
            conn.execute(text(
                "UPDATE users SET is_admin = TRUE, is_active = TRUE, password_hash = :pwd WHERE username = 'admin'"
            ), {"pwd": password_hash})
            print("admin 用户已存在，已更新为管理员并重置密码")
        else:
            # 创建新用户
            conn.execute(text("""
                INSERT INTO users (username, password_hash, is_admin, is_active, is_family_admin)
                VALUES ('admin', :pwd, TRUE, TRUE, TRUE)
            """), {"pwd": password_hash})
            print("admin 管理员账户创建成功")
        
        conn.commit()
    
    print("用户名: admin")
    print("密码: admin")

if __name__ == "__main__":
    create_admin()
