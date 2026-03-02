from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.cache import close_redis
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.responses import success_response

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield
    await close_redis()


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="API for personal expense manager with auth, RBAC, budgets and monthly stats.",
    lifespan=lifespan,
    openapi_tags=[
        {"name": "Auth", "description": "Register/login/refresh/logout"},
        {"name": "Categories", "description": "Expense/income categories"},
        {"name": "Expenses", "description": "Expense CRUD, filter, pagination, CSV export"},
        {"name": "Budgets", "description": "Monthly budgets by category"},
        {"name": "Stats", "description": "Monthly totals, breakdown and budget vs actual"},
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    return success_response({"message": "Personal Expense Manager API is running"})


@app.get("/health")
async def health():
    return success_response({"status": "ok"})
