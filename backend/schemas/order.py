from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from schemas import ResponseOut


class OrderCreateOut(ResponseOut):
    id: int


class OrderCreateIn(BaseModel):
    product_id: int = Field(..., gt=0)
    place_id: int | None = Field(default=None, gt=0)
    contact: str | None = Field(default=None, max_length=100, description="买家联系方式快照")


class OrderOut(BaseModel):
    id: int
    product_id: int
    product_title: str
    product_price: Decimal
    buyer_id: int
    seller_id: int
    buyer_nickname: str
    seller_nickname: str
    place_id: int | None = None
    contact: str | None = None
    status: int
    created_at: datetime
    finished_at: datetime | None = None
