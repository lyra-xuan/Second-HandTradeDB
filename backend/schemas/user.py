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

class LoginOut(BaseModel):
    user: UserSchema
    token: str
