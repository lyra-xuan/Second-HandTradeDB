from datetime import datetime

from . import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Integer, String, DateTime, ForeignKey, func


class ProductImage(Base):
    """商品图片表；商品删除时由数据库外键 ON DELETE CASCADE 级联清理。"""
    __tablename__ = 'product_images'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id', ondelete='CASCADE'))
    url: Mapped[str] = mapped_column(String(255))
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default='0')
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    product: Mapped["Product"] = relationship(back_populates="images")


from .product import Product  # noqa: E402  # 供 relationship 字符串解析使用
