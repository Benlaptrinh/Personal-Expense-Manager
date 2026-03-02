from datetime import datetime
import csv
import io

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import cache_delete
from app.models import User, UserRole
from app.repositories.category_repository import CategoryRepository
from app.repositories.expense_repository import ExpenseRepository
from app.schemas.expense import ExpenseCreate, ExpenseUpdate
from app.services.utils import datetime_to_month


class ExpenseService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.expense_repo = ExpenseRepository(db)
        self.category_repo = CategoryRepository(db)

    async def list_expenses(
        self,
        current_user: User,
        *,
        date_from: datetime | None,
        date_to: datetime | None,
        category_id: int | None,
        query: str | None,
        page: int,
        size: int,
        user_id: int | None = None,
    ):
        if size > 100:
            raise HTTPException(status_code=422, detail={"code": "INVALID_SIZE", "message": "size must be <= 100"})

        target_user_id = current_user.id
        if current_user.role == UserRole.ADMIN:
            target_user_id = user_id

        rows, total = await self.expense_repo.list_expenses(
            user_id=target_user_id,
            date_from=date_from,
            date_to=date_to,
            category_id=category_id,
            query=query,
            page=page,
            size=size,
        )

        return rows, total

    async def create_expense(self, current_user: User, payload: ExpenseCreate):
        category = await self.category_repo.get_for_user(payload.category_id, current_user.id)
        if category is None:
            raise HTTPException(status_code=404, detail={"code": "CATEGORY_NOT_FOUND", "message": "Category not found"})

        expense = await self.expense_repo.create(
            user_id=current_user.id,
            category_id=payload.category_id,
            amount=payload.amount,
            currency=payload.currency,
            note=payload.note,
            spent_at=payload.spent_at,
        )
        expense.category = category
        await self.db.commit()
        await self.invalidate_stats_cache(current_user.id, datetime_to_month(expense.spent_at))
        return await self.expense_repo.get_by_id(expense.id)

    async def update_expense(self, current_user: User, expense_id: int, payload: ExpenseUpdate):
        expense = await self.expense_repo.get_by_id(expense_id)
        if expense is None:
            raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Expense not found"})

        if current_user.role != UserRole.ADMIN and expense.user_id != current_user.id:
            raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Access denied"})

        old_month = datetime_to_month(expense.spent_at)

        if payload.category_id is not None:
            category = await self.category_repo.get_for_user(payload.category_id, expense.user_id)
            if category is None:
                raise HTTPException(status_code=404, detail={"code": "CATEGORY_NOT_FOUND", "message": "Category not found"})
            expense.category_id = payload.category_id
        if payload.amount is not None:
            expense.amount = payload.amount
        if payload.currency is not None:
            expense.currency = payload.currency.upper()
        if payload.note is not None:
            expense.note = payload.note
        if payload.spent_at is not None:
            expense.spent_at = payload.spent_at

        await self.db.commit()
        expense = await self.expense_repo.get_by_id(expense.id)

        await self.invalidate_stats_cache(expense.user_id, old_month)
        await self.invalidate_stats_cache(expense.user_id, datetime_to_month(expense.spent_at))
        return expense

    async def delete_expense(self, current_user: User, expense_id: int):
        expense = await self.expense_repo.get_by_id(expense_id)
        if expense is None:
            raise HTTPException(status_code=404, detail={"code": "NOT_FOUND", "message": "Expense not found"})

        if current_user.role != UserRole.ADMIN and expense.user_id != current_user.id:
            raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Access denied"})

        month = datetime_to_month(expense.spent_at)
        await self.db.delete(expense)
        await self.db.commit()
        await self.invalidate_stats_cache(expense.user_id, month)

    async def export_csv(
        self,
        current_user: User,
        *,
        date_from: datetime | None,
        date_to: datetime | None,
        category_id: int | None,
        query: str | None,
        user_id: int | None,
    ) -> str:
        target_user_id = current_user.id
        if current_user.role == UserRole.ADMIN:
            target_user_id = user_id

        rows, _ = await self.expense_repo.list_expenses(
            user_id=target_user_id,
            date_from=date_from,
            date_to=date_to,
            category_id=category_id,
            query=query,
            page=1,
            size=10000,
        )

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["id", "user_id", "category", "amount", "currency", "note", "spent_at", "created_at"])
        for item in rows:
            writer.writerow(
                [
                    item.id,
                    item.user_id,
                    item.category.name,
                    item.amount,
                    item.currency,
                    item.note or "",
                    item.spent_at.isoformat(),
                    item.created_at.isoformat(),
                ]
            )
        return output.getvalue()

    async def invalidate_stats_cache(self, user_id: int, month: str) -> None:
        await cache_delete(f"stats:{user_id}:{month}")
