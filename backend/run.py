"""可执行文件（EXE）打包入口：以 uvicorn 启动 FastAPI 应用。

开发时仍推荐从 backend 目录运行：
    python -m uvicorn main:app --reload --port 8000

本文件仅作为 PyInstaller 的统一入口（见 packaging/backend.spec）。
运行时会在 exe 所在目录查找 .env 读取数据库与 JWT 配置。
"""
import os

import uvicorn

from main import app

if __name__ == "__main__":
    # 端口可用环境变量覆盖（如 8000 被占用时：set PORT=8020）
    uvicorn.run(
        app,
        host=os.getenv("HOST", "127.0.0.1"),
        port=int(os.getenv("PORT", "8000")),
    )
