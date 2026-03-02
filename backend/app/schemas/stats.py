from decimal import Decimal

from pydantic import BaseModel


class CategoryBreakdown(BaseModel):
    category_id: int
    category_name: str
    type: str
    total: Decimal


class BudgetActualItem(BaseModel):
    category_id: int
    category_name: str
    limit_amount: Decimal
    actual_amount: Decimal


class MonthlyStatsResponse(BaseModel):
    month: str
    total_spend: Decimal
    total_income: Decimal
    breakdown: list[CategoryBreakdown]
    budget_vs_actual: list[BudgetActualItem]
