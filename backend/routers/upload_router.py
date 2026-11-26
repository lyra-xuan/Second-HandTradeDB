import uuid
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from dependencies import get_current_user
from models.user import User
from schemas.upload import UploadOut

router = APIRouter(tags=['图片上传'])

# 保存在 backend/static/uploads 下，通过 main.py 挂载的 /static 访问
UPLOAD_DIR = Path(__file__).resolve().parent.parent / 'static' / 'uploads'
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

URL_PREFIX = '/static/uploads'
# 允许的 MIME 类型 -> 落盘后缀
ALLOWED_TYPES = {
    'image/jpeg': '.jpg',
    'image/png': '.png',
    'image/webp': '.webp',
    'image/gif': '.gif',
}
MAX_FILES = 9
MAX_SIZE = 5 * 1024 * 1024  # 单张 5MB


@router.post('/uploads', response_model=UploadOut, status_code=201)
async def upload_images(
    user: Annotated[User, Depends(get_current_user)],
    files: Annotated[list[UploadFile], File(description='待上传的图片，最多 9 张')],
):
    """发布商品前上传图片：校验格式与大小后落盘，返回可访问的 URL 列表。

    前端拿到 urls 后填入 ProductCreateIn.images 即可。
    """
    if not files:
        raise HTTPException(400, detail="请选择要上传的图片！")
    if len(files) > MAX_FILES:
        raise HTTPException(400, detail=f"一次最多上传 {MAX_FILES} 张图片！")

    # 先全部读取并校验，避免校验中途失败时磁盘残留部分文件
    pending: list[tuple[str, bytes]] = []
    for file in files:
        ext = ALLOWED_TYPES.get(file.content_type)
        if ext is None:
            raise HTTPException(
                400,
                detail=f"不支持的图片格式：{file.filename or file.content_type}，仅支持 jpg/png/webp/gif！",
            )
        content = await file.read()
        if not content:
            raise HTTPException(400, detail=f"图片 {file.filename} 内容为空！")
        if len(content) > MAX_SIZE:
            raise HTTPException(
                400, detail=f"图片 {file.filename} 超过 {MAX_SIZE // (1024 * 1024)}MB 限制！"
            )
        pending.append((uuid.uuid4().hex + ext, content))

    urls = []
    for name, content in pending:
        (UPLOAD_DIR / name).write_bytes(content)
        urls.append(f"{URL_PREFIX}/{name}")
    return UploadOut(urls=urls)
