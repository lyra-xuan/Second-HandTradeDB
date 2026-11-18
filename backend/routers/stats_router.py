from typing import Annotated

from fastapi import APIRouter, Depends

from dependencies import get_session, get_current_user
from models import AsyncSession
from models.user import User
from repository.stats_repo import StatsRepository
from schemas.stats import OverviewOut, CategoryStatsOut

router = APIRouter(prefix='/stats', tags=['统计'])


@router.get('/overview', response_model=OverviewOut)
async def overview(
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """D1 平台概览：用户数 / 商品总数 / 在售数 / 成交量 / 成交额 / 成交率。"""
    row = await StatsRepository(session=session).overview()
    return OverviewOut(**dict(row))


@router.get('/categories', response_model=CategoryStatsOut)
async def category_distribution(
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """D2 分类分布：各分类在售商品数量（含空分类）。"""
    rows = await StatsRepository(session=session).category_distribution()
    return CategoryStatsOut(items=[dict(row) for row in rows])
