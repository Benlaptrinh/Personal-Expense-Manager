from datetime import datetime, timezone

from fastapi import HTTPException


def month_to_range(month: str) -> tuple[datetime, datetime]:
    try:
        year, month_num = month.split("-")
        year_i = int(year)
        month_i = int(month_num)
        start = datetime(year_i, month_i, 1, tzinfo=timezone.utc)
    except Exception as exc:
        raise HTTPException(status_code=422, detail={"code": "INVALID_MONTH", "message": "month must be YYYY-MM"}) from exc

    if month_i == 12:
        end = datetime(year_i + 1, 1, 1, tzinfo=timezone.utc)
    else:
        end = datetime(year_i, month_i + 1, 1, tzinfo=timezone.utc)

    return start, end


def datetime_to_month(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m")
