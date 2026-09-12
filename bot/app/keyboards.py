from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

MAIN_MENU = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📅 Сегодня"), KeyboardButton(text="📅 Завтра")],
        [KeyboardButton(text="📚 Неделя"), KeyboardButton(text="🔔 Настройки уведомлений")],
    ],
    resize_keyboard=True,
)
