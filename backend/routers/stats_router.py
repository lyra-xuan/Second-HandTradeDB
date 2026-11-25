from typing import Annotated

from fastapi import APIRouter, Depends, Query

from dependencies import get_session, get_current_user
from models import AsyncSession
from models.user import User
from repository.stats_repo import StatsRepository
from schemas.stats import (
    OverviewOut, CategoryStatsOut,
    PriceRangeOut, TrendOut, RankingOut, SellerRankOut, CategorySalesOut,
)

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


@router.get('/price-range', response_model=PriceRangeOut)
async def price_range(
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """D3 价格区间分布：在售 + 已预订商品的五档区间数量（柱状图）。"""
    rows = await StatsRepository(session=session).price_range()
    return PriceRangeOut(items=[dict(row) for row in rows])


@router.get('/trend', response_model=TrendOut)
async def trend(
    days: int = Query(default=30, ge=1, le=90, description='统计最近多少天'),
    user: Annotated[User, Depends(get_current_user)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
):
    """D4 发布与成交趋势：近 N 天每日新增商品数与成交订单数，无数据日期补 0（折线图）。"""
    rows = await StatsRepository(session=session).trend(days=days)
    return TrendOut(days=days, items=[dict(row) for row in rows])


@router.get('/ranking', response_model=RankingOut)
async def ranking(
    limit: int = Query(default=10, gt=0, le=50, description='返回条数'),
    user: Annotated[User, Depends(get_current_user)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
):
    """D5 热门商品排行：按浏览量为主、收藏量为辅排序（只含未下架商品）。"""
    rows = await StatsRepository(session=session).ranking(limit=limit)
    return RankingOut(items=[dict(row) for row in rows])


@router.get('/sellers', response_model=SellerRankOut)
async def top_sellers(
    limit: int = Query(default=5, gt=0, le=20, description='返回条数'),
    user: Annotated[User, Depends(get_current_user)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
):
    """加分项 1 活跃卖家排行：在售商品数 + 累计浏览量 + 历史成交量。"""
    rows = await StatsRepository(session=session).top_sellers(limit=limit)
    return SellerRankOut(items=[dict(row) for row in rows])


@router.get('/category-sales', response_model=CategorySalesOut)
async def category_sales(
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """加分项 2 分类成交分析：各分类成交笔数、成交金额与平均成交价。"""
    rows = await StatsRepository(session=session).category_sales()
    return CategorySalesOut(items=[dict(row) for row in rows])
