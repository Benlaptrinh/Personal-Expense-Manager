from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import TokenPayloadError, decode_token
from app.db.session import AsyncSessionLocal
from app.models import User, UserRole
from app.repositories.user_repository import UserRepository

bearer_scheme = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=401, detail={"code": "UNAUTHORIZED", "message": "Missing bearer token"})

    token = credentials.credentials
    try:
        payload = decode_token(token)
    except TokenPayloadError:
        raise HTTPException(status_code=401, detail={"code": "INVALID_TOKEN", "message": "Invalid access token"})

    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail={"code": "INVALID_TOKEN", "message": "Token type is not access"})

    user = await UserRepository(db).get_by_id(int(payload["sub"]))
    if user is None:
        raise HTTPException(status_code=401, detail={"code": "UNAUTHORIZED", "message": "User not found"})

    return user


def require_role(*roles: UserRole):
    async def checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Insufficient permission"})
        return current_user

    return checker
