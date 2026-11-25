"""主链路冒烟测试：注册 → 登录 → 发布 → 收藏 → 下单 → 确认 → 完成 → 统计。

运行方式（在 backend 目录下）：
    .\\.venv\\Scripts\\python.exe -m pytest tests -v

说明：
- 通过 httpx.ASGITransport 在进程内调用真实 app + 真实 MySQL，不 mock 数据库，
  因此会写入一条测试用户/商品/订单数据（项目无删除接口，数据会保留）。
- 每个断言检查业务结果而非仅 HTTP 200，可同时验证触发器状态流转与鉴权边界。
- 全程共用一个事件循环（避免 Windows 下 aiomysql 连接跨 loop），结束时释放连接池。
- 依赖 backend/.env 的数据库配置；运行前请确保已导入 schema/triggers/seed.sql。
"""
import time

import httpx
import pytest
from httpx import ASGITransport

from main import app
from models import engine


@pytest.fixture
def anyio_backend():
    return "asyncio"


def _unique(tag: str) -> str:
    """生成唯一学号，保证脚本可重复运行。"""
    return f"t{int(time.time() * 1000) % 10 ** 11}{tag}"


@pytest.mark.anyio
async def test_smoke_main_chain():
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:

        # --- 第 1、2 步：注册并登录两个用户（卖家 / 买家）---
        async def register_and_login(tag: str) -> dict:
            student_no = _unique(tag)
            resp = await client.post("/api/auth/register", json={
                "student_no": student_no,
                "email": f"{student_no}@stu.edu.cn",
                "nickname": f"测试{tag}",
                "password": "123456",
                "confirm_password": "123456",
            })
            assert resp.status_code == 200, resp.text
            assert resp.json()["result"] == "success"
            resp = await client.post("/api/auth/login",
                                     json={"student_no": student_no, "password": "123456"})
            assert resp.status_code == 200, resp.text
            return {"Authorization": f"Bearer {resp.json()['token']}"}

        seller = await register_and_login("a")
        buyer = await register_and_login("b")

        # 未登录访问受保护接口应 401
        assert (await client.get("/api/products")).status_code == 401
        assert (await client.get("/api/admin/logs")).status_code == 401

        # --- 第 3 步：卖家发布商品 ---
        resp = await client.post("/api/products", headers=seller, json={
            "title": "冒烟测试教材", "description": "用于主链路自测",
            "price": 39.9, "category_id": 1, "condition_id": 2, "images": [],
        })
        assert resp.status_code == 201, resp.text
        product_id = resp.json()["id"]

        # --- 第 4 步：买家收藏（幂等）---
        assert (await client.post(f"/api/favorites/{product_id}", headers=buyer)).status_code == 200
        favorites = (await client.get("/api/favorites", headers=buyer)).json()
        assert any(item["id"] == product_id for item in favorites)

        # --- 第 5 步：买家下单，触发器应把商品置为"已预订"(2) ---
        resp = await client.post("/api/orders", headers=buyer,
                                 json={"product_id": product_id, "contact": "QQ: 123456"})
        assert resp.status_code == 201, resp.text
        order_id = resp.json()["id"]
        detail = (await client.get(f"/api/products/{product_id}", headers=buyer)).json()
        assert detail["status"] == 2, "下单后商品应自动变为已预订"

        # 不允许购买自己发布的商品
        resp = await client.post("/api/orders", headers=seller, json={"product_id": product_id})
        assert resp.status_code == 400, resp.text

        # --- 第 6 步：卖家确认 ---
        assert (await client.post(f"/api/orders/{order_id}/confirm", headers=seller)).status_code == 200
        order = (await client.get(f"/api/orders/{order_id}", headers=seller)).json()
        assert order["status"] == 2

        # --- 第 7 步：完成交易，触发器应把商品置为"已售出"(3) ---
        assert (await client.post(f"/api/orders/{order_id}/complete", headers=buyer)).status_code == 200
        order = (await client.get(f"/api/orders/{order_id}", headers=buyer)).json()
        assert order["status"] == 3 and order["finished_at"] is not None
        detail = (await client.get(f"/api/products/{product_id}", headers=buyer)).json()
        assert detail["status"] == 3, "订单完成后商品应自动变为已售出"

        # --- 第 8 步：统计与特色分析接口均可聚合 ---
        resp = await client.get("/api/stats/overview", headers=seller)
        assert resp.status_code == 200, resp.text
        overview = resp.json()
        assert overview["product_total"] > 0 and overview["order_finished"] > 0
        for path in ("/api/stats/categories", "/api/stats/price-range",
                     "/api/stats/trend?days=7", "/api/stats/ranking?limit=5",
                     "/api/stats/sellers?limit=5", "/api/stats/category-sales"):
            assert (await client.get(path, headers=seller)).status_code == 200, path

        # --- 管理员权限边界：普通用户访问管理员接口应 403 ---
        assert (await client.get("/api/admin/logs", headers=seller)).status_code == 403

    await engine.dispose()
