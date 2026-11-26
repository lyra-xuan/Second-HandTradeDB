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

    async def price_range(self) -> list:
        """D3：在售 + 已预订商品的五档价格区间分布，区间顺序固定。"""
        sql = text("""
            SELECT
              CASE
                WHEN p.`price` <  50   THEN '0-50'
                WHEN p.`price` <  100  THEN '50-100'
                WHEN p.`price` <  300  THEN '100-300'
                WHEN p.`price` <  1000 THEN '300-1000'
                ELSE '1000以上'
              END AS price_range,
              COUNT(*) AS product_count
            FROM `products` p
            WHERE p.`status` IN (1, 2)
            GROUP BY price_range
            ORDER BY FIELD(price_range, '0-50', '50-100', '100-300', '300-1000', '1000以上')
        """)
        return list((await self.session.execute(sql)).mappings().all())

    async def trend(self, days: int) -> list:
        """D4：近 N 天发布与成交趋势，用递归生成完整日历，无数据的日期补 0。"""
        sql = text("""
            WITH RECURSIVE days(day) AS (
              SELECT DATE_SUB(CURDATE(), INTERVAL :days_back DAY)
              UNION ALL
              SELECT `day` + INTERVAL 1 DAY FROM days WHERE `day` < CURDATE()
            )
            SELECT
              DATE_FORMAT(d.`day`, '%m-%d') AS stat_date,
              IFNULL(np.`cnt`, 0)           AS new_products,
              IFNULL(fo.`cnt`, 0)           AS finished_orders
            FROM days d
            LEFT JOIN (
              SELECT DATE(`created_at`) AS d, COUNT(*) AS cnt
              FROM `products` GROUP BY DATE(`created_at`)
            ) np ON np.d = d.`day`
            LEFT JOIN (
              SELECT DATE(`finished_at`) AS d, COUNT(*) AS cnt
              FROM `orders`
              WHERE `status` = 3 AND `finished_at` IS NOT NULL
              GROUP BY DATE(`finished_at`)
            ) fo ON fo.d = d.`day`
            ORDER BY d.`day`
        """)
        return list((await self.session.execute(sql, {'days_back': days - 1})).mappings().all())

    async def ranking(self, limit: int) -> list:
        """D5：热门商品 Top N，按浏览量为主、收藏量为辅排序，只统计未下架商品。"""
        sql = text("""
            SELECT
              p.`id`    AS product_id,
              p.`title` AS title,
              p.`price` AS price,
              p.`view_count` AS view_count,
              (SELECT COUNT(*) FROM `favorites` f
                WHERE f.`product_id` = p.`id`) AS favorite_count
            FROM `products` p
            WHERE p.`status` IN (1, 2)
            ORDER BY p.`view_count` DESC, favorite_count DESC
            LIMIT :limit
        """)
        return list((await self.session.execute(sql, {'limit': limit})).mappings().all())

    async def top_sellers(self, limit: int) -> list:
        """加分项 1：活跃卖家排行，按在售商品数为主、累计浏览量为辅排序。"""
        sql = text("""
            SELECT
              u.`id`       AS seller_id,
              u.`nickname` AS nickname,
              COUNT(DISTINCT CASE WHEN p.`status` = 1 THEN p.`id` END) AS on_sale_count,
              IFNULL(SUM(p.`view_count`), 0)                            AS total_views,
              (SELECT COUNT(*) FROM `orders` o
                WHERE o.`seller_id` = u.`id` AND o.`status` = 3)         AS finished_orders
            FROM `users` u
            LEFT JOIN `products` p ON p.`seller_id` = u.`id`
            GROUP BY u.`id`, u.`nickname`
            HAVING on_sale_count > 0
            ORDER BY on_sale_count DESC, total_views DESC
            LIMIT :limit
        """)
        return list((await self.session.execute(sql, {'limit': limit})).mappings().all())

    async def category_sales(self) -> list:
        """加分项 2：各分类成交金额与平均成交价，只统计已完成订单。"""
        sql = text("""
            SELECT
              c.`name` AS category_name,
              COUNT(o.`id`)                      AS deal_count,
              IFNULL(SUM(p.`price`), 0)          AS total_amount,
              IFNULL(ROUND(AVG(p.`price`), 2), 0) AS avg_price
            FROM `orders` o
            JOIN `products`    p ON p.`id` = o.`product_id`
            JOIN `categories`  c ON c.`id` = p.`category_id`
            WHERE o.`status` = 3
            GROUP BY c.`id`, c.`name`
            ORDER BY total_amount DESC
        """)
        return list((await self.session.execute(sql)).mappings().all())
