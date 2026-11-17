-- ============================================================
--  校园二手交易平台 - 测试数据脚本（seed_data.sql）
--  执行顺序：schema.sql  →  triggers.sql  →  seed_data.sql
--
--  说明：
--  1. 所有用户密码统一为 123456，哈希由后端同款 pwdlib(0.3.1)
--     Argon2 算法生成，可直接用于登录测试
--  2. 时间字段使用 NOW() 相对偏移，任何时间导入，趋势图都有数据
--  3. 订单按"先插入、再更新状态"的顺序书写：
--     商品状态由触发器自动流转，本脚本执行成功即代表触发器工作正常
--  4. 前三条用户为本组成员（见选题文档），第 1 位为管理员
-- ============================================================

USE `second_hand_trade`;

SET FOREIGN_KEY_CHECKS = 1;

-- ------------------------------------------------------------
-- 1. 用户（10 人：1 管理员 + 9 普通用户）
-- ------------------------------------------------------------
INSERT INTO `users`
  (`id`, `student_no`, `email`, `nickname`, `avatar`, `contact`, `is_admin`, `status`, `created_at`, `_password`) VALUES
(1,  '2024141460245', '2024141460245@stu.edu.cn', '宋组长',  NULL, 'WeChat: sjx_db',     1, 1, DATE_SUB(NOW(), INTERVAL 60 DAY), '$argon2id$v=19$m=65536,t=3,p=4$FOCqISrqgH9XvvkP//tdJQ$VoGSFQo864825sxWqFpFcZq2m5XIEPXGQ+3vnZTUriE'),
(2,  '2024141460485', '2024141460485@stu.edu.cn', '兵哥',    '/static/avatars/u2.jpg',  'WeChat: mb_front',   0, 1, DATE_SUB(NOW(), INTERVAL 55 DAY), '$argon2id$v=19$m=65536,t=3,p=4$FOCqISrqgH9XvvkP//tdJQ$VoGSFQo864825sxWqFpFcZq2m5XIEPXGQ+3vnZTUriE'),
(3,  '2024141460218', '2024141460218@stu.edu.cn', '轩仔',    '/static/avatars/u3.jpg',  'WeChat: wjx_back',   0, 1, DATE_SUB(NOW(), INTERVAL 50 DAY), '$argon2id$v=19$m=65536,t=3,p=4$FOCqISrqgH9XvvkP//tdJQ$VoGSFQo864825sxWqFpFcZq2m5XIEPXGQ+3vnZTUriE'),
(4,  '2024141460301', '2024141460301@stu.edu.cn', '晨曦',    NULL, 'QQ: 3001',           0, 1, DATE_SUB(NOW(), INTERVAL 45 DAY), '$argon2id$v=19$m=65536,t=3,p=4$FOCqISrqgH9XvvkP//tdJQ$VoGSFQo864825sxWqFpFcZq2m5XIEPXGQ+3vnZTUriE'),
(5,  '2024141460366', '2024141460366@stu.edu.cn', '小美同学',  '/static/avatars/u5.jpg',  'WeChat: xm366',      0, 1, DATE_SUB(NOW(), INTERVAL 42 DAY), '$argon2id$v=19$m=65536,t=3,p=4$FOCqISrqgH9XvvkP//tdJQ$VoGSFQo864825sxWqFpFcZq2m5XIEPXGQ+3vnZTUriE'),
(6,  '2024141460520', '2024141460520@stu.edu.cn', '浩然',    NULL, '手机尾号1520',       0, 1, DATE_SUB(NOW(), INTERVAL 35 DAY), '$argon2id$v=19$m=65536,t=3,p=4$FOCqISrqgH9XvvkP//tdJQ$VoGSFQo864825sxWqFpFcZq2m5XIEPXGQ+3vnZTUriE'),
(7,  '2024141460777', '2024141460777@stu.edu.cn', '雨桐',    '/static/avatars/u7.jpg',  'WeChat: yt777',      0, 1, DATE_SUB(NOW(), INTERVAL 28 DAY), '$argon2id$v=19$m=65536,t=3,p=4$FOCqISrqgH9XvvkP//tdJQ$VoGSFQo864825sxWqFpFcZq2m5XIEPXGQ+3vnZTUriE'),
(8,  '2024141460808', '2024141460808@stu.edu.cn', '子豪',    NULL, 'QQ: 3808',           0, 1, DATE_SUB(NOW(), INTERVAL 20 DAY), '$argon2id$v=19$m=65536,t=3,p=4$FOCqISrqgH9XvvkP//tdJQ$VoGSFQo864825sxWqFpFcZq2m5XIEPXGQ+3vnZTUriE'),
(9,  '2024141460912', '2024141460912@stu.edu.cn', '欣然',    NULL, 'WeChat: xr912',      0, 1, DATE_SUB(NOW(), INTERVAL 12 DAY), '$argon2id$v=19$m=65536,t=3,p=4$FOCqISrqgH9XvvkP//tdJQ$VoGSFQo864825sxWqFpFcZq2m5XIEPXGQ+3vnZTUriE'),
(10, '2024141460999', '2024141460999@stu.edu.cn', '一帆',    NULL, 'QQ: 3999',           0, 1, DATE_SUB(NOW(), INTERVAL 5 DAY),  '$argon2id$v=19$m=65536,t=3,p=4$FOCqISrqgH9XvvkP//tdJQ$VoGSFQo864825sxWqFpFcZq2m5XIEPXGQ+3vnZTUriE');

-- ------------------------------------------------------------
-- 2. 商品分类（字典，8 类）
-- ------------------------------------------------------------
INSERT INTO `categories` (`id`, `name`, `sort_order`) VALUES
(1, '教材书籍', 1),
(2, '电子产品', 2),
(3, '生活用品', 3),
(4, '运动健身', 4),
(5, '服饰鞋包', 5),
(6, '文具用品', 6),
(7, '美妆个护', 7),
(8, '乐器', 8);

-- ------------------------------------------------------------
-- 3. 成色（字典，5 档）
-- ------------------------------------------------------------
INSERT INTO `condition_levels` (`id`, `name`, `sort_order`) VALUES
(1, '全新未拆封', 1),
(2, '九成新', 2),
(3, '八成新', 3),
(4, '七成新', 4),
(5, '明显使用痕迹', 5);

-- ------------------------------------------------------------
-- 4. 交易地点（字典，6 处）
-- ------------------------------------------------------------
INSERT INTO `trade_places` (`id`, `name`, `sort_order`) VALUES
(1, '东区宿舍楼下', 1),
(2, '西区宿舍楼下', 2),
(3, '第一食堂门口', 3),
(4, '图书馆北门', 4),
(5, '教学楼A栋大厅', 5),
(6, '校门口快递站', 6);

-- ------------------------------------------------------------
-- 5. 商品（24 件，全部初始为"在售"）
--    23、24 为管理员下架商品，直接以状态 4 写入
-- ------------------------------------------------------------
INSERT INTO `products`
  (`id`, `seller_id`, `category_id`, `condition_id`, `place_id`, `title`, `description`, `price`, `status`, `view_count`, `created_at`) VALUES
(1,  2,  1, 3, 4, '高等数学（第七版）上下册',        '同济版高数，期末95分出，无笔记涂画，配答案册',                 25.00, 1, 132, DATE_SUB(NOW(), INTERVAL 38 DAY)),
(2,  4,  1, 2, 5, '大学物理实验报告册',              '只剩两次实验没写，纸质干净，需要的同学可拆页复印思路',           10.00, 1,  45, DATE_SUB(NOW(), INTERVAL 12 DAY)),
(3,  3,  1, 2, 4, 'C语言程序设计（第5版）谭浩强',    '经典教材，转专业出，书脊完好',                                 30.00, 1,  98, DATE_SUB(NOW(), INTERVAL 35 DAY)),
(4,  5,  2, 3, 1, 'iPad 2021 第九代 64G WiFi版',    '自用一年半，电池健康良好，贴膜带壳，可送笔尖贴和保护壳',         1800.00, 1, 356, DATE_SUB(NOW(), INTERVAL 30 DAY)),
(5,  6,  2, 2, 2, '罗技G102游戏鼠标',               'RGB灯效，寝室吃灰半年，功能一切正常',                           79.00, 1, 210, DATE_SUB(NOW(), INTERVAL 25 DAY)),
(6,  7,  2, 2, 3, '小米台灯Pro',                     '国AA级照度，宿舍学习神器，原装充电器在',                        65.00, 1,  88, DATE_SUB(NOW(), INTERVAL 20 DAY)),
(7,  8,  2, 4, 4, '索尼WH-CH510头戴耳机',           '音质在线，耳罩垫已酒精消毒，送收纳袋',                         120.00, 1, 156, DATE_SUB(NOW(), INTERVAL 15 DAY)),
(8,  2,  2, 1, 6, '苹果MagSafe充电线 1米',           '全新未拆封，买错型号了，官方正品可验货',                       45.00, 1,  66, DATE_SUB(NOW(), INTERVAL 8 DAY)),
(9,  9,  3, 2, 1, '吹风机 1800W 大风力',             '毕业出，风力大，用过一学期',                                   38.00, 1,  54, DATE_SUB(NOW(), INTERVAL 22 DAY)),
(10, 4,  3, 3, 2, '挂烫机 手持迷你款',               '宿舍熨衬衫神器，赠量杯',                                       55.00, 1,  30, DATE_SUB(NOW(), INTERVAL 33 DAY)),
(11, 10, 3, 3, 1, '台式小风扇 三档风速',             '夏天神器，静音款，缺一节螺丝但完全不晃',                       25.00, 1,  47, DATE_SUB(NOW(), INTERVAL 10 DAY)),
(12, 5,  8, 2, 3, '尤克里里 23寸 合板琴',            '入门琴，送琴包+调音器+教程，弦已换新',                        158.00, 1, 189, DATE_SUB(NOW(), INTERVAL 18 DAY)),
(13, 6,  4, 2, 5, '篮球 7号球 室内外通用',           '打了一学期，气足不漏，仿真皮手感',                             68.00, 1,  92, DATE_SUB(NOW(), INTERVAL 28 DAY)),
(14, 7,  4, 1, 4, '瑜伽垫 TPE 6mm 加厚',            '全新未拆封，买重复了',                                         42.00, 1,  73, DATE_SUB(NOW(), INTERVAL 9 DAY)),
(15, 8,  4, 3, 5, '哑铃一对 10kg 包胶',              '八成新，胶面完好，毕业急出',                                   90.00, 1,  61, DATE_SUB(NOW(), INTERVAL 40 DAY)),
(16, 9,  5, 2, 2, '优衣库连帽卫衣 M码 深灰',         '洗过两次无起球，袖口完好',                                     60.00, 1, 120, DATE_SUB(NOW(), INTERVAL 14 DAY)),
(17, 10, 5, 4, 3, 'Nike Air 系列运动鞋 42码',        '鞋底磨损见照片，日常压马路没问题，原盒在',                     150.00, 1, 234, DATE_SUB(NOW(), INTERVAL 26 DAY)),
(18, 3,  6, 1, 5, '斑马中性笔 JJ15 10支装',          '全新套装，0.5mm 黑色，考试周刚需',                             15.00, 1,  39, DATE_SUB(NOW(), INTERVAL 6 DAY)),
(19, 4,  6, 2, 4, '得力订书机+两盒订书钉',           '九成新，宿舍整理资料用的',                                     12.00, 1,  25, DATE_SUB(NOW(), INTERVAL 16 DAY)),
(20, 6,  6, 3, 5, '康奈尔笔记法笔记本 8本',           '没用过的空白本，考研党组织行为，单出也行',                     20.00, 1,  58, DATE_SUB(NOW(), INTERVAL 11 DAY)),
(21, 7,  7, 1, 1, '欧莱雅男士洗面奶 100ml',          '未拆封，买多了一支，小票在可验',                               45.00, 1, 143, DATE_SUB(NOW(), INTERVAL 13 DAY)),
(22, 9,  7, 2, 2, '薄荷润唇膏 唇部护理套装',          '九成新，男女通用，冬天救星',                                   18.00, 1,  36, DATE_SUB(NOW(), INTERVAL 5 DAY)),
(23, 10, 2, 3, 4, '机械键盘 87键 红轴',              '自用键盘，键帽微油光，手感和新的一样',                         199.00, 4, 278, DATE_SUB(NOW(), INTERVAL 17 DAY)),
(24, 8,  1, 4, 4, '考研英语一真题 历年全集',          '含答案解析，真题无涂画，模拟卷有笔记',                         28.00, 4, 305, DATE_SUB(NOW(), INTERVAL 21 DAY));

-- ------------------------------------------------------------
-- 6. 商品图片（图片路径为占位地址，前端可自行替换）
-- ------------------------------------------------------------
INSERT INTO `product_images` (`product_id`, `url`, `sort_order`) VALUES
(1,  '/static/uploads/p1_1.jpg', 0), (1,  '/static/uploads/p1_2.jpg', 1),
(2,  '/static/uploads/p2_1.jpg', 0), (2,  '/static/uploads/p2_2.jpg', 1),
(3,  '/static/uploads/p3_1.jpg', 0), (3,  '/static/uploads/p3_2.jpg', 1),
(4,  '/static/uploads/p4_1.jpg', 0), (4,  '/static/uploads/p4_2.jpg', 1), (4, '/static/uploads/p4_3.jpg', 2),
(5,  '/static/uploads/p5_1.jpg', 0), (5,  '/static/uploads/p5_2.jpg', 1),
(6,  '/static/uploads/p6_1.jpg', 0), (6,  '/static/uploads/p6_2.jpg', 1),
(7,  '/static/uploads/p7_1.jpg', 0), (7,  '/static/uploads/p7_2.jpg', 1),
(8,  '/static/uploads/p8_1.jpg', 0),
(9,  '/static/uploads/p9_1.jpg', 0), (9,  '/static/uploads/p9_2.jpg', 1),
(10, '/static/uploads/p10_1.jpg', 0),
(11, '/static/uploads/p11_1.jpg', 0), (11, '/static/uploads/p11_2.jpg', 1),
(12, '/static/uploads/p12_1.jpg', 0), (12, '/static/uploads/p12_2.jpg', 1), (12, '/static/uploads/p12_3.jpg', 2),
(13, '/static/uploads/p13_1.jpg', 0), (13, '/static/uploads/p13_2.jpg', 1),
(14, '/static/uploads/p14_1.jpg', 0),
(15, '/static/uploads/p15_1.jpg', 0), (15, '/static/uploads/p15_2.jpg', 1),
(16, '/static/uploads/p16_1.jpg', 0), (16, '/static/uploads/p16_2.jpg', 1),
(17, '/static/uploads/p17_1.jpg', 0), (17, '/static/uploads/p17_2.jpg', 1), (17, '/static/uploads/p17_3.jpg', 2),
(18, '/static/uploads/p18_1.jpg', 0),
(19, '/static/uploads/p19_1.jpg', 0),
(20, '/static/uploads/p20_1.jpg', 0), (20, '/static/uploads/p20_2.jpg', 1),
(21, '/static/uploads/p21_1.jpg', 0), (21, '/static/uploads/p21_2.jpg', 1),
(22, '/static/uploads/p22_1.jpg', 0),
(23, '/static/uploads/p23_1.jpg', 0), (23, '/static/uploads/p23_2.jpg', 1),
(24, '/static/uploads/p24_1.jpg', 0), (24, '/static/uploads/p24_2.jpg', 1);

-- ------------------------------------------------------------
-- 7. 收藏（32 条，(user_id, product_id) 唯一）
-- ------------------------------------------------------------
INSERT INTO `favorites` (`user_id`, `product_id`, `created_at`) VALUES
(1, 4,  DATE_SUB(NOW(), INTERVAL 29 DAY)), (1, 7,  DATE_SUB(NOW(), INTERVAL 14 DAY)), (1, 12, DATE_SUB(NOW(), INTERVAL 17 DAY)),
(2, 3,  DATE_SUB(NOW(), INTERVAL 30 DAY)), (2, 5,  DATE_SUB(NOW(), INTERVAL 23 DAY)), (2, 13, DATE_SUB(NOW(), INTERVAL 20 DAY)), (2, 16, DATE_SUB(NOW(), INTERVAL 10 DAY)),
(3, 4,  DATE_SUB(NOW(), INTERVAL 28 DAY)), (3, 15, DATE_SUB(NOW(), INTERVAL 12 DAY)), (3, 23, DATE_SUB(NOW(), INTERVAL 9 DAY)),
(4, 1,  DATE_SUB(NOW(), INTERVAL 31 DAY)), (4, 12, DATE_SUB(NOW(), INTERVAL 11 DAY)), (4, 17, DATE_SUB(NOW(), INTERVAL 3 DAY)),  (4, 22, DATE_SUB(NOW(), INTERVAL 2 DAY)),
(5, 6,  DATE_SUB(NOW(), INTERVAL 18 DAY)), (5, 9,  DATE_SUB(NOW(), INTERVAL 15 DAY)), (5, 13, DATE_SUB(NOW(), INTERVAL 7 DAY)),
(6, 4,  DATE_SUB(NOW(), INTERVAL 27 DAY)), (6, 14, DATE_SUB(NOW(), INTERVAL 8 DAY)),  (6, 21, DATE_SUB(NOW(), INTERVAL 6 DAY)),  (6, 18, DATE_SUB(NOW(), INTERVAL 4 DAY)),
(7, 3,  DATE_SUB(NOW(), INTERVAL 26 DAY)), (7, 9,  DATE_SUB(NOW(), INTERVAL 5 DAY)),  (7, 20, DATE_SUB(NOW(), INTERVAL 7 DAY)),
(8, 1,  DATE_SUB(NOW(), INTERVAL 24 DAY)), (8, 12, DATE_SUB(NOW(), INTERVAL 13 DAY)), (8, 24, DATE_SUB(NOW(), INTERVAL 6 DAY)),
(9, 4,  DATE_SUB(NOW(), INTERVAL 25 DAY)), (9, 7,  DATE_SUB(NOW(), INTERVAL 4 DAY)),  (9, 16, DATE_SUB(NOW(), INTERVAL 3 DAY)),
(10, 2, DATE_SUB(NOW(), INTERVAL 2 DAY)),  (10, 15, DATE_SUB(NOW(), INTERVAL 1 DAY));

-- ------------------------------------------------------------
-- 8. 订单第一批（o1~o10）：插入后触发器自动将商品置"已预订"
--    注意 o11 需等 o10 取消、篮球恢复在售后才能插入
-- ------------------------------------------------------------
INSERT INTO `orders`
  (`id`, `product_id`, `buyer_id`, `seller_id`, `place_id`, `contact`, `status`, `created_at`) VALUES
(1,  4,  3,  5,  1, 'WeChat: wjx_back', 1, DATE_SUB(NOW(), INTERVAL 2 DAY)),   -- iPad，待确认
(2,  15, 2,  8,  5, 'WeChat: mb_front',  1, DATE_SUB(NOW(), INTERVAL 38 DAY)),  -- 哑铃（后更新为已完成）
(3,  2,  5,  4,  5, 'WeChat: xm366',    1, DATE_SUB(NOW(), INTERVAL 10 DAY)),  -- 实验报告册（后更新为已完成）
(4,  12, 2,  5,  3, 'WeChat: mb_front',  1, DATE_SUB(NOW(), INTERVAL 16 DAY)),  -- 尤克里里（后更新为已完成）
(5,  7,  9,  8,  4, 'WeChat: xr912',    1, DATE_SUB(NOW(), INTERVAL 4 DAY)),   -- 索尼耳机，已确认
(6,  17, 4,  10, 3, 'QQ: 3001',        1, DATE_SUB(NOW(), INTERVAL 3 DAY)),   -- Nike鞋，已确认
(7,  21, 6,  7,  1, 'WeChat: yt777',   1, DATE_SUB(NOW(), INTERVAL 1 DAY)),   -- 洗面奶，待确认
(8,  1,  8,  2,  4, 'QQ: 3808',        1, DATE_SUB(NOW(), INTERVAL 36 DAY)),  -- 高数书（后取消，恢复在售）
(9,  6,  10, 7,  3, 'QQ: 3999',        1, DATE_SUB(NOW(), INTERVAL 19 DAY)),  -- 台灯（后更新为已完成）
(10, 13, 3,  6,  5, 'WeChat: wjx_back', 1, DATE_SUB(NOW(), INTERVAL 27 DAY));  -- 篮球（后取消，被重新下单）

-- 8.1 取消 o8（高数书）：触发器自动把商品 1 恢复"在售"
UPDATE `orders`
SET `status` = 4, `finished_at` = DATE_SUB(NOW(), INTERVAL 36 DAY)
WHERE `id` = 8;

-- 8.2 取消 o10（篮球第一次）：触发器自动把商品 13 恢复"在售"
UPDATE `orders`
SET `status` = 4, `finished_at` = DATE_SUB(NOW(), INTERVAL 26 DAY)
WHERE `id` = 10;

-- 8.3 篮球被另一位买家重新下单（此时商品 13 已恢复在售，触发器校验通过）
INSERT INTO `orders`
  (`id`, `product_id`, `buyer_id`, `seller_id`, `place_id`, `contact`, `status`, `created_at`) VALUES
(11, 13, 9, 6, 5, 'WeChat: xr912', 1, DATE_SUB(NOW(), INTERVAL 24 DAY));

-- 8.4 完成确认：o2/o3/o4/o9/o11 置"已完成"，触发器自动把对应商品置"已售出"
UPDATE `orders`
SET `status` = 3, `finished_at` = DATE_SUB(NOW(), INTERVAL 35 DAY)
WHERE `id` = 2;
UPDATE `orders`
SET `status` = 3, `finished_at` = DATE_SUB(NOW(), INTERVAL 9 DAY)
WHERE `id` = 3;
UPDATE `orders`
SET `status` = 3, `finished_at` = DATE_SUB(NOW(), INTERVAL 14 DAY)
WHERE `id` = 4;
UPDATE `orders`
SET `status` = 3, `finished_at` = DATE_SUB(NOW(), INTERVAL 18 DAY)
WHERE `id` = 9;
UPDATE `orders`
SET `status` = 3, `finished_at` = DATE_SUB(NOW(), INTERVAL 23 DAY)
WHERE `id` = 11;

-- 8.5 卖家确认 o5/o6：置"已确认"（商品保持"已预订"）
UPDATE `orders` SET `status` = 2 WHERE `id` = 5;
UPDATE `orders` SET `status` = 2 WHERE `id` = 6;

-- 8.6 一笔刚下的订单（今天，6小时前）
INSERT INTO `orders`
  (`id`, `product_id`, `buyer_id`, `seller_id`, `place_id`, `contact`, `status`, `created_at`) VALUES
(12, 5, 4, 6, 2, 'QQ: 3001', 1, DATE_SUB(NOW(), INTERVAL 6 HOUR));  -- 罗技鼠标，待确认

-- ------------------------------------------------------------
-- 9. 管理员操作（第 23、24 号商品已在上方直接以"已下架"写入）
--    这里记录管理员下架与封禁的日志（应用层写入）
-- ------------------------------------------------------------
INSERT INTO `admin_logs` (`admin_id`, `action`, `target_type`, `target_id`, `detail`) VALUES
(1, 'delist_product', 'product', 23, '商品描述与实物不符，管理员下架'),
(1, 'delist_product', 'product', 24, '涉及盗版资料，管理员下架');

-- 9.1 封禁用户 10（一帆）：UPDATE 触发审计触发器，自动写入一条 auto_user_status 日志
UPDATE `users` SET `status` = 0 WHERE `id` = 10;

-- 9.2 管理员解封示例（再触发一次审计日志，展示解封流程）
UPDATE `users` SET `status` = 1 WHERE `id` = 10;

-- ============================================================
-- 数据导入完成后的状态概览：
--   在售 12 件：1、3、8、9、10、11、14、16、18、19、20、22
--   已预订 5 件：4、5、7、17、21
--   已售出 5 件：2、6、12、13、15
--   已下架 2 件：23、24
--   订单 12 笔：待确认 3 / 已确认 2 / 已完成 5 / 已取消 2
-- ============================================================
