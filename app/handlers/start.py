from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from app.keyboards import main_menu_keyboard


router = Router()


WELCOME_TEXT = (
    "👋 Привет! Я PDF Helper Bot.\n\n"
    "Выбери раздел ниже:\n"
    "📸 Скан — фото, документы, паспорт / ID.\n"
    "🧰 Инструменты — сжать, разделить или прочитать PDF."
)


@router.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(WELCOME_TEXT, reply_markup=main_menu_keyboard())


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    await message.answer(
        "✨ Как пользоваться\n\n"
        "1. Выбери раздел: 📸 Скан или 🧰 Инструменты.\n"
        "2. Нажми нужное действие.\n"
        "3. Отправь фото, изображение файлом или PDF.\n\n"
        "💡 Для лучшего качества отправляй фото как файл.",
        reply_markup=main_menu_keyboard(),
    )
