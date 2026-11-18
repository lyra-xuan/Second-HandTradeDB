from sqlalchemy import select, func, or_

from models import AsyncSession
from models.product import Product
from models.product_image import ProductImage
from models.category import Category
from models.condition_level import ConditionLevel
from models.trade_place import TradePlace
from schemas.product import ProductCreateIn, ProductUpdateIn


class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, product_id: int) -> Product | None:
        return await self.session.scalar(select(Product).filter(Product.id == product_id))

    @staticmethod
    def _escape_keyword(keyword: str) -> str:
        """转义 LIKE 通配符，避免用户输入的 % / _ 改变检索语义。"""
        return keyword.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')

    def _build_list_stmt(self, category_id: int | None, keyword: str | None,
                         only_on_sale: bool, seller_id: int | None = None):
        cover = (select(ProductImage.url)
                 .where(ProductImage.product_id == Product.id)
                 .order_by(ProductImage.sort_order)
                 .limit(1)
                 .scalar_subquery())
        stmt = (select(
            Product.id, Product.title, Product.price, Product.status,
            Product.view_count, Product.created_at,
            Category.name.label('category_name'),
            ConditionLevel.name.label('condition_name'),
            TradePlace.name.label('place_name'),
            cover.label('cover_image'),
        )
            .join(Category, Product.category_id == Category.id)
            .join(ConditionLevel, Product.condition_id == ConditionLevel.id)
            .outerjoin(TradePlace, Product.place_id == TradePlace.id))
        if only_on_sale:
            stmt = stmt.where(Product.status == 1)
        if seller_id is not None:
            stmt = stmt.where(Product.seller_id == seller_id)
        if category_id is not None:
            stmt = stmt.where(Product.category_id == category_id)
        if keyword:
            pattern = f'%{self._escape_keyword(keyword)}%'
            stmt = stmt.where(or_(
                Product.title.like(pattern, escape='\\'),
                Product.description.like(pattern, escape='\\'),
            ))
        return stmt

    async def list_products(
        self,
        category_id: int | None = None,
        keyword: str | None = None,
        page: int = 1,
        page_size: int = 12,
        only_on_sale: bool = True,
        seller_id: int | None = None,
    ) -> tuple[int, list]:
        stmt = self._build_list_stmt(category_id, keyword, only_on_sale, seller_id)
        total = await self.session.scalar(
            select(func.count()).select_from(stmt.order_by(None).subquery())
        )
        rows = (await self.session.execute(
            stmt.order_by(Product.created_at.desc(), Product.id.desc())
                .offset((page - 1) * page_size).limit(page_size)
        )).all()
        return total or 0, rows

    async def create(self, seller_id: int, data: ProductCreateIn) -> Product:
        product = Product(
            seller_id=seller_id,
            title=data.title,
            description=data.description,
            price=data.price,
            category_id=data.category_id,
            condition_id=data.condition_id,
            place_id=data.place_id,
            images=[ProductImage(url=url, sort_order=i) for i, url in enumerate(data.images)],
        )
        self.session.add(product)
        await self.session.flush()
        return product

    async def update(self, product: Product, data: ProductUpdateIn) -> Product:
        payload = data.model_dump(exclude_unset=True)
        images = payload.pop('images', None)
        for key, value in payload.items():
            setattr(product, key, value)
        if images is not None:
            product.images.clear()
            product.images.extend(
                ProductImage(url=url, sort_order=i) for i, url in enumerate(images)
            )
        await self.session.flush()
        return product

    async def delist(self, product: Product) -> None:
        """发布者/管理员下架：只写 status=4，绝不碰触发器管理的 1/2/3。"""
        product.status = 4
        await self.session.flush()

    async def reshelf(self, product: Product) -> None:
        """管理员重新上架：只做 4→1，不碰 2/3。"""
        product.status = 1
        await self.session.flush()

    async def add_view(self, product: Product) -> None:
        product.view_count += 1
        await self.session.flush()

    async def get_images(self, product_id: int) -> list[str]:
        rows = (await self.session.execute(
            select(ProductImage.url)
            .where(ProductImage.product_id == product_id)
            .order_by(ProductImage.sort_order)
        )).scalars().all()
        return list(rows)

    async def is_favorite(self, user_id: int, product_id: int) -> bool:
        from models.favorite import Favorite
        return bool(await self.session.scalar(
            select(Favorite.id).where(
                Favorite.user_id == user_id, Favorite.product_id == product_id
            ).limit(1)
        ))
