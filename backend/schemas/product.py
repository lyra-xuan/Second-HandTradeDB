from datetime import datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field

from schemas import ResponseOut

TitleStr = Annotated[str, Field(..., min_length=1, max_length=100, description="商品标题")]
PriceValue = Annotated[Decimal, Field(..., gt=0, le=99999.99, description="价格（元）")]


class ProductCreateIn(BaseModel):
    title: TitleStr
    description: str | None = Field(default=None, max_length=2000)
    price: PriceValue
    category_id: int = Field(..., gt=0)
    condition_id: int = Field(..., gt=0)
    place_id: int | None = Field(default=None, gt=0)
    images: list[str] = Field(default_factory=list, max_length=9, description="图片 URL 列表")


class ProductCreateOut(ResponseOut):
    id: int


class ProductUpdateIn(BaseModel):
    """发布者编辑商品；只允许改字段，不涉及 status（下架走单独接口）。"""
    title: TitleStr | None = None
    description: str | None = Field(default=None, max_length=2000)
    price: PriceValue | None = None
    category_id: int | None = Field(default=None, gt=0)
    condition_id: int | None = Field(default=None, gt=0)
    place_id: int | None = Field(default=None, gt=0)
    images: list[str] | None = Field(default=None, max_length=9)


class ProductListItem(BaseModel):
    id: int
    title: str
    price: Decimal
    status: int
    view_count: int
    created_at: datetime
    category_name: str
    condition_name: str
    place_name: str | None = None
    cover_image: str | None = None


class ProductListOut(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[ProductListItem]


class SellerBrief(BaseModel):
    id: int
    nickname: str
    avatar: str | None = None
    contact: str | None = None


class ProductDetail(BaseModel):
    id: int
    title: str
    description: str | None = None
    price: Decimal
    status: int
    view_count: int
    created_at: datetime
    updated_at: datetime
    seller: SellerBrief
    category_name: str
    condition_name: str
    place_name: str | None = None
    images: list[str] = Field(default_factory=list)
    is_favorite: bool = False
