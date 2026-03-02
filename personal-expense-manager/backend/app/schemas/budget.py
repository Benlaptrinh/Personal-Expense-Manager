from decimal import Decimal

from pydantic import BaseModel, Field


class BudgetUpsert(BaseModel):
    limit_amount: Decimal = Field(gt=0)


class BudgetRead(BaseModel):
    id: int
    category_id: int
    category_name: str
    month: str
    limit_amount: Decimal

    model_config = {"from_attributes": True}
