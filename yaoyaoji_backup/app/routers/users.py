"""
用户认证和管理路由
"""
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.responses import Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import User
from app.schemas.schemas import (
    UserCreate, UserResponse, UserLogin, Token, MessageResponse
)
from app.auth import (
    get_password_hash, authenticate_user, create_access_token, get_current_user
)
from app.captcha import generate_captcha, verify_captcha
from app.config import settings

router = APIRouter(prefix="/api/users", tags=["用户管理"])
auth_router = APIRouter(prefix="/api/auth", tags=["认证"])


@auth_router.get("/captcha")
async def get_captcha():
    """获取图形验证码"""
    captcha_id, image_bytes = generate_captcha()
    return Response(
        content=image_bytes,
        media_type="image/png",
        headers={"X-Captcha-Id": captcha_id},
    )


@auth_router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    # 验证码校验
    if not user.captcha_id or not user.captcha_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请输入验证码",
        )
    if not verify_captcha(user.captcha_id, user.captcha_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误或已过期",
        )

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
    captcha_id: str = Form(""),
    captcha_code: str = Form(""),
    db: Session = Depends(get_db)
):
    """用户登录"""
    # 验证码校验
    if not captcha_id or not captcha_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="请输入验证码",
        )
    if not verify_captcha(captcha_id, captcha_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="验证码错误或已过期",
        )

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
    
    # 更新最后登录时间
    user.last_login = datetime.now()
    db.commit()
    
    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.post("/google-login", response_model=Token)
async def google_login(
    credential: str = Form(...),
    db: Session = Depends(get_db)
):
    """Google 第三方登录"""
    from google.oauth2 import id_token
    from google.auth.transport import requests as google_requests

    try:
        idinfo = id_token.verify_oauth2_token(
            credential,
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google 登录验证失败",
        )

    email = idinfo.get("email")
    name = idinfo.get("name", email.split("@")[0] if email else "google_user")

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无法获取 Google 账号邮箱",
        )

    # 查找已有用户（先按邮箱匹配）
    user = db.query(User).filter(User.email == email).first()
    if not user:
        # 自动注册
        import uuid
        random_pw = get_password_hash(uuid.uuid4().hex)
        user = User(
            username=name,
            password_hash=random_pw,
            email=email,
            avatar=idinfo.get("picture", ""),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="该账号已被禁用，请联系管理员",
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    user.last_login = datetime.now()
    db.commit()

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


@router.patch("/update-profile", response_model=UserResponse)
async def update_profile(
    phone: str = None,
    email: str = None,
    feishu_webhook: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新个人信息（手机号、邮箱、飞书Webhook）"""
    # 验证手机号格式
    if phone is not None:
        if phone and not phone.isdigit():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号格式不正确"
            )
        if phone and len(phone) != 11:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="手机号必须是11位数字"
            )
        # 检查手机号是否已被其他用户使用
        if phone:
            existing_phone = db.query(User).filter(
                User.phone == phone,
                User.id != current_user.id
            ).first()
            if existing_phone:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="该手机号已被其他用户使用"
                )
        current_user.phone = phone or None
    
    # 验证邮箱格式
    if email is not None:
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if email and not re.match(email_pattern, email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱格式不正确"
            )
        # 检查邮箱是否已被其他用户使用
        if email:
            existing_email = db.query(User).filter(
                User.email == email,
                User.id != current_user.id
            ).first()
            if existing_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="该邮箱已被其他用户使用"
                )
        current_user.email = email or None
    
    # 验证飞书Webhook格式
    if feishu_webhook is not None:
        if feishu_webhook:
            import re
            # 飞书Webhook URL 格式: https://open.feishu.cn/open-apis/bot/v2/hook/xxx
            if not feishu_webhook.startswith('https://open.feishu.cn/open-apis/bot/'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="飞书Webhook地址格式不正确，应以 https://open.feishu.cn/open-apis/bot/ 开头"
                )
        current_user.feishu_webhook = feishu_webhook or None
    
    db.commit()
    db.refresh(current_user)
    
    return current_user
