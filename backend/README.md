# 校园二手交易平台 - 后端

FastAPI + SQLAlchemy 2.0（async）+ aiomysql 实现的校园二手交易平台后端。所有接口统一挂在 `/api` 前缀下，数据库使用 MySQL 8.0，库名 `second_hand_trade`。

接口文档：启动后访问 `http://127.0.0.1:8000/docs`（Swagger UI）或 `/redoc`。

## 技术栈

| 组件 | 选型 |
| --- | --- |
| Web 框架 | FastAPI 0.141 |
| ORM | SQLAlchemy 2.0（`Mapped` 声明式 + async） |
| 数据库驱动 | aiomysql / PyMySQL |
| 鉴权 | PyJWT（HS256，无状态 Token） |
| 密码哈希 | pwdlib + Argon2（`argon2-cffi`） |
| 配置 | python-dotenv（`.env`） |

## 目录结构

```
backend/
├── main.py          # 应用入口：中间件、CORS、异常处理、路由注册
├── run.py           # 可执行文件打包入口（uvicorn 启动）
├── settings/        # 读取 .env，导出 DB_URI / JWT 配置
├── core/auth.py     # AuthHandler：Token 签发与校验（单例）
├── dependencies.py  # 通用依赖：get_session / get_current_user / get_admin_user
├── models/          # SQLAlchemy ORM 模型（users、products、orders…）
├── schemas/         # Pydantic 请求/响应模型
├── repository/      # 数据访问层（每张表/聚合一个 Repository）
├── routers/         # 路由层（auth / dict / product / order / favorite / stats / admin / upload）
├── static/          # 静态资源根目录，uploads/ 存放上传的图片（运行期生成，不提交）
├── tests/           # 主链路冒烟测试（pytest）
└── packaging/       # 打包配置（PyInstaller spec + 构建脚本）
```

## 快速启动

前置：已安装 Python 3.12+ 与 MySQL 8.0，并在 MySQL 中按顺序导入 `database/` 下的脚本。

```sql
-- 在 MySQL 客户端按顺序执行（一次即可）
SOURCE database/schema.sql;    -- 建库建表 + 索引 + 约束
SOURCE database/triggers.sql;  -- 4 个触发器（状态一致性 + 审计）
SOURCE database/seed_data.sql; -- 测试数据（所有用户密码均为 123456）
```

配置环境变量：复制 `.env.example` 为 `.env`，填入真实数据库密码与 JWT 密钥。

```powershell
cd backend
# 1. 创建虚拟环境并安装依赖
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
# 2. 启动服务
.\.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000
```

服务地址 `http://127.0.0.1:8000`，前端开发服务器默认把 `/api`、`/static` 代理到这里。

## 分层与请求流程

```
HTTP → DBSessionMiddleware → 路由函数 → 依赖注入(get_current_user) → Repository → ORM → MySQL
```

- **路由层**：只做参数校验、权限判断、组装响应，不写 SQL。
- **Repository 层**：封装所有数据访问；写操作用 `flush()` 不自行 `commit()`。
- **事务边界**：由 [DBSessionMiddleware](file:///e:/work_space/二手交易平台/backend/main.py) 统一管理。响应状态码 < 400 时在响应发出前 `commit`，否则 `rollback`。这样"发布商品后立刻查询""下单后立刻看订单状态"都能读到最新数据，避免 FastAPI `yield` 依赖在响应后才清理导致的读写竞态。
- **鉴权**：`get_current_user` 校验 Token 并拦截封禁用户（`status=0` → 403）；`get_admin_user` 在其基础上要求 `is_admin`。

## 接口清单

统一前缀 `/api`。除标注"公开"外其余接口均需 `Authorization: Bearer <token>`。

### 认证 `/api/auth`

| 方法 | 路径 | 权限 | 说明 |
| --- | --- | --- | --- |
| POST | `/auth/register` | 公开 | 注册（学号/邮箱唯一，两次密码需一致） |
| POST | `/auth/login` | 公开 | 登录，返回 `{user, token}`；封禁用户返回 403 |
| GET | `/auth/me` | 登录 | 当前用户信息 |
| PATCH | `/auth/me` | 登录 | 改昵称/头像/联系方式（学号、邮箱、密码不可改） |
| POST | `/auth/logout` | 登录 | 无状态登出，前端清除本地 Token |

### 字典 `/api`

| 方法 | 路径 | 权限 | 说明 |
| --- | --- | --- | --- |
| GET | `/categories` | 登录 | 分类列表 `{id, name, sort_order}` |
| GET | `/conditions` | 登录 | 成色列表 |
| GET | `/places` | 登录 | 交易地点列表 |

### 商品 `/api/products`

| 方法 | 路径 | 权限 | 说明 |
| --- | --- | --- | --- |
| POST | `/products` | 登录 | 发布商品，返回 `{result, id}`（201） |
| GET | `/products` | 登录 | 列表：仅"在售"，支持 `category_id` / `keyword` / 分页 |
| GET | `/products/mine` | 登录 | 我的发布（含全部状态） |
| GET | `/products/{id}` | 登录 | 详情，含卖家信息、图片、`category_id/condition_id/place_id` 回填字段；每次浏览 `view_count +1` |
| PUT | `/products/{id}` | 发布者 | 编辑商品（已下架不可编辑） |
| POST | `/products/{id}/delist` | 发布者或管理员 | 下架（`status=4`） |
| POST | `/products/{id}/reshelf` | 管理员 | 重新上架（仅 `4 → 1`） |

### 订单 `/api/orders`

| 方法 | 路径 | 权限 | 说明 |
| --- | --- | --- | --- |
| POST | `/orders` | 登录 | 下单，返回 `{result, id}`（201） |
| GET | `/orders?role=buyer\|seller` | 登录 | 我的订单，买家/卖家视角 |
| GET | `/orders/{id}` | 交易双方 | 订单详情 |
| POST | `/orders/{id}/confirm` | 卖家 | 待确认 → 已确认 |
| POST | `/orders/{id}/complete` | 买家或卖家 | 已确认 → 已完成 |
| POST | `/orders/{id}/cancel` | 交易双方 | 待确认/已确认 → 已取消 |

### 收藏 `/api/favorites`

| 方法 | 路径 | 权限 | 说明 |
| --- | --- | --- | --- |
| GET | `/favorites` | 登录 | 我的收藏（商品列表项结构） |
| POST | `/favorites/{product_id}` | 登录 | 收藏（幂等） |
| DELETE | `/favorites/{product_id}` | 登录 | 取消收藏 |

### 统计与特色分析 `/api/stats`（均需登录）

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/stats/overview` | D1 概览：用户数/商品总数/在售数/成交量/成交额/成交率 |
| GET | `/stats/categories` | D2 各分类在售商品数（含空分类） |
| GET | `/stats/price-range` | D3 价格区间分布（五档，固定顺序） |
| GET | `/stats/trend?days=30` | D4 近 N 天发布与成交趋势（1~90，缺数据补 0） |
| GET | `/stats/ranking?limit=10` | D5 热门商品 Top N（浏览量为主、收藏量为辅） |
| GET | `/stats/sellers?limit=5` | 加分项 1 活跃卖家排行（1~20） |
| GET | `/stats/category-sales` | 加分项 2 各分类成交金额与均价 |

### 管理员 `/api/admin`（均需管理员）

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| PATCH | `/admin/users/{user_id}/status` | 封禁(0)/解封(1)用户 |
| GET | `/admin/logs?page=1&page_size=20` | 操作日志分页查询（按时间倒序） |

### 图片上传 `/api/uploads`（登录）

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/uploads` | 多图上传（`multipart/form-data`，字段名 `files`，最多 9 张、单张 ≤5MB，仅 jpg/png/webp/gif）；返回 `{result, urls}`（201） |

上传成功返回的 `urls`（形如 `/static/uploads/xxx.png`）直接填入发布/编辑商品的 `images` 字段即可；图片通过 `/static` 静态目录对外访问。

## 关键技术实现（报告第六章素材）

1. **三层架构解耦**：`routers → repository → models`。路由层无 SQL，Repository 无 HTTP 概念，便于单独测试与替换。
2. **统一事务边界**：自定义 `DBSessionMiddleware` 在响应发出前提交事务，解决异步 ORM 下"写后即读"的可见性问题；异常时回滚，配合 `IntegrityError` 全局处理器把完整性约束冲突统一转 400。
3. **状态一致性交给数据库触发器**：商品状态（在售/已预订/已售出）与订单状态的联动由 `trg_orders_bi_check / ai_reserve / au_sync` 三个触发器维护，后端只 `INSERT 订单` 与 `UPDATE 订单状态`，从数据库层面保证"下单、取消、完成"涉及两张表的原子性。
4. **审计日志由触发器兜底**：`trg_users_au_log` 在 `users.status` 变化时自动写入 `admin_logs`（`action='auto_user_status'`），后端封禁/解封接口只改状态、不重复写日志，避免双写不一致。
5. **统计口径与数据库一致**：5 个统计查询直接以 `text()` 执行与 `database/stats_queries.sql` 同字段同口径的 SQL，不拆成 ORM 重写，保证"接口返回 = 报告数值 = 数据库直查"三方一致。
6. **鉴权分层**：`get_current_user` 统一处理 401 与封禁 403；`get_admin_user` 复用前者再做管理员校验，权限判断集中在依赖而非散落各接口。

## 前端对接说明（新增接口，待前端接入界面）

前端 [Stats.vue](file:///e:/work_space/二手交易平台/frontend/src/views/Stats.vue) 目前只用了 `/stats/overview` 与 `/stats/categories`。以下接口已就绪，可按需增加图表：

| 建议界面 | 接口 | 关键响应字段 |
| --- | --- | --- |
| 价格区间柱状图 | `GET /stats/price-range` | `items[].price_range` / `items[].product_count` |
| 发布/成交折线图 | `GET /stats/trend?days=30` | `days` / `items[].stat_date`、`new_products`、`finished_orders` |
| 热门商品榜 | `GET /stats/ranking?limit=10` | `product_id` / `title` / `price` / `view_count` / `favorite_count` |
| 活跃卖家榜 | `GET /stats/sellers?limit=5` | `seller_id` / `nickname` / `on_sale_count` / `total_views` / `finished_orders` |
| 分类成交分析 | `GET /stats/category-sales` | `category_name` / `deal_count` / `total_amount` / `avg_price` |
| 管理员后台 | `PATCH /admin/users/{id}/status`、`GET /admin/logs` | 封禁/解封、操作日志分页 |
| 发布/编辑商品传图 | `POST /uploads` | `urls[]`（填入 `images`，形如 `/static/uploads/xxx.png`） |

金额字段为字符串化的 `Decimal`，展示前请用前端 `money()` 格式化。

## 验收与测试

- 交互式验证：启动后访问 `/docs` 直接调用各接口。
- 主链路冒烟测试（注册 → 登录 → 发布 → 收藏 → 下单 → 确认 → 完成 → 统计）：

```powershell
.\.venv\Scripts\python.exe -m pip install pytest httpx   # 仅首次需要
.\.venv\Scripts\python.exe -m pytest tests -v
```

该测试进程内调用真实 app 与真实 MySQL，并断言触发器状态流转（下单后商品变已预订、完成后变已售出）与鉴权边界；因项目无删除接口，会在数据库留下一条测试用户/商品/订单数据。

## 打包为可执行文件（EXE）

换电脑演示时无需安装 Python，只需「exe 目录 + `.env`」即可运行。

```powershell
cd backend
.\.venv\Scripts\python.exe -m pip install pyinstaller   # 仅首次需要
.\packaging\build.ps1                                    # 产物：dist\campus-market-backend\
```

产物说明与部署步骤：

1. `dist\campus-market-backend\` 是整个可运行目录（内含 `campus-market-backend.exe` 与 `_internal\`），需整体拷贝。
2. 在目录内把 `.env.example` 复制为 `.env`，填入目标机器的数据库连接与 JWT 密钥。
3. 双击 `campus-market-backend.exe` 启动，默认监听 `http://127.0.0.1:8000`；端口被占用时用环境变量覆盖：

```powershell
$env:PORT="8020"; .\campus-market-backend.exe
```

打包配置见 [backend.spec](file:///e:/work_space/二手交易平台/backend/packaging/backend.spec)：SQLAlchemy 方言、uvicorn 协议、pydantic 的 `EmailStr` 均为运行时动态导入，已在 `hiddenimports` 中显式声明；`dist/`、`build/` 已在 `.gitignore` 中忽略，不提交二进制。
