from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models import Budget


class BudgetRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_for_user(self, user_id: int, category_id: int, month: str) -> Budget | None:
        result = await self.db.execute(
            select(Budget).where(Budget.user_id == user_id, Budget.category_id == category_id, Budget.month == month)
        )
        return result.scalar_one_or_none()

    async def list_for_user_month(self, user_id: int, month: str) -> list[Budget]:
        result = await self.db.execute(
            select(Budget)
            .options(joinedload(Budget.category))
            .where(Budget.user_id == user_id, Budget.month == month)
            .order_by(Budget.category_id.asc())
        )
        return list(result.scalars().all())

    async def upsert(self, user_id: int, category_id: int, month: str, limit_amount) -> Budget:
        budget = await self.get_for_user(user_id, category_id, month)
        if budget is None:
            budget = Budget(user_id=user_id, category_id=category_id, month=month, limit_amount=limit_amount)
            self.db.add(budget)
        else:
            budget.limit_amount = limit_amount
        await self.db.flush()
        await self.db.refresh(budget)
        return budget
