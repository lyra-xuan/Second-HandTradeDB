# 校园二手交易平台前端

Vue 3 + Vite + Vue Router，JavaScript 单文件组件。调用现有 FastAPI API，不包含模拟交易数据。使用 hash 路由，刷新子页面无需服务器 SPA 回退配置。

## 启动

在本目录执行（已验证的本地 Node 版本为 22.23.3）：

```powershell
npm.cmd ci
npm.cmd run dev
```

访问终端输出的 http://127.0.0.1:5173。默认代理 `/api` 和 `/static` 到 `http://127.0.0.1:8000`。
后端须先导入 database/schema.sql、triggers.sql、seed_data.sql，配置 backend/.env 并安装 requirements.txt，然后从 backend 目录运行 `python -m uvicorn main:app --reload --port 8000`。数据库和后端由对应负责人配置；不要在共享数据库上随意重置或重复导入种子数据。

要连接同学的后端，复制 `.env.example` 为 `.env.local`，修改 `API_PROXY_TARGET` 后重启 Vite。不要提交 `.env.local`。浏览器端不能配置数据库密码。

```powershell
npm.cmd test
npm.cmd run build
```

构建产物为 dist/。正式部署需要服务器将 `/api` 与 `/static` 反向代理至后端，或在构建时设置 VITE_API_BASE 并配置后端 CORS；Vite 开发代理不属于生产产物。

## 页面和模块

- src/api.js：统一请求、超时、错误格式、token；token 存在 sessionStorage，同一标签页刷新保留，关闭标签页后结束。
- src/main.js：路由与登录校验。
- src/domain.js：状态字典、金额显示、交易按钮权限、图片 URL 校验。
- src/views/：登录注册、商品列表/详情/发布/编辑、订单、资料、统计。
- src/components/ProductCard.vue：商品卡片与图片失败占位。
- src/style.css：桌面与移动端布局。

## 与后端的衔接事项

1. 分类、成色、交易地点分别通过 `/api/categories`、`/api/conditions`、`/api/places` 加载，使用接口返回的 ID 和名称。
2. 编辑商品直接使用详情返回的分类、成色、地点 ID 回填。交易地点可留空。
3. 暂无上传 API，发布页接受最多 9 个图片地址。种子图片是占位路径，未提供真实文件时显示无图占位。
4. 商品下架使用 delist，收藏移除使用 DELETE。未虚构商品删除接口；课程删除要求需团队确认。
5. 完成订单按当前后端规则：已确认订单的买家或卖家任一方可完成，不是双方分别确认。
6. 统计仅显示现有 overview/categories 的真实数据。趋势、排名、用户封禁待后端开放接口再增加界面。
7. 若空数据库 overview 报错，检查后端 finish_rate 对 NULL 的处理。后端错误不会转换成假数据。
8. 前端按钮和路由控制仅用于体验，最终权限必须由后端验证。

## 联调验收

- 注册新学号；检查重复学号、邮箱格式、两次密码不一致；登录后刷新；退出后访问业务页。
- 未启动后端时应显示错误，恢复后能重试；过期 token 应返回登录。
- 搜索、分类和分页；空结果；错误图片占位；我的发布显示所有状态。
- 账号 A 发布商品并编辑；账号 B 收藏、取消收藏、预订；A 确认；B 完成；检查状态和统计。
- 使用另一笔订单检查取消后商品恢复在售；已结束订单不应显示操作按钮。
- 检查本人不能购买本人商品，普通用户不能操作其他人的商品。
- 修改资料刷新后保留；检查桌面和手机宽度。

## GitHub 提交

先完成真实联调，再从仓库根目录检查 `git diff`、`git status`，只添加 frontend/，提交并推送当前功能分支。创建 PR 时 base 选 dev，由至少一位同学审查。此次前端包含多个业务页面，PR 描述应列出上述未接入能力和实际验证结果。
