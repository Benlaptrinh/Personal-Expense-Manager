from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class ExpenseCreate(BaseModel):
    category_id: int
    amount: Decimal = Field(gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=3)
    note: str | None = Field(default=None, max_length=1000)
    spent_at: datetime


class ExpenseUpdate(BaseModel):
    category_id: int | None = None
    amount: Decimal | None = Field(default=None, gt=0)
    currency: str | None = Field(default=None, min_length=3, max_length=3)
    note: str | None = Field(default=None, max_length=1000)
    spent_at: datetime | None = None


class ExpenseRead(BaseModel):
    id: int
    category_id: int
    category_name: str
    amount: Decimal
    currency: str
    note: str | None
    spent_at: datetime
    created_at: datetime


class ExpenseListMeta(BaseModel):
    page: int
    size: int
    total: int
