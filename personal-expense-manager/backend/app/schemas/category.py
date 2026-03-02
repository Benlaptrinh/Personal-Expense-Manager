from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import CategoryType


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    type: CategoryType


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=120)
    type: CategoryType | None = None


class CategoryRead(BaseModel):
    id: int
    name: str
    type: CategoryType
    created_at: datetime

    model_config = {"from_attributes": True}
