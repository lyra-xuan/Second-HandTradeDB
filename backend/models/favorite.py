from datetime import datetime

from . import Base
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Integer, DateTime, ForeignKey, UniqueConstraint, Index, func


class Favorite(Base):
    """用户收藏表；同一用户对同一商品仅一条记录。"""
    __tablename__ = 'favorites'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id', ondelete='CASCADE'))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    __table_args__ = (
        UniqueConstraint('user_id', 'product_id', name='uk_fav_user_product'),
        Index('idx_favorites_product', 'product_id'),
    )
