from typing import Annotated

from fastapi import Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from core.auth import AuthHandler
from models.user import User
from repository.user_repo import UserRepository


async def get_session(request: Request) -> AsyncSession:
    """取本次请求的 Session。

    事务边界由 DBSessionMiddleware 管理：在响应发出前提交，异常时回滚。
    这样前端创建/下单后立即查询能读到最新状态，Repository 仍不自行提交。
    """
    return request.state.db_session


auth_handler = AuthHandler()


async def get_current_user(
    user_id: Annotated[int, Depends(auth_handler.auth_access_dependency)],
    session: AsyncSession = Depends(get_session),
) -> User:
    """所有业务接口的统一登录依赖，返回当前用户 ORM 对象。"""
    user = await UserRepository(session=session).get_by_id(user_id)
    if not user:
        raise HTTPException(404, detail="用户不存在！")
    if user.status == 0:
        raise HTTPException(403, detail="该账号已被封禁！")
    return user


async def get_admin_user(
    user: Annotated[User, Depends(get_current_user)],
) -> User:
    """管理员接口依赖。"""
    if not user.is_admin:
        raise HTTPException(403, detail="需要管理员权限！")
    return user
