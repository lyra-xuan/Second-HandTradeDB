from models import AsyncSession
from models.user import User
from sqlalchemy import select, exists

from schemas.user import UserCreateSchema, UserUpdateIn

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> User|None:
        return await self.session.scalar(select(User).filter(User.id==user_id))

    async def get_by_student_no(self, student_no: str) -> User|None:
        return await self.session.scalar(select(User).filter(User.student_no==student_no))

    async def student_no_is_exist(self, student_no: str) -> bool:
        stmt = select(exists().where(User.student_no==student_no))
        return await self.session.scalar(stmt)

    async def email_is_exist(self, email: str) -> bool:
        stmt = select(exists().where(User.email==email))
        return await self.session.scalar(stmt)

    async def create(self, user_schema: UserCreateSchema) -> User:
        user = User(**user_schema.model_dump())
        self.session.add(user)
        await self.session.flush()
        return user

    async def update(self, user: User, user_schema: UserUpdateIn) -> User:
        """只更新调用方显式传入的字段，未传字段保持原值。"""
        for field, value in user_schema.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        await self.session.flush()
        return user
