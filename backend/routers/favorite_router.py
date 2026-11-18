from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from dependencies import get_session, get_current_user
from models import AsyncSession
from models.user import User
from repository.favorite_repo import FavoriteRepository
from repository.product_repo import ProductRepository
from schemas import ResponseOut
from schemas.product import ProductListItem

router = APIRouter(prefix='/favorites', tags=['收藏'])


@router.get('', response_model=list[ProductListItem])
async def list_favorites(
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    rows = await FavoriteRepository(session=session).list_rows(user.id)
    return [ProductListItem(**row._mapping) for row in rows]


@router.post('/{product_id}', response_model=ResponseOut)
async def add_favorite(
    product_id: int,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    repo = FavoriteRepository(session=session)
    product = await ProductRepository(session=session).get_by_id(product_id)
    if product is None:
        raise HTTPException(404, detail="商品不存在！")
    if await repo.is_exist(user.id, product_id):
        return ResponseOut()
    await repo.add(user.id, product_id)
    return ResponseOut()


@router.delete('/{product_id}', response_model=ResponseOut)
async def remove_favorite(
    product_id: int,
    user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    await FavoriteRepository(session=session).remove(user.id, product_id)
    return ResponseOut()
