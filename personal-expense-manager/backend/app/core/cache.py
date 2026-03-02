import json
from typing import Any

import redis.asyncio as redis

from app.core.config import get_settings


_redis_client: redis.Redis | None = None


async def get_redis_client() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        settings = get_settings()
        _redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_client


async def cache_get_json(key: str) -> dict[str, Any] | None:
    client = await get_redis_client()
    value = await client.get(key)
    if value is None:
        return None
    return json.loads(value)


async def cache_set_json(key: str, value: dict[str, Any], ttl_seconds: int) -> None:
    client = await get_redis_client()
    await client.set(key, json.dumps(value), ex=ttl_seconds)


async def cache_delete(key: str) -> None:
    client = await get_redis_client()
    await client.delete(key)


async def close_redis() -> None:
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None
