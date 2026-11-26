from sqlalchemy import select, func

from models import AsyncSession
from models.user import User
from models.admin_log import AdminLog


class AdminRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user(self, user_id: int) -> User | None:
        return await self.session.scalar(select(User).filter(User.id == user_id))

    async def update_user_status(self, user: User, status: int) -> User:
        """封禁/解封：只改 status，审计日志由 trg_users_au_log 触发器自动写入。"""
        user.status = status
        await self.session.flush()
        return user

    async def list_logs(self, page: int, page_size: int) -> tuple[int, list]:
        """管理员操作日志，按时间倒序分页。"""
        total = await self.session.scalar(select(func.count()).select_from(AdminLog))
        rows = (await self.session.execute(
            select(AdminLog)
            .order_by(AdminLog.created_at.desc(), AdminLog.id.desc())
            .offset((page - 1) * page_size).limit(page_size)
        )).scalars().all()
        return total or 0, list(rows)
