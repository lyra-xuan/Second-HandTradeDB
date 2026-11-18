from datetime import datetime

from . import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Integer, String, DateTime, SmallInteger, ForeignKey, CheckConstraint, Index, func


class Order(Base):
    """订单表。

    status：1 待确认 / 2 已确认 / 3 已完成 / 4 已取消。
    应用层只 INSERT 订单、UPDATE 订单状态；
    商品状态 1/2/3 完全由数据库触发器联动，不要在这里手动改。
    """
    __tablename__ = 'orders'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    buyer_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    seller_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    place_id: Mapped[int | None] = mapped_column(ForeignKey('trade_places.id'), default=None)
    contact: Mapped[str | None] = mapped_column(String(100), default=None)
    status: Mapped[int] = mapped_column(SmallInteger, default=1, server_default='1')
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, default=None)

    __table_args__ = (
        CheckConstraint('status IN (1, 2, 3, 4)', name='chk_orders_status'),
        CheckConstraint('buyer_id <> seller_id', name='chk_orders_not_self'),
        Index('idx_orders_buyer', 'buyer_id', 'status'),
        Index('idx_orders_seller', 'seller_id', 'status'),
        Index('idx_orders_product', 'product_id', 'status'),
        Index('idx_orders_created', 'created_at'),
    )
