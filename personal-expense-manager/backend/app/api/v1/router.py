from fastapi import APIRouter

from app.api.v1.routers.auth import router as auth_router
from app.api.v1.routers.budgets import router as budgets_router
from app.api.v1.routers.categories import router as categories_router
from app.api.v1.routers.expenses import router as expenses_router
from app.api.v1.routers.stats import router as stats_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(categories_router)
api_router.include_router(expenses_router)
api_router.include_router(budgets_router)
api_router.include_router(stats_router)
