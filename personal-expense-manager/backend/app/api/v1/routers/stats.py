from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user, get_db
from app.core.responses import success_response
from app.models import User, UserRole
from app.services.stats_service import StatsService

router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get("/monthly", summary="Monthly stats with breakdown and budget vs actual")
async def monthly_stats(
    month: str = Query(..., pattern=r"^\d{4}-\d{2}$"),
    user_id: int | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    target_user_id = current_user.id
    if user_id is not None:
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Admin only"})
        target_user_id = user_id

    data = await StatsService(db).monthly_stats(target_user_id, month)
    return success_response(data.model_dump(mode="json"))
