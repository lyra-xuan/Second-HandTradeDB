from typing import TYPE_CHECKING
from decimal import Decimal
from datetime import datetime

from . import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Integer, String, Text, DateTime, Numeric, SmallInteger, ForeignKey, CheckConstraint, Index, func

if TYPE_CHECKING:
    from .user import User
    from .category import Category
    from .condition_level import ConditionLevel
    from .trade_place import TradePlace
    from .product_image import ProductImage


class Product(Base):
    """二手商品表。

    status：1 在售 / 2 已预订 / 3 已售出 / 4 已下架。
    1/2/3 由数据库触发器随订单自动流转，应用层不得手动改；
    只有 4（下架）与 4→1（重新上架）由后端直接 UPDATE。
    """
    __tablename__ = 'products'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    seller_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id'))
    condition_id: Mapped[int] = mapped_column(ForeignKey('condition_levels.id'))
    place_id: Mapped[int | None] = mapped_column(ForeignKey('trade_places.id'), default=None)
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text, default=None)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    status: Mapped[int] = mapped_column(SmallInteger, default=1, server_default='1')
    view_count: Mapped[int] = mapped_column(Integer, default=0, server_default='0')
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    seller: Mapped["User"] = relationship()
    category: Mapped["Category"] = relationship()
    condition_level: Mapped["ConditionLevel"] = relationship()
    place: Mapped["TradePlace"] = relationship()
    images: Mapped[list["ProductImage"]] = relationship(
        back_populates="product", cascade="all, delete-orphan", lazy="selectin"
    )

    __table_args__ = (
        CheckConstraint('price > 0 AND price <= 99999.99', name='chk_products_price'),
        CheckConstraint('status IN (1, 2, 3, 4)', name='chk_products_status'),
        Index('idx_products_category', 'category_id'),
        Index('idx_products_seller', 'seller_id'),
        Index('idx_products_list', 'status', 'created_at'),
    )
