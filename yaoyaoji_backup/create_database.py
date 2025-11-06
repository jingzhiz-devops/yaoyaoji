"""
创建 MySQL 数据库脚本
"""
import pymysql
from app.config import settings


def create_database():
    """创建数据库"""
    try:
        # 连接到 MySQL（不指定数据库）
        connection = pymysql.connect(
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
            user=settings.MYSQL_USER,
            password=settings.MYSQL_PASSWORD,
            charset='utf8mb4'
        )

        cursor = connection.cursor()

        # 创建数据库
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS {settings.MYSQL_DATABASE} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✅ 数据库 '{settings.MYSQL_DATABASE}' 创建成功！")

        cursor.close()
        connection.close()

    except Exception as e:
        print(f"❌ 错误: {e}")


if __name__ == "__main__":
    create_database()
