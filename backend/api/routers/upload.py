"""
文件上传API路由
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from typing import List
import os
import uuid
from datetime import datetime
from pathlib import Path
import shutil

from backend.api.dependencies import get_current_farmer
from backend.models.farmer import Farmer
from backend.config.settings import settings

router = APIRouter()

# 上传目录配置
UPLOAD_DIR = Path("uploads")
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".webm"}
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100MB


def ensure_upload_dir():
    """确保上传目录存在"""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    (UPLOAD_DIR / "images").mkdir(exist_ok=True)
    (UPLOAD_DIR / "videos").mkdir(exist_ok=True)
    (UPLOAD_DIR / "documents").mkdir(exist_ok=True)


def get_file_extension(filename: str) -> str:
    """获取文件扩展名"""
    return Path(filename).suffix.lower()


def generate_unique_filename(original_filename: str) -> str:
    """生成唯一文件名"""
    ext = get_file_extension(original_filename)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    return f"{timestamp}_{unique_id}{ext}"


@router.post(
    "/images",
    summary="上传图片",
    description="上传产品图片，支持JPG、PNG、GIF、WebP格式"
)
async def upload_image(
    file: UploadFile = File(...),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """
    上传图片文件
    
    Args:
        file: 上传的图片文件
        current_farmer: 当前登录的农户
    
    Returns:
        包含图片URL的响应
    """
    # 检查文件扩展名
    ext = get_file_extension(file.filename)
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的图片格式。允许的格式: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
        )
    
    # 读取文件内容检查大小
    contents = await file.read()
    if len(contents) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"图片文件过大。最大允许: {MAX_IMAGE_SIZE / 1024 / 1024}MB"
        )
    
    # 确保上传目录存在
    ensure_upload_dir()
    
    # 生成唯一文件名
    filename = generate_unique_filename(file.filename)
    file_path = UPLOAD_DIR / "images" / filename
    
    # 保存文件
    try:
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件保存失败: {str(e)}"
        )
    
    # 返回文件URL
    file_url = f"/uploads/images/{filename}"
    
    return {
        "url": file_url,
        "filename": filename,
        "original_filename": file.filename,
        "size": len(contents),
        "content_type": file.content_type
    }


@router.post(
    "/images/batch",
    summary="批量上传图片",
    description="一次上传多张图片"
)
async def upload_images_batch(
    files: List[UploadFile] = File(...),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """
    批量上传图片
    
    Args:
        files: 上传的图片文件列表
        current_farmer: 当前登录的农户
    
    Returns:
        包含所有图片URL的响应
    """
    if len(files) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="一次最多上传10张图片"
        )
    
    results = []
    errors = []
    
    for file in files:
        try:
            # 检查文件扩展名
            ext = get_file_extension(file.filename)
            if ext not in ALLOWED_IMAGE_EXTENSIONS:
                errors.append({
                    "filename": file.filename,
                    "error": f"不支持的格式: {ext}"
                })
                continue
            
            # 读取文件内容检查大小
            contents = await file.read()
            if len(contents) > MAX_IMAGE_SIZE:
                errors.append({
                    "filename": file.filename,
                    "error": "文件过大"
                })
                continue
            
            # 确保上传目录存在
            ensure_upload_dir()
            
            # 生成唯一文件名
            filename = generate_unique_filename(file.filename)
            file_path = UPLOAD_DIR / "images" / filename
            
            # 保存文件
            with open(file_path, "wb") as f:
                f.write(contents)
            
            # 添加到结果
            results.append({
                "url": f"/uploads/images/{filename}",
                "filename": filename,
                "original_filename": file.filename,
                "size": len(contents)
            })
            
        except Exception as e:
            errors.append({
                "filename": file.filename,
                "error": str(e)
            })
    
    return {
        "success": results,
        "errors": errors,
        "total": len(files),
        "success_count": len(results),
        "error_count": len(errors)
    }


@router.post(
    "/videos",
    summary="上传视频",
    description="上传产品视频，支持MP4、MOV、AVI、WebM格式"
)
async def upload_video(
    file: UploadFile = File(...),
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """
    上传视频文件
    
    Args:
        file: 上传的视频文件
        current_farmer: 当前登录的农户
    
    Returns:
        包含视频URL的响应
    """
    # 检查文件扩展名
    ext = get_file_extension(file.filename)
    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的视频格式。允许的格式: {', '.join(ALLOWED_VIDEO_EXTENSIONS)}"
        )
    
    # 读取文件内容检查大小
    contents = await file.read()
    if len(contents) > MAX_VIDEO_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"视频文件过大。最大允许: {MAX_VIDEO_SIZE / 1024 / 1024}MB"
        )
    
    # 确保上传目录存在
    ensure_upload_dir()
    
    # 生成唯一文件名
    filename = generate_unique_filename(file.filename)
    file_path = UPLOAD_DIR / "videos" / filename
    
    # 保存文件
    try:
        with open(file_path, "wb") as f:
            f.write(contents)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件保存失败: {str(e)}"
        )
    
    # 返回文件URL
    file_url = f"/uploads/videos/{filename}"
    
    return {
        "url": file_url,
        "filename": filename,
        "original_filename": file.filename,
        "size": len(contents),
        "content_type": file.content_type
    }


@router.delete(
    "/files",
    summary="删除文件",
    description="删除已上传的文件"
)
async def delete_file(
    file_path: str,
    current_farmer: Farmer = Depends(get_current_farmer)
):
    """
    删除文件
    
    Args:
        file_path: 文件路径（相对路径，如 /uploads/images/xxx.jpg）
        current_farmer: 当前登录的农户
    
    Returns:
        删除结果
    """
    # 安全检查：确保路径在uploads目录下
    if not file_path.startswith("/uploads/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的文件路径"
        )
    
    # 构建实际文件路径
    relative_path = file_path.lstrip("/uploads/")
    full_path = UPLOAD_DIR / relative_path
    
    # 检查文件是否存在
    if not full_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    # 删除文件
    try:
        full_path.unlink()
        return {
            "message": "文件删除成功",
            "file_path": file_path
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件删除失败: {str(e)}"
        )

