from __future__ import annotations

import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

from aiogram import Bot
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))

from app.core.config import get_settings  # noqa: E402
from app.db.session import AsyncSessionLocal  # noqa: E402
from app.models import NotificationDelivery, ScheduleEntry, User  # noqa: E402
from app.services.schedule_service import ScheduleService  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("notification_worker")


async def send_due_notifications() -> None:
    settings = get_settings()
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    now = datetime.now(settings.tz)
    async with AsyncSessionLocal() as session:
        users = (await session.scalars(select(User).where(User.notifications_enabled.is_(True)))).all()
        bot = Bot(token)
        try:
            for user in users:
                schedule = await ScheduleService(session, settings).for_date(now.date())
                for lesson in schedule.lessons:
                    minutes = user.notification_minutes_before
                    due_from = lesson.starts_at - timedelta(minutes=minutes)
                    due_until = due_from + timedelta(seconds=65)
                    if not (due_from <= now <= due_until):
                        continue
                    try:
                        await session.execute(
                            insert(NotificationDelivery).values(user_id=user.id, schedule_id=lesson.id, minutes_before=minutes)
                        )
                        await session.commit()
                    except IntegrityError:
                        await session.rollback()
                        continue
                    text = f"🔔 Напоминание\n\nЧерез {minutes} минут начинается:\n\n📚 {lesson.subject}\n\n⏰ {lesson.starts_at:%H:%M}-{lesson.ends_at:%H:%M}"
                    if lesson.teacher:
                        text += f"\n\n👨‍🏫 {lesson.teacher}"
                    keyboard = (
                        InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔗 Подключиться к паре", url=lesson.meeting_url)]])
                        if lesson.meeting_url
                        else None
                    )
                    await bot.send_message(user.telegram_id, text, reply_markup=keyboard)
                    logger.info("notification sent user_id=%s schedule_id=%s", user.id, lesson.id)
        finally:
            await bot.session.close()


async def main() -> None:
    while True:
        try:
            await send_due_notifications()
        except Exception:
            logger.exception("notification cycle failed")
        await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(main())
