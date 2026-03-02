from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.core.responses import success_response
from app.models import User
from app.schemas.budget import BudgetRead, BudgetUpsert
from app.services.budget_service import BudgetService

router = APIRouter(prefix="/budgets", tags=["Budgets"])


@router.get("", summary="List budgets by month")
async def list_budgets(
    month: str = Query(..., pattern=r"^\d{4}-\d{2}$"),
    user_id: int | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items = await BudgetService(db).list_budgets(current_user, month, user_id)
    data = [
        BudgetRead(
            id=item.id,
            category_id=item.category_id,
            category_name=item.category.name,
            month=item.month,
            limit_amount=item.limit_amount,
        ).model_dump(mode="json")
        for item in items
    ]
    return success_response(data)


@router.put("/{category_id}", summary="Create/update budget for category in month")
async def upsert_budget(
    category_id: int,
    payload: BudgetUpsert,
    month: str = Query(..., pattern=r"^\d{4}-\d{2}$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    item = await BudgetService(db).upsert_budget(current_user, category_id, month, payload)
    return success_response(
        BudgetRead(
            id=item.id,
            category_id=item.category_id,
            category_name=item.category.name,
            month=item.month,
            limit_amount=item.limit_amount,
        ).model_dump(mode="json")
    )
