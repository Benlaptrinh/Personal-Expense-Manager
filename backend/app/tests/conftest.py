from __future__ import annotations

import os
from collections import defaultdict
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/15")
os.environ.setdefault("JWT_SECRET", "test-secret")

from app.core.config import clear_settings_cache
from app.db.base import Base
from app.db.session import AsyncSessionLocal, engine
from app.main import app


class FakeRedis:
    def __init__(self):
        self.store: dict[str, str] = {}
        self.counters = defaultdict(int)

    async def get(self, key: str):
        return self.store.get(key)

    async def set(self, key: str, value: str, ex: int | None = None):
        self.store[key] = value

    async def delete(self, key: str):
        self.store.pop(key, None)

    async def incr(self, key: str):
        self.counters[key] += 1
        return self.counters[key]

    async def expire(self, key: str, ttl: int):
        return True

    async def close(self):
        return None


@pytest.fixture(scope="session", autouse=True)
def _clear_settings_cache():
    clear_settings_cache()


@pytest_asyncio.fixture(autouse=True)
async def setup_db() -> AsyncGenerator[None, None]:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest_asyncio.fixture()
async def fake_redis(monkeypatch):
    from app.core import cache

    redis = FakeRedis()

    async def _get_fake():
        return redis

    monkeypatch.setattr(cache, "_redis_client", redis)
    monkeypatch.setattr(cache, "get_redis_client", _get_fake)
    yield redis


@pytest_asyncio.fixture()
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture()
async def client(fake_redis) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
