from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.keyboards import MAIN_MENU
from app.services.api import ScheduleApi

router = Router()


def lesson_line(lesson: dict) -> str:
    status = {"current": "🟢 ИДЕТ СЕЙЧАС", "upcoming": "🟡 СЛЕДУЮЩАЯ ПАРА", "finished": "⚪ Завершена"}[lesson["status"]]
    start = lesson["starts_at"][11:16]
    end = lesson["ends_at"][11:16]
    parts = [f"{status}", f"{lesson['lesson_number']}. {start}-{end}", f"📚 {lesson['subject']}"]
    if lesson.get("teacher"):
        parts.append(f"👨‍🏫 {lesson['teacher']}")
    if lesson.get("room"):
        parts.append(f"🏫 {lesson['room']}")
    return "\n".join(parts)


def meeting_keyboard(lessons: list[dict]) -> InlineKeyboardMarkup | None:
    buttons = [
        [InlineKeyboardButton(text=f"🔗 Пара {lesson['lesson_number']}", url=lesson["meeting_url"])]
        for lesson in lessons
        if lesson.get("meeting_url")
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons) if buttons else None


def register(api: ScheduleApi) -> Router:
    @router.message(CommandStart())
    async def start(message: Message) -> None:
        await api.register_user(message.from_user.model_dump() if message.from_user else {})
        await message.answer("Готов показывать расписание.", reply_markup=MAIN_MENU)

    @router.message(lambda message: message.text == "📅 Сегодня")
    async def today(message: Message) -> None:
        data = await api.schedule("today")
        lessons = data["lessons"]
        if not lessons:
            await message.answer("Сегодня пар нет 🎉", reply_markup=MAIN_MENU)
            return
        await message.answer("\n\n".join(lesson_line(item) for item in lessons), reply_markup=meeting_keyboard(lessons))

    @router.message(lambda message: message.text == "📅 Завтра")
    async def tomorrow(message: Message) -> None:
        data = await api.schedule("tomorrow")
        lessons = data["lessons"]
        if not lessons:
            await message.answer("Завтра пар нет.", reply_markup=MAIN_MENU)
            return
        await message.answer("\n\n".join(lesson_line(item) for item in lessons), reply_markup=meeting_keyboard(lessons))

    @router.message(lambda message: message.text == "📚 Неделя")
    async def week(message: Message) -> None:
        data = await api.schedule("week")
        chunks = []
        for day in data["days"]:
            if day["lessons"]:
                chunks.append(f"{day['date']}:\n" + "\n\n".join(lesson_line(item) for item in day["lessons"]))
        await message.answer("\n\n".join(chunks) if chunks else "На этой неделе занятий нет.", reply_markup=MAIN_MENU)

    @router.message(lambda message: message.text == "🔔 Настройки уведомлений")
    async def notifications(message: Message) -> None:
        await message.answer("Уведомления настраиваются администратором в этой версии: 5, 10, 15 или 30 минут.", reply_markup=MAIN_MENU)

    return router
