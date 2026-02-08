# 文件上传路由
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from pathlib import Path
import shutil
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/upload", tags=["文件上传"])

# 定义上传目录
UPLOAD_DIR = Path("uploads")
MEDICINE_IMAGES_DIR = UPLOAD_DIR / "medicine_images"
AVATAR_IMAGES_DIR = UPLOAD_DIR / "avatars"

# 确保目录存在
MEDICINE_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
AVATAR_IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# 允许的图片格式
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

# 最大文件大小 (5MB)
MAX_FILE_SIZE = 5 * 1024 * 1024


@router.post("/medicine-image", response_model=dict)
async def upload_medicine_image(file: UploadFile = File(...)):
    """
    上传药品包装图
    
    - 支持格式：jpg, jpeg, png, gif, webp
    - 最大大小：5MB
    - 返回：文件访问路径
    """
    # 检查文件扩展名
    file_ext = Path(file.filename).suffix.lower() if file.filename else ""
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件格式。允许的格式：{', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # 读取文件内容检查大小
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件大小超过限制（最大 5MB）"
        )
    
    # 生成唯一文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    filename = f"medicine_{timestamp}_{unique_id}{file_ext}"
    file_path = MEDICINE_IMAGES_DIR / filename
    
    # 保存文件
    try:
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件保存失败：{str(e)}"
        )
    
    # 返回相对路径（用于前端访问）
    relative_path = f"/uploads/medicine_images/{filename}"
    
    return {
        "message": "上传成功",
        "filename": filename,
        "path": relative_path,
        "url": relative_path  # 前端可以直接使用这个URL
    }


@router.delete("/medicine-image/{filename}", response_model=dict)
async def delete_medicine_image(filename: str):
    """
    删除药品包装图
    
    - 需要提供文件名
    """
    file_path = MEDICINE_IMAGES_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    try:
        file_path.unlink()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件删除失败：{str(e)}"
        )
    
    return {"message": "删除成功"}


@router.post("/avatar", response_model=dict)
async def upload_avatar(file: UploadFile = File(...)):
    """
    上传用户头像
    
    - 支持格式：jpg, jpeg, png, gif, webp
    - 最大大小：5MB
    - 返回：文件访问路径
    """
    # 检查文件扩展名
    file_ext = Path(file.filename).suffix.lower() if file.filename else ""
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件格式。允许的格式：{', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # 读取文件内容检查大小
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件大小超过限制（最大 5MB）"
        )
    
    # 生成唯一文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    filename = f"avatar_{timestamp}_{unique_id}{file_ext}"
    file_path = AVATAR_IMAGES_DIR / filename
    
    # 保存文件
    try:
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件保存失败：{str(e)}"
        )
    
    # 返回相对路径（用于前端访问）
    relative_path = f"/uploads/avatars/{filename}"
    
    return {
        "message": "上传成功",
        "filename": filename,
        "path": relative_path,
        "url": relative_path
    }


@router.delete("/avatar/{filename}", response_model=dict)
async def delete_avatar(filename: str):
    """
    删除用户头像
    
    - 需要提供文件名
    """
    file_path = AVATAR_IMAGES_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    try:
        file_path.unlink()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件删除失败：{str(e)}"
        )
    
    return {"message": "删除成功"}
