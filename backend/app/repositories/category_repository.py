from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Category


class CategoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_for_user(self, user_id: int) -> list[Category]:
        result = await self.db.execute(select(Category).where(Category.user_id == user_id).order_by(Category.name.asc()))
        return list(result.scalars().all())

    async def list_all(self) -> list[Category]:
        result = await self.db.execute(select(Category).order_by(Category.name.asc()))
        return list(result.scalars().all())

    async def get_for_user(self, category_id: int, user_id: int) -> Category | None:
        result = await self.db.execute(
            select(Category).where(Category.id == category_id, Category.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, category_id: int) -> Category | None:
        result = await self.db.execute(select(Category).where(Category.id == category_id))
        return result.scalar_one_or_none()

    async def create(self, user_id: int, name: str, category_type: str) -> Category:
        category = Category(user_id=user_id, name=name, type=category_type)
        self.db.add(category)
        await self.db.flush()
        await self.db.refresh(category)
        return category

    async def delete_for_user(self, category_id: int, user_id: int) -> bool:
        result = await self.db.execute(delete(Category).where(Category.id == category_id, Category.user_id == user_id))
        return result.rowcount > 0
