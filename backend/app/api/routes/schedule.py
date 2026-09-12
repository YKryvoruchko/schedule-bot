from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_app_settings, get_db
from app.core.config import Settings
from app.models import User
from app.schemas.schedule import DayScheduleOut, TelegramUserIn, WeekScheduleOut
from app.services.schedule_service import ScheduleService

router = APIRouter(prefix="/api/schedule", tags=["schedule"])


@router.get("/today", response_model=DayScheduleOut)
async def today(group: str | None = Query(default=None), session: AsyncSession = Depends(get_db), settings: Settings = Depends(get_app_settings)):
    return await ScheduleService(session, settings).today(group)


@router.get("/tomorrow", response_model=DayScheduleOut)
async def tomorrow(group: str | None = Query(default=None), session: AsyncSession = Depends(get_db), settings: Settings = Depends(get_app_settings)):
    return await ScheduleService(session, settings).tomorrow(group)


@router.get("/week", response_model=WeekScheduleOut)
async def week(group: str | None = Query(default=None), session: AsyncSession = Depends(get_db), settings: Settings = Depends(get_app_settings)):
    return await ScheduleService(session, settings).week(group)


@router.get("/date/{target_date}", response_model=DayScheduleOut)
async def by_date(target_date: date, group: str | None = Query(default=None), session: AsyncSession = Depends(get_db), settings: Settings = Depends(get_app_settings)):
    return await ScheduleService(session, settings).for_date(target_date, group)


@router.post("/telegram-users")
async def upsert_telegram_user(payload: TelegramUserIn, session: AsyncSession = Depends(get_db)) -> dict[str, str]:
    user = await session.scalar(select(User).where(User.telegram_id == payload.telegram_id))
    if user is None:
        user = User(telegram_id=payload.telegram_id)
        session.add(user)
    user.username = payload.username
    user.first_name = payload.first_name
    user.last_name = payload.last_name
    await session.commit()
    return {"status": "ok"}
