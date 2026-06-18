from pathlib import Path

from aiogram import Bot

from app.config import RUNTIME_DIR


def get_user_dir(user_id: int) -> Path:
    user_dir = RUNTIME_DIR / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir


def last_pdf_path(user_id: int) -> Path:
    return get_user_dir(user_id) / "last.pdf"


async def save_telegram_file(bot: Bot, file_id: str, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    file = await bot.get_file(file_id)
    await bot.download_file(file.file_path, destination)
    return destination
