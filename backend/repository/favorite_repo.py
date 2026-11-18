from sqlalchemy import select

from models import AsyncSession
from models.favorite import Favorite
from models.product import Product
from models.category import Category
from models.condition_level import ConditionLevel
from models.product_image import ProductImage


class FavoriteRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def is_exist(self, user_id: int, product_id: int) -> bool:
        return bool(await self.session.scalar(
            select(Favorite.id).where(
                Favorite.user_id == user_id, Favorite.product_id == product_id
            ).limit(1)
        ))

    async def add(self, user_id: int, product_id: int) -> None:
        self.session.add(Favorite(user_id=user_id, product_id=product_id))
        await self.session.flush()

    async def remove(self, user_id: int, product_id: int) -> None:
        favorite = await self.session.scalar(
            select(Favorite).where(
                Favorite.user_id == user_id, Favorite.product_id == product_id
            )
        )
        if favorite is not None:
            await self.session.delete(favorite)
            await self.session.flush()

    async def list_rows(self, user_id: int) -> list:
        cover = (select(ProductImage.url)
                 .where(ProductImage.product_id == Product.id)
                 .order_by(ProductImage.sort_order)
                 .limit(1)
                 .scalar_subquery())
        return (await self.session.execute(
            select(
                Product.id, Product.title, Product.price, Product.status,
                Product.view_count, Product.created_at,
                Category.name.label('category_name'),
                ConditionLevel.name.label('condition_name'),
                cover.label('cover_image'),
                Favorite.created_at.label('favorited_at'),
            )
            .join(Product, Favorite.product_id == Product.id)
            .join(Category, Product.category_id == Category.id)
            .join(ConditionLevel, Product.condition_id == ConditionLevel.id)
            .where(Favorite.user_id == user_id)
            .order_by(Favorite.created_at.desc())
        )).all()
