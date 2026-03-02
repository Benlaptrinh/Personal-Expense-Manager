from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.rate_limit import enforce_login_rate_limit
from app.core.security import TokenPayloadError, create_token, decode_token, hash_password, verify_password
from app.repositories.refresh_token_repository import RefreshTokenRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenPair


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.refresh_repo = RefreshTokenRepository(db)

    async def register(self, payload: RegisterRequest):
        existing = await self.user_repo.get_by_email(payload.email)
        if existing:
            raise HTTPException(status_code=409, detail={"code": "EMAIL_EXISTS", "message": "Email already registered"})

        user = await self.user_repo.create(
            email=payload.email,
            password_hash=hash_password(payload.password),
            role=payload.role,
        )
        await self.db.commit()
        return user

    async def login(self, payload: LoginRequest, rate_limit_identifier: str) -> TokenPair:
        await enforce_login_rate_limit(rate_limit_identifier)

        user = await self.user_repo.get_by_email(payload.email)
        if user is None or not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=401, detail={"code": "INVALID_CREDENTIALS", "message": "Invalid email or password"})

        settings = get_settings()
        access_token, _, _ = create_token(
            subject=str(user.id),
            token_type="access",
            role=user.role.value,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MIN),
        )
        refresh_token, refresh_jti, refresh_exp = create_token(
            subject=str(user.id),
            token_type="refresh",
            role=user.role.value,
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )

        await self.refresh_repo.create(user_id=user.id, jti=refresh_jti, expires_at=refresh_exp)
        await self.db.commit()

        return TokenPair(access_token=access_token, refresh_token=refresh_token)

    async def refresh(self, refresh_token: str) -> TokenPair:
        try:
            payload = decode_token(refresh_token)
        except TokenPayloadError:
            raise HTTPException(status_code=401, detail={"code": "INVALID_TOKEN", "message": "Invalid refresh token"})
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail={"code": "INVALID_TOKEN", "message": "Token type is not refresh"})

        jti = payload["jti"]
        record = await self.refresh_repo.get_by_jti(jti)
        if record is None or record.revoked:
            raise HTTPException(status_code=401, detail={"code": "TOKEN_REVOKED", "message": "Refresh token is revoked"})
        if record.expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=401, detail={"code": "TOKEN_EXPIRED", "message": "Refresh token expired"})

        user = await self.user_repo.get_by_id(int(payload["sub"]))
        if user is None:
            raise HTTPException(status_code=401, detail={"code": "UNAUTHORIZED", "message": "User not found"})

        settings = get_settings()
        access_token, _, _ = create_token(
            subject=str(user.id),
            token_type="access",
            role=user.role.value,
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MIN),
        )
        new_refresh_token, new_refresh_jti, new_refresh_exp = create_token(
            subject=str(user.id),
            token_type="refresh",
            role=user.role.value,
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )

        record.revoked = True
        await self.refresh_repo.create(user_id=user.id, jti=new_refresh_jti, expires_at=new_refresh_exp)
        await self.db.commit()

        return TokenPair(access_token=access_token, refresh_token=new_refresh_token)

    async def logout(self, refresh_token: str) -> None:
        try:
            payload = decode_token(refresh_token)
        except TokenPayloadError:
            raise HTTPException(status_code=401, detail={"code": "INVALID_TOKEN", "message": "Invalid refresh token"})
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=400, detail={"code": "INVALID_TOKEN", "message": "Token type is not refresh"})

        await self.refresh_repo.revoke_by_jti(payload["jti"])
        await self.db.commit()
