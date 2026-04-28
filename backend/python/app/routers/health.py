from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.database import get_async_session
from app.schemas import HealthResponse, ApiResponse

router = APIRouter(tags=["健康检查"])


@router.get("/health", response_model=ApiResponse[HealthResponse])
async def health_check():
    return ApiResponse(
        success=True,
        data=HealthResponse(
            status="ok",
            message="Memorise backend is running"
        )
    )


@router.get("/health/db", response_model=ApiResponse)
async def db_health_check(
    db: AsyncSession = Depends(get_async_session)
):
    try:
        result = await db.execute(text("SELECT 1"))
        result.scalar()
        return ApiResponse(
            success=True,
            data={"status": "ok", "message": "Database connection is healthy"}
        )
    except Exception as e:
        return ApiResponse(
            success=False,
            error=f"Database connection failed: {str(e)}"
        )
