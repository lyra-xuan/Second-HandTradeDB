from sqlalchemy import select, func, and_, text

from models import AsyncSession
from models.category import Category
from models.product import Product


class StatsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def overview(self):
        """D1：与 stats_queries.sql 中 D1 的 SELECT 保持同字段同口径。"""
        sql = text("""
            SELECT
              (SELECT COUNT(*) FROM `users` WHERE `status` = 1)                AS user_count,
              (SELECT COUNT(*) FROM `products`)                                AS product_total,
              (SELECT COUNT(*) FROM `products` WHERE `status` = 1)             AS product_on_sale,
              (SELECT COUNT(*) FROM `orders` WHERE `status` = 3)               AS order_finished,
              (SELECT IFNULL(SUM(p.`price`), 0)
                 FROM `orders` o JOIN `products` p ON o.`product_id` = p.`id`
                 WHERE o.`status` = 3)                                         AS trade_amount,
              (SELECT IFNULL(CONCAT(ROUND(100 * SUM(`status` = 3) / COUNT(*), 1), '%'), '0%')
                 FROM `orders`)                                                AS finish_rate
        """)
        return (await self.session.execute(sql)).mappings().one()

    async def category_distribution(self) -> list:
        """D2：各分类在售商品数，含空分类。"""
        stmt = (select(
            Category.id.label('category_id'),
            Category.name.label('category_name'),
            func.count(Product.id).label('on_sale_count'),
        )
            .outerjoin(Product, and_(Product.category_id == Category.id, Product.status == 1))
            .group_by(Category.id, Category.name)
            .order_by(Category.sort_order))
        return list((await self.session.execute(stmt)).mappings().all())
