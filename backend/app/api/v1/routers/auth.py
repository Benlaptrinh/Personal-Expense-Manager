from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.core.responses import success_response
from app.schemas.auth import LoginRequest, LogoutRequest, RefreshRequest, RegisterRequest, UserPublic
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", summary="Register new user")
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    user = await AuthService(db).register(payload)
    return success_response(UserPublic.model_validate(user).model_dump())


@router.post("/login", summary="Login and get access/refresh tokens")
async def login(payload: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    identifier = payload.email or (request.client.host if request.client else "unknown")
    token_pair = await AuthService(db).login(payload, identifier)
    return success_response(token_pair.model_dump())


@router.post("/refresh", summary="Refresh token pair")
async def refresh(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    token_pair = await AuthService(db).refresh(payload.refresh_token)
    return success_response(token_pair.model_dump())


@router.post("/logout", summary="Revoke refresh token")
async def logout(payload: LogoutRequest, db: AsyncSession = Depends(get_db)):
    await AuthService(db).logout(payload.refresh_token)
    return success_response({"logged_out": True})
