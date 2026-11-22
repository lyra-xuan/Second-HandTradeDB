from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from dependencies import get_session, get_current_user, get_admin_user
from models import AsyncSession
from models.product import Product
from models.user import User
from repository.product_repo import ProductRepository
from schemas import ResponseOut
from schemas.product import (
    ProductCreateIn, ProductCreateOut, ProductUpdateIn,
    ProductListOut, ProductListItem, ProductDetail, SellerBrief,
)

router = APIRouter(prefix='/products', tags=['商品'])


@router.post('', response_model=ProductCreateOut, status_code=201)
async def create_product(
    data: ProductCreateIn,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    repo = ProductRepository(session=session)
    product = await repo.create(seller_id=user.id, data=data)
    return ProductCreateOut(id=product.id)


@router.get('', response_model=ProductListOut)
async def list_products(
    category_id: int | None = Query(default=None, gt=0),
    keyword: str | None = Query(default=None, max_length=50),
    page: int = Query(default=1, gt=0),
    page_size: int = Query(default=12, gt=0, le=50),
    user: Annotated[User, Depends(get_current_user)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
):
    """商品列表：仅展示在售商品，按发布时间倒序，支持分类筛选与关键词检索。"""
    total, rows = await ProductRepository(session=session).list_products(
        category_id=category_id, keyword=keyword, page=page, page_size=page_size
    )
    return ProductListOut(
        total=total, page=page, page_size=page_size,
        items=[ProductListItem(**row._mapping) for row in rows],
    )


@router.get('/mine', response_model=ProductListOut)
async def list_my_products(
    page: int = Query(default=1, gt=0),
    page_size: int = Query(default=12, gt=0, le=50),
    user: Annotated[User, Depends(get_current_user)] = None,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
):
    """我的发布：包含全部状态，供 U4 使用。"""
    total, rows = await ProductRepository(session=session).list_products(
        page=page, page_size=page_size, only_on_sale=False, seller_id=user.id
    )
    return ProductListOut(
        total=total, page=page, page_size=page_size,
        items=[ProductListItem(**row._mapping) for row in rows],
    )


@router.get('/{product_id}', response_model=ProductDetail)
async def get_product(
    product_id: int,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """商品详情：图片、卖家信息、发布时间、浏览量；浏览一次浏览量 +1。"""
    stmt = (select(Product)
            .where(Product.id == product_id)
            .options(
                selectinload(Product.seller),
                selectinload(Product.category),
                selectinload(Product.condition_level),
                selectinload(Product.place),
                selectinload(Product.images),
            ))
    product = await session.scalar(stmt)
    if product is None:
        raise HTTPException(404, detail="商品不存在！")

    repo = ProductRepository(session=session)
    await repo.add_view(product)
    return ProductDetail(
        id=product.id,
        title=product.title,
        description=product.description,
        price=product.price,
        status=product.status,
        view_count=product.view_count,
        created_at=product.created_at,
        updated_at=product.updated_at,
        seller=SellerBrief(
            id=product.seller.id,
            nickname=product.seller.nickname,
            avatar=product.seller.avatar,
            contact=product.seller.contact,
        ),
        category_id=product.category_id,
        condition_id=product.condition_id,
        place_id=product.place_id,
        category_name=product.category.name,
        condition_name=product.condition_level.name,
        place_name=product.place.name if product.place else None,
        images=[image.url for image in sorted(product.images, key=lambda x: x.sort_order)],
        is_favorite=await repo.is_favorite(user.id, product_id),
    )


@router.put('/{product_id}', response_model=ResponseOut)
async def update_product(
    product_id: int,
    data: ProductUpdateIn,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    repo = ProductRepository(session=session)
    product = await repo.get_by_id(product_id)
    if product is None:
        raise HTTPException(404, detail="商品不存在！")
    if product.seller_id != user.id:
        raise HTTPException(403, detail="只能编辑自己发布的商品！")
    if product.status == 4:
        raise HTTPException(400, detail="已下架商品不可编辑！")
    await repo.update(product, data)
    return ResponseOut()


@router.post('/{product_id}/delist', response_model=ResponseOut)
async def delist_product(
    product_id: int,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """发布者或管理员下架：只写 status=4，不触碰触发器管理的 1/2/3。"""
    repo = ProductRepository(session=session)
    product = await repo.get_by_id(product_id)
    if product is None:
        raise HTTPException(404, detail="商品不存在！")
    if product.seller_id != user.id and not user.is_admin:
        raise HTTPException(403, detail="无权下架该商品！")
    if product.status == 4:
        raise HTTPException(400, detail="商品已下架！")
    await repo.delist(product)
    return ResponseOut()


@router.post('/{product_id}/reshelf', response_model=ResponseOut)
async def reshelf_product(
    product_id: int,
    admin: Annotated[User, Depends(get_admin_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """管理员重新上架：只做 4→1。"""
    repo = ProductRepository(session=session)
    product = await repo.get_by_id(product_id)
    if product is None:
        raise HTTPException(404, detail="商品不存在！")
    if product.status != 4:
        raise HTTPException(400, detail="只有已下架商品可以重新上架！")
    await repo.reshelf(product)
    return ResponseOut()
