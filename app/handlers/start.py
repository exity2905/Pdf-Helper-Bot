from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from app.i18n import language_by_label, t
from app.keyboards import language_keyboard, main_menu_keyboard
from app.services.preferences import get_user_lang, set_user_lang


router = Router()


@router.message(CommandStart())
async def start(message: Message) -> None:
    lang = get_user_lang(message.from_user.id)
    await message.answer(t(lang, "choose_language"), reply_markup=language_keyboard())


@router.message(F.text.in_({"🇺🇦 Українська", "🇷🇺 Русский", "🇬🇧 English"}))
async def choose_language(message: Message) -> None:
    lang = language_by_label(message.text) or "uk"
    set_user_lang(message.from_user.id, lang)

    await message.answer(
        t(lang, "language_saved"),
        reply_markup=main_menu_keyboard(lang),
        parse_mode="HTML",
    )


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    lang = get_user_lang(message.from_user.id)
    await message.answer(
        t(lang, "help_command"),
        reply_markup=main_menu_keyboard(lang),
    )
