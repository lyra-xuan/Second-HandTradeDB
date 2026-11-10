from . import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Integer, String, DateTime, Boolean
from pwdlib import PasswordHash #加密
from datetime import datetime

password_hash = PasswordHash.recommended()


class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_no: Mapped[str] = mapped_column(String(20), unique=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    nickname: Mapped[str] = mapped_column(String(50))
    avatar: Mapped[str | None] = mapped_column(String(255), default=None)
    contact: Mapped[str | None] = mapped_column(String(100), default=None)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[int] = mapped_column(Integer, default=1)  # 1 正常，0 已封禁
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    _password: Mapped[str] = mapped_column(String(200))

    def __init__(self, *args, **kwargs):
        password = kwargs.get("password")
        if password:
            password = kwargs.pop("password")
        super().__init__(*args, **kwargs)
        self.password = password

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = password_hash.hash(password)

    def check_password(self, raw_password):
        return password_hash.verify(raw_password, self.password)
