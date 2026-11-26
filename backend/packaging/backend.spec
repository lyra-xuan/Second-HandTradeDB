# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller 打包配置：校园二手交易平台后端（Windows onedir）。

用法（在 backend 目录下执行）：
    .\\.venv\\Scripts\\python.exe -m PyInstaller packaging/backend.spec --noconfirm --clean

产物：backend/dist/campus-market-backend/（内含 campus-market-backend.exe）。
说明：SQLAlchemy 方言、uvicorn 协议、pydantic 的 EmailStr 等都通过运行时动态
      导入，PyInstaller 静态分析抓不到，必须在 hiddenimports 中显式声明。
"""
import os

BACKEND_DIR = os.path.abspath(os.path.dirname(SPECPATH))

hiddenimports = [
    # uvicorn 运行时按字符串动态加载的协议/循环实现
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    # 数据库驱动：SQLAlchemy 通过字符串加载方言模块
    'sqlalchemy.dialects.mysql.aiomysql',
    'aiomysql',
    'pymysql',
    # 其余运行时动态导入的依赖
    'email_validator',   # pydantic EmailStr
    'pwdlib',            # 密码哈希
    'argon2',
    'dotenv',
    'jwt',
]

a = Analysis(
    [os.path.join(BACKEND_DIR, 'run.py')],
    pathex=[BACKEND_DIR],
    binaries=[],
    datas=[],
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=['tkinter', 'pytest'],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='campus-market-backend',
    debug=False,
    strip=False,
    upx=False,
    console=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name='campus-market-backend',
)
