# 校园二手交易平台 - 数据库部分说明



## 文件清单

| 文件                  | 作用                                         | 执行顺序  |
| ------------------- | ------------------------------------------ | ----- |
| `schema.sql`        | 建库、9 张表（含全部主键 / 外键 / UNIQUE / CHECK 约束、索引） | 第 1 步 |
| `triggers.sql`      | 4 个触发器（下单校验、状态联动、审计日志）                     | 第 2 步 |
| `seed_data.sql`     | 测试数据（10 用户 / 24 商品 / 32 收藏 / 12 订单）        | 第 3 步 |
| `stats_queries.sql` | 统计分析查询（D1~D5 + 2 个加分项），可随时执行               | 按需    |

## 执行方法

命令行（任选其一）：

```bash
# 依次执行三个脚本（会提示输入 MySQL 密码）
mysql -u root -p < database/schema.sql
mysql -u root -p < database/triggers.sql
mysql -u root -p < database/seed_data.sql
```

或直接把三个文件的内容依次粘进 Navicat 查询窗口执行。

**重置数据库**（开发阶段反复导入时用）：

```bash
mysql -u root -p -e "DROP DATABASE IF EXISTS second_hand_trade;"
```

然后重新按 1→2→3 顺序执行。

## 表结构总览（共 9 张，满足"8 张表以上"要求）

| 表                  | 类型   | 说明                        |
| ------------------ | ---- | ------------------------- |
| `users`            | 基础实体 | 平台用户（与后端 SQLAlchemy 模型一致） |
| `products`         | 基础实体 | 二手商品                      |
| `categories`       | 字典表  | 商品分类（8 类预置）               |
| `condition_levels` | 字典表  | 成色（5 档预置）                 |
| `trade_places`     | 字典表  | 交易地点（6 处预置）               |
| `product_images`   | 联系表  | 商品图片（1:N，随商品级联删除）         |
| `favorites`        | 联系表  | 收藏（M:N，UNIQUE 防重复收藏）      |
| `orders`           | 联系表  | 订单（CHECK 买家≠卖家）           |
| `admin_logs`       | 辅助表  | 管理员操作日志（含触发器自动审计）         |

## 状态字典

**商品 `products.status`**（由触发器自动维护，应用层只读）：

| 值   | 含义  | 由谁改变      |
| --- | --- | --------- |
| 1   | 在售  | 订单取消后自动恢复 |
| 2   | 已预订 | 买家下单后自动置为 |
| 3   | 已售出 | 订单完成后自动置为 |
| 4   | 已下架 | 管理员手动操作   |

**订单 `orders.status`**（由后端 UPDATE）：

| 值   | 含义          |
| --- | ----------- |
| 1   | 待确认         |
| 2   | 已确认（双方约好面交） |
| 3   | 已完成         |
| 4   | 已取消         |

## ⚠️ 给后端同学的重要约定（吴佳轩请看这里）

1. **不要在应用层手动 UPDATE `products.status` 的 1/2/3**。
   下单时只需 `INSERT INTO orders`，商品自动变"已预订"；
   订单置 3（完成）商品自动变"已售出"，订单置 4（取消）商品自动恢复"在售"。
   下单时商品若不在售，触发器会直接报错（SIGNAL），后端捕获该错误返回给前端即可。
2. 只有**管理员下架/重新上架**（status 4 ↔ 1）才由后端直接 UPDATE `products.status`。
3. `users` 表列名与 `models/user.py` 完全一致（密码列叫 `_password`），已建库请勿改列名。
4. 统计接口直接参考 `stats_queries.sql`，每段注释对应需求 D1~D5，字段名即 JSON 字段名。
5. 数据库连接串见 `backend/.env.example`，库名 `second_hand_trade`。

## 触发器清单

| 触发器                     | 时机          | 作用                         |
| ----------------------- | ----------- | -------------------------- |
| `trg_orders_bi_check`   | 订单 INSERT 前 | 校验商品必须"在售"，否则 SIGNAL 拒单    |
| `trg_orders_ai_reserve` | 订单 INSERT 后 | 商品置"已预订"(2)                |
| `trg_orders_au_sync`    | 订单 UPDATE 后 | 完成→商品已售出；取消→商品恢复在售         |
| `trg_users_au_log`      | 用户 UPDATE 后 | 封禁/解封自动写入 `admin_logs`（审计） |

## 测试账号（密码统一为 `123456`）

| 学号（登录用）       | 昵称   | 角色      |
| ------------- | ---- | ------- |
| 2024141460245 | 宋组长  | **管理员** |
| 2024141460485 | 兵哥   | 普通用户    |
| 2024141460218 | 轩仔   | 普通用户    |
| 2024141460301 | 晨曦   | 普通用户    |
| 2024141460366 | 小美同学 | 普通用户    |

其余 5 个账号见 `seed_data.sql`，密码均为 `123456`。
密码哈希由后端同款 `pwdlib(0.3.1) PasswordHash.recommended()`（Argon2）生成，登录接口可直接验证通过。

## 期末交付：数据库备份文件

全部脚本验证通过后，用以下命令导出最终备份（对应提交材料"x组-数据库备份文件"）：

```bash
mysqldump -u root -p --databases second_hand_trade \
  --add-drop-database --routines --triggers \
  > x组-数据库备份文件/second_hand_trade.sql
```

也可在 Navicat 中右键数据库 → 转储 SQL 文件 → 结构和数据。
