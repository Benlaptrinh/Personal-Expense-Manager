from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import cache_delete
from app.models import User, UserRole
from app.repositories.budget_repository import BudgetRepository
from app.repositories.category_repository import CategoryRepository
from app.schemas.budget import BudgetUpsert


class BudgetService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.budget_repo = BudgetRepository(db)
        self.category_repo = CategoryRepository(db)

    async def list_budgets(self, current_user: User, month: str, user_id: int | None = None):
        target_user = current_user.id
        if current_user.role == UserRole.ADMIN and user_id is not None:
            target_user = user_id
        return await self.budget_repo.list_for_user_month(target_user, month)

    async def upsert_budget(self, current_user: User, category_id: int, month: str, payload: BudgetUpsert):
        category = await self.category_repo.get_for_user(category_id, current_user.id)
        if category is None:
            raise HTTPException(status_code=404, detail={"code": "CATEGORY_NOT_FOUND", "message": "Category not found"})

        budget = await self.budget_repo.upsert(
            user_id=current_user.id,
            category_id=category_id,
            month=month,
            limit_amount=payload.limit_amount,
        )
        await self.db.commit()
        await cache_delete(f"stats:{current_user.id}:{month}")
        budgets = await self.budget_repo.list_for_user_month(current_user.id, month)
        for item in budgets:
            if item.category_id == category_id:
                return item
        return budget
