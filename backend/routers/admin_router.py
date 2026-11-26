from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from dependencies import get_session, get_admin_user
from models import AsyncSession
from models.user import User
from repository.admin_repo import AdminRepository
from schemas import ResponseOut
from schemas.admin import UserStatusIn, AdminLogListOut, AdminLogItem

router = APIRouter(prefix='/admin', tags=['管理员'])


@router.patch('/users/{user_id}/status', response_model=ResponseOut)
async def update_user_status(
    user_id: int,
    data: UserStatusIn,
    admin: Annotated[User, Depends(get_admin_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """管理员封禁(0)/解封(1)用户；审计日志由数据库触发器 trg_users_au_log 自动写入。"""
    repo = AdminRepository(session=session)
    user = await repo.get_user(user_id)
    if user is None:
        raise HTTPException(404, detail="用户不存在！")
    if user.id == admin.id:
        raise HTTPException(400, detail="不能修改自己的账号状态！")
    if user.status == data.status:
        raise HTTPException(400, detail="用户已处于该状态！")
    await repo.update_user_status(user, data.status)
    return ResponseOut()


@router.get('/logs', response_model=AdminLogListOut)
async def list_logs(
    page: int = Query(default=1, gt=0),
    page_size: int = Query(default=20, gt=0, le=100),
    admin: Annotated[User, Depends(get_admin_user)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
):
    """管理员操作日志：含触发器自动审计记录，按时间倒序分页。"""
    total, rows = await AdminRepository(session=session).list_logs(page=page, page_size=page_size)
    return AdminLogListOut(
        total=total, page=page, page_size=page_size,
        items=[AdminLogItem.model_validate(row) for row in rows],
    )
