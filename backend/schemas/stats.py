from decimal import Decimal

from pydantic import BaseModel


class OverviewOut(BaseModel):
    user_count: int
    product_total: int
    product_on_sale: int
    order_finished: int
    trade_amount: Decimal
    finish_rate: str


class CategoryStatItem(BaseModel):
    category_id: int
    category_name: str
    on_sale_count: int


class CategoryStatsOut(BaseModel):
    items: list[CategoryStatItem]
