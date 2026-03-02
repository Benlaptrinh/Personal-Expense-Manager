from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.core.responses import success_response
from app.models import User
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.services.category_service import CategoryService

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get("", summary="List categories")
async def list_categories(
    user_id: int | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items = await CategoryService(db).list_categories(current_user, user_id)
    return success_response([CategoryRead.model_validate(item).model_dump(mode="json") for item in items])


@router.post("", summary="Create category")
async def create_category(
    payload: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    item = await CategoryService(db).create_category(current_user, payload)
    return success_response(CategoryRead.model_validate(item).model_dump(mode="json"))


@router.patch("/{category_id}", summary="Update category")
async def update_category(
    category_id: int,
    payload: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    item = await CategoryService(db).update_category(current_user, category_id, payload)
    return success_response(CategoryRead.model_validate(item).model_dump(mode="json"))


@router.delete("/{category_id}", summary="Delete category")
async def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await CategoryService(db).delete_category(current_user, category_id)
    return success_response({"deleted": True})
