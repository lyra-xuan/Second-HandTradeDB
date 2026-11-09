# 协作规范

本项目为数据库系统课程设计，采用 Next.js + FastAPI + PostgreSQL 技术栈。多人协作期间，所有代码变更均通过分支与 Pull Request 流转，`main` 分支始终保持可运行状态。

## 分支模型

| 分支 | 用途 | 生命周期 |
| --- | --- | --- |
| `main` | 稳定分支，只保存可运行、可演示的版本 | 长期 |
| `dev` | 集成分支，日常开发的汇合点 | 长期 |
| `feat/<描述>` | 功能开发，从 `dev` 切出 | 功能完成后删除 |
| `fix/<描述>` | 缺陷修复，从 `dev` 切出 | 修复完成后删除 |
| `chore/<描述>` | 构建、依赖、配置等杂项改动 | 完成后删除 |

分支命名使用小写英文与连字符，例如 `feat/user-auth`、`fix/order-list-pagination`。

## 工作流程

```bash
# 1. 同步最新的集成分支
git switch dev
git pull

# 2. 从 dev 切出功能分支
git switch -c feat/user-auth

# 3. 开发并提交
git add <具体文件>
git commit -m "feat: 实现用户注册接口"

# 4. 推送到远程
git push -u origin feat/user-auth
```

推送后在 GitHub 对 `dev` 分支发起 Pull Request。**合并前必须由至少一名组员完成 Review**，确认代码可运行后再合并。

功能分支存活时间应尽量短。合并前若 `dev` 已有新提交，需先同步：

```bash
git switch dev
git pull
git switch feat/user-auth
git merge dev
```

## 提交信息规范

格式：`<type>: <描述>`，其中 `type` 取值如下。

| type | 含义 |
| --- | --- |
| `feat` | 新增功能 |
| `fix` | 缺陷修复 |
| `docs` | 文档改动 |
| `style` | 不影响逻辑的格式调整 |
| `refactor` | 重构，不改变外部行为 |
| `test` | 测试相关 |
| `chore` | 构建、依赖、配置等杂项 |

示例：

```text
feat: 新增商品发布与图片上传
fix: 修复登录 token 过期后未跳转的问题
docs: 补充数据库表结构说明
```

描述部分说明「为什么做这个改动」，避免出现「修改代码」「更新文件」这类无信息量的表述。

## 禁止提交的内容

- `.env`、`.env.local` 等环境变量文件，以及任何 API Key、数据库密码
- 依赖与缓存目录：`node_modules/`、`.venv/`、`__pycache__/`、`.next/`
- 本地数据库文件与数据导出：`*.db`、`*.sqlite3`、`*.dump`、`*.sql.bak`

以上内容已在 `.gitignore` 中排除。若不慎提交了密钥，须立即更换密钥，并同步清理提交历史。

## 数据库改动约定

- `schema.sql` 与迁移脚本是团队共享的唯一真源，修改前须先在群内同步，避免多人并行改动同一张表
- 本地数据库各自重建，任何人不提交本地数据
- 表结构变更应与对应的 `feat:` 或 `chore:` 提交一同提交，并在 Pull Request 描述中注明

## 模块分工建议

按模块划分职责可显著降低冲突概率：

- 后端接口（FastAPI 路由、业务逻辑）
- 前端页面（Next.js 页面与组件）
- 数据库（表结构、迁移脚本、查询语句）

尽量避免两人同时修改同一文件。确需并行修改时，先在群内说明改动范围。

## 常用命令

```bash
git status                # 查看当前改动
git switch dev            # 切换到集成分支
git switch -c feat/xxx    # 新建并切换功能分支
git log --oneline -10     # 查看最近提交
git pull                  # 拉取远程更新
git push                  # 推送当前分支
gitk                      # 以图形界面查看提交历史
```
