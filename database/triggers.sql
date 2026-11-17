-- ============================================================
--  校园二手交易平台 - 触发器脚本（triggers.sql）
--  执行顺序：schema.sql  →  triggers.sql  →  seed_data.sql
--
--  设计说明：
--  商品状态（1在售/2已预订/3已售出）与订单状态（1待确认/2已确认/
--  3已完成/4已取消）的一致性，由数据库触发器自动维护。
--  后端只需 INSERT 订单、UPDATE 订单状态即可，无需手动改商品状态，
--  从而保证"下单、取消、完成涉及两张表"的跨表一致性（需求 4）。
-- ============================================================

USE `second_hand_trade`;

DELIMITER $$

-- ------------------------------------------------------------
-- T1  trg_orders_bi_check：下单前校验（BEFORE INSERT ON orders）
--     商品必须处于"在售"状态，否则拒单
--     （配合 CHECK buyer<>seller，从数据库层面杜绝非法订单）
-- ------------------------------------------------------------
CREATE TRIGGER `trg_orders_bi_check`
BEFORE INSERT ON `orders`
FOR EACH ROW
BEGIN
  DECLARE v_status INT;

  SELECT `status` INTO v_status
  FROM `products` WHERE `id` = NEW.`product_id`;

  IF v_status IS NULL THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = '下单失败：商品不存在';
  ELSEIF v_status <> 1 THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = '下单失败：商品当前不在售';
  END IF;
END$$

-- ------------------------------------------------------------
-- T2  trg_orders_ai_reserve：下单后商品置为"已预订"
--     （AFTER INSERT ON orders）
-- ------------------------------------------------------------
CREATE TRIGGER `trg_orders_ai_reserve`
AFTER INSERT ON `orders`
FOR EACH ROW
BEGIN
  UPDATE `products` SET `status` = 2 WHERE `id` = NEW.`product_id`;
END$$

-- ------------------------------------------------------------
-- T3  trg_orders_au_sync：订单状态更新后联动商品状态
--     订单已完成(3) → 商品置"已售出"
--     订单已取消(4) → 商品恢复"在售"
--     （AFTER UPDATE ON orders）
-- ------------------------------------------------------------
CREATE TRIGGER `trg_orders_au_sync`
AFTER UPDATE ON `orders`
FOR EACH ROW
BEGIN
  IF NEW.`status` <> OLD.`status` THEN
    IF NEW.`status` = 3 THEN
      UPDATE `products` SET `status` = 3 WHERE `id` = NEW.`product_id`;
    ELSEIF NEW.`status` = 4 THEN
      UPDATE `products` SET `status` = 1 WHERE `id` = NEW.`product_id`;
    END IF;
  END IF;
END$$

-- ------------------------------------------------------------
-- T4  trg_users_au_log：用户封禁/解封审计（AFTER UPDATE ON users）
--     status 变化时自动写入 admin_logs（审计触发器）
-- ------------------------------------------------------------
CREATE TRIGGER `trg_users_au_log`
AFTER UPDATE ON `users`
FOR EACH ROW
BEGIN
  IF OLD.`status` <> NEW.`status` THEN
    INSERT INTO `admin_logs`
      (`admin_id`, `action`, `target_type`, `target_id`, `detail`)
    VALUES
      (NULL, 'auto_user_status', 'user', OLD.`id`,
       CONCAT('用户状态变更: ', OLD.`status`, ' -> ', NEW.`status`));
  END IF;
END$$

DELIMITER ;
