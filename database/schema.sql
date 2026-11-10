-- ===========================================
--   校园二手交易平台 - 数据库建表脚本
--   当前为最小可运行版本，仅包含 users 表
--   后续商品、订单等表由数据库组员逐步补充
-- ===========================================

CREATE TABLE IF NOT EXISTS `users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `student_no` VARCHAR(20) NOT NULL,
  `email` VARCHAR(100) NOT NULL,
  `nickname` VARCHAR(50) NOT NULL,
  `avatar` VARCHAR(255) DEFAULT NULL,
  `contact` VARCHAR(100) DEFAULT NULL,
  `is_admin` TINYINT(1) NOT NULL DEFAULT 0,
  `status` INT NOT NULL DEFAULT 1 COMMENT '1 正常, 0 已封禁',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `_password` VARCHAR(200) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `student_no` (`student_no`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
