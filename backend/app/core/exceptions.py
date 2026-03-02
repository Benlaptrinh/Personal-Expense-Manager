from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.core.responses import error_response
from app.core.rate_limit import RateLimitExceeded


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
        detail = exc.detail
        if isinstance(detail, dict) and "code" in detail and "message" in detail:
            payload = error_response(detail["code"], detail["message"], detail.get("details"))
        else:
            payload = error_response("HTTP_ERROR", str(detail))
        return JSONResponse(status_code=exc.status_code, content=payload)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=error_response("VALIDATION_ERROR", "Request validation failed", exc.errors()),
        )

    @app.exception_handler(IntegrityError)
    async def db_integrity_handler(_: Request, __: IntegrityError) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content=error_response("DB_INTEGRITY_ERROR", "Database integrity constraint violated"),
        )

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(_: Request, __: RateLimitExceeded) -> JSONResponse:
        return JSONResponse(
            status_code=429,
            content=error_response("RATE_LIMITED", "Too many login attempts. Please try again later."),
        )
