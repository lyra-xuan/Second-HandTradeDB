from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select

from dependencies import get_session, get_current_user
from models import AsyncSession
from models.user import User
from models.category import Category
from models.condition_level import ConditionLevel
from models.trade_place import TradePlace
from schemas.dict import DictItem

router = APIRouter(tags=['字典'])


async def _list_dict(session: AsyncSession, model) -> list[DictItem]:
    rows = (await session.execute(
        select(model.id, model.name, model.sort_order)
        .order_by(model.sort_order, model.id)
    )).all()
    return [DictItem(**row._mapping) for row in rows]


@router.get('/categories', response_model=list[DictItem])
async def list_categories(
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """分类字典：供前端列表筛选与发布表单使用。"""
    return await _list_dict(session, Category)


@router.get('/conditions', response_model=list[DictItem])
async def list_conditions(
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """成色字典。"""
    return await _list_dict(session, ConditionLevel)


@router.get('/places', response_model=list[DictItem])
async def list_places(
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """交易地点字典。"""
    return await _list_dict(session, TradePlace)
