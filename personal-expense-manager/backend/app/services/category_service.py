from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, UserRole
from app.repositories.category_repository import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = CategoryRepository(db)

    async def list_categories(self, current_user: User, user_id: int | None = None):
        if current_user.role == UserRole.ADMIN and user_id is None:
            return await self.repo.list_all()
        target_user_id = user_id if current_user.role == UserRole.ADMIN and user_id is not None else current_user.id
        return await self.repo.list_for_user(target_user_id)

    async def create_category(self, current_user: User, payload: CategoryCreate):
        category = await self.repo.create(current_user.id, payload.name, payload.type)
        await self.db.commit()
        return category

    async def update_category(self, current_user: User, category_id: int, payload: CategoryUpdate):
        category = await self.repo.get_by_id(category_id)
        if category is None:
            raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Category not found"})

        if current_user.role != UserRole.ADMIN and category.user_id != current_user.id:
            raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Access denied"})

        if payload.name is not None:
            category.name = payload.name
        if payload.type is not None:
            category.type = payload.type

        await self.db.commit()
        await self.db.refresh(category)
        return category

    async def delete_category(self, current_user: User, category_id: int):
        category = await self.repo.get_by_id(category_id)
        if category is None:
            raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Category not found"})

        if current_user.role != UserRole.ADMIN and category.user_id != current_user.id:
            raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Access denied"})

        await self.db.delete(category)
        await self.db.commit()
