from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException

from dependencies import get_session, get_current_user
from models import AsyncSession
from models.user import User
from repository.order_repo import OrderRepository
from schemas import ResponseOut
from schemas.order import OrderCreateIn, OrderCreateOut, OrderOut

router = APIRouter(prefix='/orders', tags=['订单'])


@router.post('', response_model=OrderCreateOut, status_code=201)
async def create_order(
    data: OrderCreateIn,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """下单：只 INSERT 订单，商品状态由 trg_orders_bi_check / ai_reserve 触发器校验并联动。"""
    repo = OrderRepository(session=session)
    try:
        order = await repo.create(buyer_id=user.id, data=data)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    return OrderCreateOut(id=order.id)


@router.get('', response_model=list[OrderOut])
async def list_orders(
    role: Literal['buyer', 'seller'] = 'buyer',
    user: Annotated[User, Depends(get_current_user)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
):
    """我的订单：role=buyer 买家视角，role=seller 卖家视角。"""
    rows = await OrderRepository(session=session).list_rows(user.id, role)
    return [OrderOut(**row._mapping) for row in rows]


@router.get('/{order_id}', response_model=OrderOut)
async def get_order(
    order_id: int,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    repo = OrderRepository(session=session)
    row = await repo.get_detail_row(order_id)
    if row is None:
        raise HTTPException(404, detail="订单不存在！")
    if user.id not in (row.buyer_id, row.seller_id):
        raise HTTPException(403, detail="无权查看该订单！")
    return OrderOut(**row._mapping)


async def _change_status(order_id: int, user: User, session: AsyncSession, target: int):
    repo = OrderRepository(session=session)
    order = await repo.get_by_id(order_id)
    if order is None:
        raise HTTPException(404, detail="订单不存在！")
    try:
        await repo.update_status(order, new_status=target, actor_id=user.id)
    except ValueError as e:
        raise HTTPException(400, detail=str(e))
    return ResponseOut()


@router.post('/{order_id}/confirm', response_model=ResponseOut)
async def confirm_order(
    order_id: int,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """卖家确认：1 待确认 → 2 已确认（商品保持"已预订"）。"""
    return await _change_status(order_id, user, session, target=2)


@router.post('/{order_id}/complete', response_model=ResponseOut)
async def complete_order(
    order_id: int,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """完成交易：2 已确认 → 3 已完成，触发器自动把商品置"已售出"。"""
    return await _change_status(order_id, user, session, target=3)


@router.post('/{order_id}/cancel', response_model=ResponseOut)
async def cancel_order(
    order_id: int,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """取消订单：1/2 → 4 已取消，触发器自动把商品恢复"在售"。"""
    return await _change_status(order_id, user, session, target=4)
