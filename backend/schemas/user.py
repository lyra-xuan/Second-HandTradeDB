from pydantic import BaseModel, Field, EmailStr, model_validator
from typing import Annotated

StudentNoStr = Annotated[str, Field(..., min_length=4, max_length=20, description="学号")]
NicknameStr = Annotated[str, Field(..., min_length=1, max_length=20, description="昵称")]
RawPasswordStr = Annotated[str, Field(min_length=6, max_length=20, description="密码")]

class RegisterIn(BaseModel):
    student_no: StudentNoStr
    email: EmailStr
    nickname: NicknameStr
    password: RawPasswordStr
    confirm_password: RawPasswordStr

    @model_validator(mode="after")
    def password_is_match(self) -> "RegisterIn":
        password = self.password
        confirm_password = self.confirm_password
        if password != confirm_password:
            raise ValueError("密码不一致！")
        return self

class UserCreateSchema(BaseModel):
        student_no: StudentNoStr
        email: EmailStr
        nickname: NicknameStr
        password: RawPasswordStr

class LoginIn(BaseModel):
    student_no: StudentNoStr
    password: RawPasswordStr

class UserSchema(BaseModel):
    id: Annotated[int, Field(...)]
    student_no: StudentNoStr
    email: EmailStr
    nickname: NicknameStr
    avatar: str | None = None
    contact: str | None = None
    is_admin: bool

class UserUpdateIn(BaseModel):
    """个人资料修改：只开放昵称/头像/联系方式。

    学号、邮箱、密码不在此接口修改；显式传 null 代表清空头像/联系方式。
    """
    nickname: str | None = Field(default=None, min_length=1, max_length=20, description="昵称")
    avatar: str | None = Field(default=None, max_length=255, description="头像 URL")
    contact: str | None = Field(default=None, max_length=100, description="联系方式")

    @model_validator(mode="after")
    def at_least_one_field(self) -> "UserUpdateIn":
        if not self.model_fields_set:
            raise ValueError("至少提供一个待修改字段！")
        return self

class LoginOut(BaseModel):
    user: UserSchema
    token: str
