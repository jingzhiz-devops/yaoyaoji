"""
FastAPI 主应用入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.config import settings

# 导入所有路由
from app.routers.users import router as users_router, auth_router
from app.routers.medicines import router as medicines_router, user_med_router
from app.routers.schedules import schedule_router, record_router
from app.routers.symptoms import router as symptoms_router
from app.routers.diseases import router as diseases_router
from app.routers.health_profile import router as health_profile_router
from app.routers.family import router as family_router
from app.routers.upload import router as upload_router
from app.routers.ai_doctor import router as ai_doctor_router
from app.routers.chronic_disease import router as chronic_disease_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="药药记 - 智能用药安全管理系统",
)

# CORS 配置 - 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth_router)  # 认证路由
app.include_router(users_router)  # 用户管理
app.include_router(medicines_router)  # 药品库管理
app.include_router(user_med_router)  # 用户药箱管理
app.include_router(schedule_router)  # 用药计划
app.include_router(record_router)  # 用药记录
app.include_router(symptoms_router)  # 症状记录
app.include_router(diseases_router)  # 疾病查询
app.include_router(health_profile_router)  # 健康档案
app.include_router(family_router)  # 家庭管理
app.include_router(upload_router)  # 文件上传
app.include_router(ai_doctor_router)  # AI医生
app.include_router(chronic_disease_router)  # 慢性病管理

# 配置静态文件服务（用于访问上传的图片）
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
(UPLOAD_DIR / "medicine_images").mkdir(exist_ok=True)
(UPLOAD_DIR / "avatars").mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/")
async def root():
    """根路径健康检查"""
    return {
        "message": "欢迎使用药药记 API",
        "version": settings.APP_VERSION,
        "status": "healthy",
        "docs": "/docs",  # Swagger UI
        "redoc": "/redoc"  # ReDoc
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "ok"}
