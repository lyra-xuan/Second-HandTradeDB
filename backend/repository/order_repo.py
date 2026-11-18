from datetime import datetime

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import aliased

from models import AsyncSession
from models.order import Order
from models.product import Product
from models.user import User
from schemas.order import OrderCreateIn


class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _order_select(self):
        buyer = aliased(User)
        seller = aliased(User)
        return select(
            Order.id, Order.product_id,
            Product.title.label('product_title'), Product.price.label('product_price'),
            Order.buyer_id, Order.seller_id,
            buyer.nickname.label('buyer_nickname'), seller.nickname.label('seller_nickname'),
            Order.place_id, Order.contact, Order.status, Order.created_at, Order.finished_at,
        ).join(Product, Order.product_id == Product.id) \
         .join(buyer, Order.buyer_id == buyer.id) \
         .join(seller, Order.seller_id == seller.id)

    async def get_by_id(self, order_id: int) -> Order | None:
        return await self.session.scalar(select(Order).filter(Order.id == order_id))

    async def get_detail_row(self, order_id: int):
        return (await self.session.execute(
            self._order_select().where(Order.id == order_id)
        )).one_or_none()

    async def list_rows(self, user_id: int, role: str) -> list:
        column = Order.buyer_id if role == 'buyer' else Order.seller_id
        return (await self.session.execute(
            self._order_select().where(column == user_id).order_by(Order.created_at.desc())
        )).all()

    async def create(self, buyer_id: int, data: OrderCreateIn) -> Order:
        """只 INSERT 订单；商品状态由 trg_orders_ai_reserve 自动置 2。"""
        product = await self.session.get(Product, data.product_id)
        if product is None:
            raise ValueError('商品不存在！')
        if product.seller_id == buyer_id:
            raise ValueError('不能购买自己发布的商品！')
        if product.status != 1:
            raise ValueError('商品当前不在售，无法下单！')

        order = Order(
            product_id=data.product_id,
            buyer_id=buyer_id,
            seller_id=product.seller_id,
            place_id=data.place_id,
            contact=data.contact,
            status=1,
        )
        self.session.add(order)
        try:
            await self.session.flush()
        except SQLAlchemyError as e:
            # 触发器 SIGNAL SQLSTATE '45000'（并发抢单时兜底）
            message = str(e.orig) if e.orig is not None else str(e)
            if '下单失败' in message or '45000' in message or '1644' in message:
                raise ValueError('商品当前不在售，无法下单！') from e
            raise
        return order

    async def update_status(self, order: Order, new_status: int, actor_id: int) -> None:
        """只改订单状态；商品 1/2/3 由 trg_orders_au_sync 联动，绝不手动改。"""
        old_status = order.status
        if new_status not in (2, 3, 4):
            raise ValueError('不支持的订单状态！')
        if new_status == 2:
            if old_status != 1:
                raise ValueError('只有待确认订单可以确认！')
            if actor_id != order.seller_id:
                raise ValueError('只有卖家可以确认订单！')
        elif new_status == 3:
            if old_status != 2:
                raise ValueError('只有已确认订单可以完成！')
            if actor_id not in (order.buyer_id, order.seller_id):
                raise ValueError('无权操作该订单！')
        else:  # new_status == 4
            if old_status not in (1, 2):
                raise ValueError('该订单已结束，无法取消！')
            if actor_id not in (order.buyer_id, order.seller_id):
                raise ValueError('无权操作该订单！')

        order.status = new_status
        if new_status in (3, 4):
            order.finished_at = datetime.now()
        await self.session.flush()
