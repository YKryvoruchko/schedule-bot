from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/db")
async def db_health(session: AsyncSession = Depends(get_db)) -> dict[str, str]:
    await session.execute(text("select 1"))
    return {"status": "ok"}
