from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Budget, Category, Expense


class StatsRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_breakdown(self, user_id: int, month_start: datetime, month_end: datetime):
        stmt = (
            select(
                Category.id,
                Category.name,
                Category.type,
                func.coalesce(func.sum(Expense.amount), 0).label("total"),
            )
            .join(Expense, Expense.category_id == Category.id)
            .where(
                Expense.user_id == user_id,
                Expense.spent_at >= month_start,
                Expense.spent_at < month_end,
            )
            .group_by(Category.id, Category.name, Category.type)
            .order_by(Category.type.asc(), Category.name.asc())
        )
        result = await self.db.execute(stmt)
        return result.all()

    async def get_budget_vs_actual(self, user_id: int, month: str, month_start: datetime, month_end: datetime):
        spent_subquery = (
            select(Expense.category_id, func.coalesce(func.sum(Expense.amount), 0).label("actual_amount"))
            .join(Category, Expense.category_id == Category.id)
            .where(
                Expense.user_id == user_id,
                Expense.spent_at >= month_start,
                Expense.spent_at < month_end,
                Category.type == "expense",
            )
            .group_by(Expense.category_id)
            .subquery()
        )

        stmt = (
            select(
                Budget.category_id,
                Category.name,
                Budget.limit_amount,
                func.coalesce(spent_subquery.c.actual_amount, 0).label("actual_amount"),
            )
            .join(Category, Budget.category_id == Category.id)
            .outerjoin(spent_subquery, spent_subquery.c.category_id == Budget.category_id)
            .where(Budget.user_id == user_id, Budget.month == month)
            .order_by(Category.name.asc())
        )
        result = await self.db.execute(stmt)
        return result.all()
