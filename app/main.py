import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.config import settings
from app.handlers import files, start


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()
    dp.include_router(start.router)
    dp.include_router(files.router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
