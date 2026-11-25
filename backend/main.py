from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.exc import IntegrityError

from models import AsyncSessionFactory

from routers.auth_router import router as auth_router
from routers.dict_router import router as dict_router
from routers.product_router import router as product_router
from routers.order_router import router as order_router
from routers.favorite_router import router as favorite_router
from routers.stats_router import router as stats_router
from routers.admin_router import router as admin_router
from routers.upload_router import router as upload_router

class DBSessionMiddleware(BaseHTTPMiddleware):
    """每个请求一个 Session，并把事务提交提前到响应发出之前。

    FastAPI 的 yield 依赖是在响应发出后才清理的，会导致「写完后立刻查」
    读到旧状态；这里改成中间件里显式 commit/rollback，解决前后端联调竞态。
    """

    async def dispatch(self, request: Request, call_next):
        session = AsyncSessionFactory()
        request.state.db_session = session
        try:
            response = await call_next(request)
            if response.status_code < 400:
                try:
                    await session.commit()
                except IntegrityError:
                    await session.rollback()
                    return JSONResponse(
                        status_code=400,
                        content={"detail": "数据违反完整性约束（如重复数据或无效关联）！"},
                    )
            else:
                await session.rollback()
            return response
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


app = FastAPI(title="校园二手交易平台 API")

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    """唯一键/外键/CHECK 冲突统一转 400，避免数据库错误冒泡成 500。"""
    return JSONResponse(
        status_code=400,
        content={"detail": "数据违反完整性约束（如重复数据或无效关联）！"},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(DBSessionMiddleware)

API_PREFIX = "/api"
app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(dict_router, prefix=API_PREFIX)
app.include_router(product_router, prefix=API_PREFIX)
app.include_router(order_router, prefix=API_PREFIX)
app.include_router(favorite_router, prefix=API_PREFIX)
app.include_router(stats_router, prefix=API_PREFIX)
app.include_router(admin_router, prefix=API_PREFIX)
app.include_router(upload_router, prefix=API_PREFIX)

# 图片等静态资源：与前端开发代理 /static 对齐，上传接口返回的 URL 即可直接访问
STATIC_DIR = Path(__file__).resolve().parent / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def root():
    return {"message": "校园二手交易平台 API 已启动，接口前缀为 /api"}
