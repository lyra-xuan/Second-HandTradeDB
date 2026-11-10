from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated
from dependencies import get_session
from models import AsyncSession
from repository.user_repo import UserRepository, User
from schemas import ResponseOut
from schemas.user import UserCreateSchema, RegisterIn, LoginIn, LoginOut, UserSchema
from core.auth import AuthHandler

router = APIRouter(prefix="/auth")

auth_handler = AuthHandler()

@router.post(path="/register", response_model=ResponseOut)
async def register(
    data: RegisterIn,
    session: AsyncSession = Depends(get_session),
):
    user_repo = UserRepository(session=session)
    # 1. 判断学号是否已注册
    student_no_exist = await user_repo.student_no_is_exist(student_no=data.student_no)
    if student_no_exist:
        raise HTTPException(status_code=400, detail="该学号已经注册！")

    # 2. 判断邮箱是否已被占用
    email_exist = await user_repo.email_is_exist(email=str(data.email))
    if email_exist:
        raise HTTPException(status_code=400, detail="该邮箱已经存在！")

    try:
        await user_repo.create(UserCreateSchema(
            student_no=data.student_no,
            email=str(data.email),
            nickname=data.nickname,
            password=data.password
        ))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return ResponseOut()

@router.post('/login', response_model=LoginOut)
async def login(
    data: LoginIn,
    session: AsyncSession = Depends(get_session),
):
    # 1. 创建user_repo对象
    user_repo = UserRepository(session=session)
    # 2. 根据学号查找用户
    user: User|None = await user_repo.get_by_student_no(data.student_no)
    if not user:
        raise HTTPException(400, detail="该用户不存在！")
    if not user.check_password(data.password):
        raise HTTPException(400, detail="学号或密码错误！")
    if user.status == 0:
        raise HTTPException(400, detail="该账号已被封禁！")
    # 3. 生成JWToken
    token = auth_handler.encode_access_token(user.id)
    return {
        "user": user,
        "token": token
    }

@router.get('/me', response_model=UserSchema)
async def get_me(
    user_id: Annotated[int, Depends(auth_handler.auth_access_dependency)],
    session: AsyncSession = Depends(get_session),
):
    user: User|None = await UserRepository(session=session).get_by_id(user_id)
    if not user:
        raise HTTPException(404, detail="用户不存在！")
    return user
