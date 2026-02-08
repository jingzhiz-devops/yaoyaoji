"""
用户认证和管理路由
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db
from app.models.models import User
from app.schemas.schemas import (
    UserCreate, UserResponse, UserLogin, Token, MessageResponse
)
from app.auth import (
    get_password_hash, authenticate_user, create_access_token, get_current_user
)
from app.config import settings

router = APIRouter(prefix="/api/users", tags=["用户管理"])
auth_router = APIRouter(prefix="/api/auth", tags=["认证"])


@auth_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 检查邮箱是否已存在
    if user.email:
        existing_email = db.query(User).filter(User.email == user.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被使用"
            )
    
    # 创建新用户
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        password_hash=hashed_password,
        email=user.email
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@auth_router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """用户登录"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取指定用户信息"""
    # 只能查看自己的信息
    if getattr(current_user, 'id') != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问其他用户信息"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return user


@router.patch("/change-password", response_model=MessageResponse)
async def change_password(
    old_password: str,
    new_password: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """修改密码"""
    # 验证旧密码
    user = authenticate_user(db, current_user.username, old_password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="原密码错误"
        )
    
    # 验证新密码
    if len(new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码至少6个字符"
        )
    
    if old_password == new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码不能与原密码相同"
        )
    
    # 更新密码
    current_user.password_hash = get_password_hash(new_password)
    db.commit()
    
    return MessageResponse(message="密码修改成功")


@router.patch("/change-username", response_model=MessageResponse)
async def change_username(
    new_username: str,
    password: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """修改用户名"""
    # 验证密码
    user = authenticate_user(db, current_user.username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码错误"
        )
    
    # 验证新用户名
    if len(new_username) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名至少2个字符"
        )
    
    # 验证用户名格式（支持中文、英文、数字、下划线）
    import re
    if not re.match(r'^[\u4e00-\u9fa5a-zA-Z0-9_]+$', new_username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名只能包含中文、英文、数字和下划线"
        )
    
    if new_username == current_user.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新用户名不能与原用户名相同"
        )
    
    # 检查用户名是否已被使用
    existing_user = db.query(User).filter(User.username == new_username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已被使用"
        )
    
    # 更新用户名
    current_user.username = new_username
    db.commit()
    
    return MessageResponse(message="用户名修改成功")


@router.patch("/change-avatar", response_model=MessageResponse)
async def change_avatar(
    avatar_url: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """修改用户头像"""
    # 更新头像
    current_user.avatar = avatar_url
    db.commit()
    
    return MessageResponse(message="头像修改成功")
