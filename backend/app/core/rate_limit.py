from app.core.config import get_settings
from app.core.cache import get_redis_client


class RateLimitExceeded(Exception):
    pass


async def enforce_login_rate_limit(identifier: str) -> None:
    settings = get_settings()
    key = f"rl:login:{identifier}"
    try:
        redis_client = await get_redis_client()

        current = await redis_client.incr(key)
        if current == 1:
            await redis_client.expire(key, settings.RATE_LIMIT_LOGIN_WINDOW_SECONDS)

        if current > settings.RATE_LIMIT_LOGIN_ATTEMPTS:
            raise RateLimitExceeded()
    except RateLimitExceeded:
        raise
    except Exception:
        return
