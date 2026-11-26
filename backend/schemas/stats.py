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


class PriceRangeItem(BaseModel):
    price_range: str
    product_count: int


class PriceRangeOut(BaseModel):
    items: list[PriceRangeItem]


class TrendItem(BaseModel):
    stat_date: str
    new_products: int
    finished_orders: int


class TrendOut(BaseModel):
    days: int
    items: list[TrendItem]


class RankingItem(BaseModel):
    product_id: int
    title: str
    price: Decimal
    view_count: int
    favorite_count: int


class RankingOut(BaseModel):
    items: list[RankingItem]


class SellerRankItem(BaseModel):
    seller_id: int
    nickname: str
    on_sale_count: int
    total_views: int
    finished_orders: int


class SellerRankOut(BaseModel):
    items: list[SellerRankItem]


class CategorySalesItem(BaseModel):
    category_name: str
    deal_count: int
    total_amount: Decimal
    avg_price: Decimal


class CategorySalesOut(BaseModel):
    items: list[CategorySalesItem]
