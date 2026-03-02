from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import cache_get_json, cache_set_json
from app.core.config import get_settings
from app.repositories.expense_repository import ExpenseRepository
from app.repositories.stats_repository import StatsRepository
from app.schemas.stats import BudgetActualItem, CategoryBreakdown, MonthlyStatsResponse
from app.services.utils import month_to_range


class StatsService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.expense_repo = ExpenseRepository(db)
        self.stats_repo = StatsRepository(db)

    async def monthly_stats(self, user_id: int, month: str) -> MonthlyStatsResponse:
        key = f"stats:{user_id}:{month}"
        cached = await cache_get_json(key)
        if cached is not None:
            return MonthlyStatsResponse.model_validate(cached)

        month_start, month_end = month_to_range(month)

        breakdown_rows = await self.stats_repo.get_breakdown(user_id, month_start, month_end)
        breakdown: list[CategoryBreakdown] = []
        total_spend = Decimal("0")
        total_income = Decimal("0")

        for row in breakdown_rows:
            item = CategoryBreakdown(
                category_id=row[0],
                category_name=row[1],
                type=row[2].value,
                total=Decimal(str(row[3])),
            )
            breakdown.append(item)
            if item.type == "expense":
                total_spend += item.total
            else:
                total_income += item.total

        budget_rows = await self.stats_repo.get_budget_vs_actual(user_id, month, month_start, month_end)
        budget_vs_actual = [
            BudgetActualItem(
                category_id=row[0],
                category_name=row[1],
                limit_amount=Decimal(str(row[2])),
                actual_amount=Decimal(str(row[3])),
            )
            for row in budget_rows
        ]

        response = MonthlyStatsResponse(
            month=month,
            total_spend=total_spend,
            total_income=total_income,
            breakdown=breakdown,
            budget_vs_actual=budget_vs_actual,
        )

        settings = get_settings()
        await cache_set_json(key, response.model_dump(mode="json"), settings.STATS_CACHE_TTL_SECONDS)
        return response
