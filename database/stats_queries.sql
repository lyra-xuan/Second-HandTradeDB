-- ============================================================
--  校园二手交易平台 - 统计分析查询（stats_queries.sql）
--  对应需求分析 3.4 节 D1~D5，外加 P2 加分项两则
--
--  使用方式：
--    1. 直接在 MySQL 客户端 / Navicat 中逐段执行，验证结果
--    2. 后端统计接口（/api/stats/...）可直接把对应 SELECT
--       翻译成 SQLAlchemy 查询或 aiomysql execute
--    3. 前端图表（饼图/柱状图/折线图）按下述字段渲染
--
--  约定：列名使用英文别名，便于后端序列化为 JSON
-- ============================================================

USE `second_hand_trade`;

-- ------------------------------------------------------------
-- D1 平台概览指标（指标卡）
--    用户数 / 商品总数 / 在售数 / 累计成交量 / 累计成交额 / 成交率
-- ------------------------------------------------------------
SELECT
  (SELECT COUNT(*) FROM `users` WHERE `status` = 1)                AS user_count,
  (SELECT COUNT(*) FROM `products`)                                 AS product_total,
  (SELECT COUNT(*) FROM `products` WHERE `status` = 1)              AS product_on_sale,
  (SELECT COUNT(*) FROM `orders` WHERE `status` = 3)                AS order_finished,
  (SELECT IFNULL(SUM(p.`price`), 0)
     FROM `orders` o JOIN `products` p ON o.`product_id` = p.`id`
     WHERE o.`status` = 3)                                          AS trade_amount,
  (SELECT CONCAT(ROUND(100 * SUM(`status` = 3) / COUNT(*), 1), '%')
     FROM `orders`)                                                 AS finish_rate;

-- ------------------------------------------------------------
-- D2 分类分布（饼图 / 柱状图）
--    各分类在售商品数量，含空分类（LEFT JOIN 保证图例完整）
-- ------------------------------------------------------------
SELECT
  c.`id`   AS category_id,
  c.`name` AS category_name,
  COUNT(p.`id`) AS on_sale_count
FROM `categories` c
LEFT JOIN `products` p
  ON p.`category_id` = c.`id` AND p.`status` = 1
GROUP BY c.`id`, c.`name`
ORDER BY c.`sort_order`;

-- ------------------------------------------------------------
-- D3 价格区间分布（柱状图）
--    统计在售+已预订商品的五档价格区间
-- ------------------------------------------------------------
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
ORDER BY FIELD(price_range, '0-50', '50-100', '100-300', '300-1000', '1000以上');

-- ------------------------------------------------------------
-- D4 近 30 天发布与成交趋势（折线图，双序列）
--    WITH RECURSIVE 生成完整日历，无数据的日期补 0
--    new_products   : 当日新发布商品数
--    finished_orders: 当日成交订单数
-- ------------------------------------------------------------
WITH RECURSIVE days(day) AS (
  SELECT DATE_SUB(CURDATE(), INTERVAL 29 DAY)
  UNION ALL
  SELECT `day` + INTERVAL 1 DAY FROM days WHERE `day` < CURDATE()
)
SELECT
  DATE_FORMAT(d.`day`, '%m-%d')                     AS stat_date,
  IFNULL(np.`cnt`, 0)                               AS new_products,
  IFNULL(fo.`cnt`, 0)                               AS finished_orders
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
ORDER BY d.`day`;

-- ------------------------------------------------------------
-- D5 热门商品 Top 10（排行榜）
--    按浏览量为主、收藏量为辅排序，只统计未下架商品
-- ------------------------------------------------------------
SELECT
  p.`id`    AS product_id,
  p.`title` AS title,
  p.`price` AS price,
  p.`view_count` AS view_count,
  (SELECT COUNT(*) FROM `favorites` f
    WHERE f.`product_id` = p.`id`)                 AS favorite_count
FROM `products` p
WHERE p.`status` IN (1, 2)
ORDER BY p.`view_count` DESC, favorite_count DESC
LIMIT 10;

-- ------------------------------------------------------------
-- 加分项 1：活跃卖家排行 Top 5（体现"数据排名"加工）
--    在售商品数 + 累计浏览量 + 历史成交量
-- ------------------------------------------------------------
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
LIMIT 5;

-- ------------------------------------------------------------
-- 加分项 2：各分类成交金额与平均成交价（体现"聚合分析"加工）
--    只统计已完成订单对应商品
-- ------------------------------------------------------------
SELECT
  c.`name` AS category_name,
  COUNT(o.`id`)                    AS deal_count,
  IFNULL(SUM(p.`price`), 0)        AS total_amount,
  IFNULL(ROUND(AVG(p.`price`), 2), 0) AS avg_price
FROM `orders` o
JOIN `products`    p ON p.`id` = o.`product_id`
JOIN `categories`  c ON c.`id` = p.`category_id`
WHERE o.`status` = 3
GROUP BY c.`id`, c.`name`
ORDER BY total_amount DESC;
