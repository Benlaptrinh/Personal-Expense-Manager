from datetime import datetime

from sqlalchemy import and_, delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models import Category, Expense


class ExpenseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        user_id: int,
        category_id: int,
        amount,
        currency: str,
        note: str | None,
        spent_at: datetime,
    ) -> Expense:
        expense = Expense(
            user_id=user_id,
            category_id=category_id,
            amount=amount,
            currency=currency.upper(),
            note=note,
            spent_at=spent_at,
        )
        self.db.add(expense)
        await self.db.flush()
        await self.db.refresh(expense)
        return expense

    async def get_for_user(self, expense_id: int, user_id: int) -> Expense | None:
        result = await self.db.execute(
            select(Expense)
            .options(joinedload(Expense.category))
            .where(Expense.id == expense_id, Expense.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, expense_id: int) -> Expense | None:
        result = await self.db.execute(select(Expense).options(joinedload(Expense.category)).where(Expense.id == expense_id))
        return result.scalar_one_or_none()

    async def delete_for_user(self, expense_id: int, user_id: int) -> bool:
        result = await self.db.execute(delete(Expense).where(Expense.id == expense_id, Expense.user_id == user_id))
        return result.rowcount > 0

    async def list_expenses(
        self,
        *,
        user_id: int | None,
        date_from: datetime | None,
        date_to: datetime | None,
        category_id: int | None,
        query: str | None,
        page: int,
        size: int,
    ) -> tuple[list[Expense], int]:
        filters = []
        if user_id is not None:
            filters.append(Expense.user_id == user_id)
        if date_from is not None:
            filters.append(Expense.spent_at >= date_from)
        if date_to is not None:
            filters.append(Expense.spent_at <= date_to)
        if category_id is not None:
            filters.append(Expense.category_id == category_id)
        if query:
            filters.append(or_(Expense.note.ilike(f"%{query}%"), Category.name.ilike(f"%{query}%")))

        base_stmt = (
            select(Expense)
            .join(Category, Expense.category_id == Category.id)
            .options(joinedload(Expense.category))
            .order_by(Expense.spent_at.desc(), Expense.id.desc())
        )
        if filters:
            base_stmt = base_stmt.where(and_(*filters))

        total_stmt = select(func.count(Expense.id)).join(Category, Expense.category_id == Category.id)
        if filters:
            total_stmt = total_stmt.where(and_(*filters))

        total_result = await self.db.execute(total_stmt)
        total = int(total_result.scalar_one())

        stmt = base_stmt.offset((page - 1) * size).limit(size)
        result = await self.db.execute(stmt)
        rows = list(result.unique().scalars().all())
        return rows, total

    async def totals_by_month(self, user_id: int, month_start: datetime, month_end: datetime) -> tuple[float, float]:
        stmt = (
            select(
                func.coalesce(
                    func.sum(
                        func.case((Category.type == "expense", Expense.amount), else_=0)
                    ),
                    0,
                ),
                func.coalesce(
                    func.sum(
                        func.case((Category.type == "income", Expense.amount), else_=0)
                    ),
                    0,
                ),
            )
            .join(Category, Expense.category_id == Category.id)
            .where(
                Expense.user_id == user_id,
                Expense.spent_at >= month_start,
                Expense.spent_at < month_end,
            )
        )
        result = await self.db.execute(stmt)
        spend, income = result.one()
        return float(spend), float(income)
