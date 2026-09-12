from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.config import BotSettings
from app.handlers.schedule import register
from app.services.api import ScheduleApi


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    settings = BotSettings()
    bot = Bot(settings.telegram_bot_token)
    dispatcher = Dispatcher()
    dispatcher.include_router(register(ScheduleApi(settings.backend_url, settings.default_group)))
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
