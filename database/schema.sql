-- ============================================================
--  校园二手交易平台 - 数据库建表脚本（schema.sql）
--  适用版本：MySQL 8.0+（utf8mb4_0900_ai_ci）
--  执行顺序：schema.sql  →  triggers.sql  →  seed_data.sql
--
--  表清单（共 9 张，满足"8 张表以上"要求）：
--    基础实体表：users（用户）、products（商品）
--    字典表    ：categories（商品分类）、condition_levels（成色）、
--                trade_places（交易地点）
--    联系表    ：product_images（商品图片）、favorites（收藏）、
--                orders（订单）
--    辅助表    ：admin_logs（管理员操作日志）
--
--  说明：
--    1. users 表与后端 SQLAlchemy 模型（models/user.py）保持一致，勿改列名
--    2. 商品状态、订单状态由触发器自动维护（见 triggers.sql）
--    3. 所有外键列与父表列类型统一为 INT，保证 FK 可建立
-- ============================================================

CREATE DATABASE IF NOT EXISTS `second_hand_trade`
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_0900_ai_ci;

USE `second_hand_trade`;

SET FOREIGN_KEY_CHECKS = 1;

-- ------------------------------------------------------------
-- 1. 用户表 users（基础实体表，与后端 User 模型一致）
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `student_no` VARCHAR(20) NOT NULL COMMENT '学号',
  `email` VARCHAR(100) NOT NULL COMMENT '邮箱',
  `nickname` VARCHAR(50) NOT NULL COMMENT '昵称',
  `avatar` VARCHAR(255) DEFAULT NULL COMMENT '头像地址',
  `contact` VARCHAR(100) DEFAULT NULL COMMENT '联系方式（微信/QQ/手机）',
  `is_admin` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '1 管理员, 0 普通用户',
  `status` INT NOT NULL DEFAULT 1 COMMENT '1 正常, 0 已封禁',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
  `_password` VARCHAR(200) NOT NULL COMMENT '密码哈希（pwdlib/Argon2）',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_users_student_no` (`student_no`),
  UNIQUE KEY `uk_users_email` (`email`),
  CONSTRAINT `chk_users_status` CHECK (`status` IN (0, 1)),
  CONSTRAINT `chk_users_is_admin` CHECK (`is_admin` IN (0, 1))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
  COMMENT='平台用户表';

-- ------------------------------------------------------------
-- 2. 商品分类表 categories（字典表，数据预置）
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `categories` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(30) NOT NULL COMMENT '分类名称',
  `sort_order` INT NOT NULL DEFAULT 0 COMMENT '展示排序，越小越靠前',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_categories_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
  COMMENT='商品分类字典表';

-- ------------------------------------------------------------
-- 3. 成色表 condition_levels（字典表）
--    注：表名带 levels，避开 MySQL 保留字 condition
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `condition_levels` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(30) NOT NULL COMMENT '成色名称，如 九成新',
  `sort_order` INT NOT NULL DEFAULT 0 COMMENT '展示排序',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_condition_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
  COMMENT='商品成色字典表';

-- ------------------------------------------------------------
-- 4. 交易地点表 trade_places（字典表）
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `trade_places` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(50) NOT NULL COMMENT '地点名称，如 东区宿舍楼下',
  `sort_order` INT NOT NULL DEFAULT 0,
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_place_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
  COMMENT='交易地点字典表';

-- ------------------------------------------------------------
-- 5. 商品表 products（基础实体表）
--    status：1 在售 / 2 已预订 / 3 已售出 / 4 已下架
--    商品状态由触发器随订单自动流转，应用层只读此列
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `products` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `seller_id` INT NOT NULL COMMENT '发布者（卖家）id',
  `category_id` INT NOT NULL COMMENT '分类 id',
  `condition_id` INT NOT NULL COMMENT '成色 id',
  `place_id` INT DEFAULT NULL COMMENT '期望交易地点 id（可空）',
  `title` VARCHAR(100) NOT NULL COMMENT '商品标题',
  `description` TEXT COMMENT '商品描述',
  `price` DECIMAL(10,2) NOT NULL COMMENT '价格（元）',
  `status` TINYINT NOT NULL DEFAULT 1 COMMENT '1在售 2已预订 3已售出 4已下架',
  `view_count` INT NOT NULL DEFAULT 0 COMMENT '浏览量',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '发布时间',
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
             ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_products_seller`
    FOREIGN KEY (`seller_id`) REFERENCES `users` (`id`),
  CONSTRAINT `fk_products_category`
    FOREIGN KEY (`category_id`) REFERENCES `categories` (`id`),
  CONSTRAINT `fk_products_condition`
    FOREIGN KEY (`condition_id`) REFERENCES `condition_levels` (`id`),
  CONSTRAINT `fk_products_place`
    FOREIGN KEY (`place_id`) REFERENCES `trade_places` (`id`),
  CONSTRAINT `chk_products_price` CHECK (`price` > 0 AND `price` <= 99999.99),
  CONSTRAINT `chk_products_status` CHECK (`status` IN (1, 2, 3, 4)),
  KEY `idx_products_category` (`category_id`),
  KEY `idx_products_seller` (`seller_id`),
  KEY `idx_products_list` (`status`, `created_at`),   -- 商品列表页：在售 + 按时间倒序
  FULLTEXT KEY `ft_products_search` (`title`, `description`) WITH PARSER ngram  -- 中文模糊检索
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
  COMMENT='二手商品表';

-- ------------------------------------------------------------
-- 6. 商品图片表 product_images（联系表：商品 1:N 图片）
--    商品删除时图片级联清理
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `product_images` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `product_id` INT NOT NULL COMMENT '所属商品 id',
  `url` VARCHAR(255) NOT NULL COMMENT '图片地址',
  `sort_order` INT NOT NULL DEFAULT 0 COMMENT '展示顺序',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_images_product`
    FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
    ON DELETE CASCADE,
  KEY `idx_images_product` (`product_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
  COMMENT='商品图片表';

-- ------------------------------------------------------------
-- 7. 收藏表 favorites（联系表：用户 M:N 商品）
--    同一用户对同一商品仅一条记录（UNIQUE 保证）
--    用户注销不删行；商品删除时收藏级联清理
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `favorites` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL COMMENT '收藏者 id',
  `product_id` INT NOT NULL COMMENT '商品 id',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_fav_user_product` (`user_id`, `product_id`),
  CONSTRAINT `fk_favorites_user`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `fk_favorites_product`
    FOREIGN KEY (`product_id`) REFERENCES `products` (`id`)
    ON DELETE CASCADE,
  KEY `idx_favorites_product` (`product_id`)  -- 统计商品收藏量
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
  COMMENT='用户收藏表';

-- ------------------------------------------------------------
-- 8. 订单表 orders（联系表：一次交易生成一条订单）
--    status：1 待确认 / 2 已确认 / 3 已完成 / 4 已取消
--    约束：
--      a. 买家与卖家不能为同一人（CHECK）
--      b. 商品必须"在售"才能下单（triggers.sql 中 trg_orders_bi 校验）
--      c. 订单状态由应用层更新，商品状态由触发器联动
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `orders` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `product_id` INT NOT NULL COMMENT '商品 id',
  `buyer_id` INT NOT NULL COMMENT '买家 id',
  `seller_id` INT NOT NULL COMMENT '卖家 id（下单时从商品冗余，便于查询）',
  `place_id` INT DEFAULT NULL COMMENT '约定交易地点 id（下单时选择）',
  `contact` VARCHAR(100) DEFAULT NULL COMMENT '买家联系方式（下单时快照）',
  `status` TINYINT NOT NULL DEFAULT 1 COMMENT '1待确认 2已确认 3已完成 4已取消',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '下单时间',
  `finished_at` DATETIME DEFAULT NULL COMMENT '完成/取消时间',
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_orders_product`
    FOREIGN KEY (`product_id`) REFERENCES `products` (`id`),
  CONSTRAINT `fk_orders_buyer`
    FOREIGN KEY (`buyer_id`) REFERENCES `users` (`id`),
  CONSTRAINT `fk_orders_seller`
    FOREIGN KEY (`seller_id`) REFERENCES `users` (`id`),
  CONSTRAINT `fk_orders_place`
    FOREIGN KEY (`place_id`) REFERENCES `trade_places` (`id`),
  CONSTRAINT `chk_orders_status` CHECK (`status` IN (1, 2, 3, 4)),
  CONSTRAINT `chk_orders_not_self` CHECK (`buyer_id` <> `seller_id`),
  KEY `idx_orders_buyer` (`buyer_id`, `status`),
  KEY `idx_orders_seller` (`seller_id`, `status`),
  KEY `idx_orders_product` (`product_id`, `status`),
  KEY `idx_orders_created` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
  COMMENT='订单表';

-- ------------------------------------------------------------
-- 9. 管理员操作日志表 admin_logs（辅助表）
--    两种写入来源：
--      a. 应用层记录管理员下架/封禁操作
--      b. trg_users_after_update 触发器自动记录用户状态变更（admin_id 为空）
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS `admin_logs` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `admin_id` INT DEFAULT NULL COMMENT '操作管理员 id，触发器自动记录时为空',
  `action` VARCHAR(40) NOT NULL
    COMMENT '操作类型：delist_product/product_on_shelf/ban_user/unban_user/auto_user_status',
  `target_type` VARCHAR(20) NOT NULL COMMENT '操作对象类型：user/product',
  `target_id` INT NOT NULL COMMENT '操作对象 id',
  `detail` VARCHAR(255) DEFAULT NULL COMMENT '操作说明',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_logs_admin`
    FOREIGN KEY (`admin_id`) REFERENCES `users` (`id`),
  KEY `idx_logs_created` (`created_at`),
  KEY `idx_logs_target` (`target_type`, `target_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
  COMMENT='管理员操作日志表';
