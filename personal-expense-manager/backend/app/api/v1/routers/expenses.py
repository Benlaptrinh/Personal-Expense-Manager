from datetime import datetime

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.core.responses import success_response
from app.models import User
from app.schemas.expense import ExpenseCreate, ExpenseRead, ExpenseUpdate
from app.services.expense_service import ExpenseService

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.get("", summary="List expenses with pagination and filters")
async def list_expenses(
    date_from: datetime | None = Query(default=None, alias="from"),
    date_to: datetime | None = Query(default=None, alias="to"),
    category_id: int | None = None,
    q: str | None = None,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    user_id: int | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ExpenseService(db)
    rows, total = await service.list_expenses(
        current_user,
        date_from=date_from,
        date_to=date_to,
        category_id=category_id,
        query=q,
        page=page,
        size=size,
        user_id=user_id,
    )
    data = [
        ExpenseRead(
            id=item.id,
            category_id=item.category_id,
            category_name=item.category.name,
            amount=item.amount,
            currency=item.currency,
            note=item.note,
            spent_at=item.spent_at,
            created_at=item.created_at,
        ).model_dump(mode="json")
        for item in rows
    ]
    return success_response(data, meta={"page": page, "size": size, "total": total})


@router.get("/export", summary="Export expenses to CSV")
async def export_expenses(
    date_from: datetime | None = Query(default=None, alias="from"),
    date_to: datetime | None = Query(default=None, alias="to"),
    category_id: int | None = None,
    q: str | None = None,
    user_id: int | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    csv_content = await ExpenseService(db).export_csv(
        current_user,
        date_from=date_from,
        date_to=date_to,
        category_id=category_id,
        query=q,
        user_id=user_id,
    )
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=expenses.csv"},
    )


@router.post("", summary="Create expense")
async def create_expense(
    payload: ExpenseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    item = await ExpenseService(db).create_expense(current_user, payload)
    return success_response(
        ExpenseRead(
            id=item.id,
            category_id=item.category_id,
            category_name=item.category.name,
            amount=item.amount,
            currency=item.currency,
            note=item.note,
            spent_at=item.spent_at,
            created_at=item.created_at,
        ).model_dump(mode="json")
    )


@router.patch("/{expense_id}", summary="Update expense")
async def update_expense(
    expense_id: int,
    payload: ExpenseUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    item = await ExpenseService(db).update_expense(current_user, expense_id, payload)
    return success_response(
        ExpenseRead(
            id=item.id,
            category_id=item.category_id,
            category_name=item.category.name,
            amount=item.amount,
            currency=item.currency,
            note=item.note,
            spent_at=item.spent_at,
            created_at=item.created_at,
        ).model_dump(mode="json")
    )


@router.delete("/{expense_id}", summary="Delete expense")
async def delete_expense(
    expense_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await ExpenseService(db).delete_expense(current_user, expense_id)
    return success_response({"deleted": True})
