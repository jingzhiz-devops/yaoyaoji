"""
将指定用户设置为管理员
用法: python set_admin.py <用户名>
"""
import sys
from sqlalchemy import create_engine, text
from app.config import settings

def set_admin(username: str):
    """将用户设置为管理员"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        result = conn.execute(text(
            "UPDATE users SET is_admin = TRUE WHERE username = :username"
        ), {"username": username})
        conn.commit()
        
        if result.rowcount > 0:
            print(f"用户 '{username}' 已设置为管理员")
        else:
            print(f"未找到用户 '{username}'")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python set_admin.py <用户名>")
        sys.exit(1)
    set_admin(sys.argv[1])
