import os
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from telegram.constants import ParseMode

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

from handlers.user_private import user_private_router
from handlers.user_group import user_group_router
from handlers.admin_private import admin_router
from database.engine import create_db, session_maker
from middlewares.db import DatabaseSession

bot = Bot(token=os.getenv("TOKEN"),
          default=DefaultBotProperties(parse_mode=ParseMode.HTML))
bot.my_admins_list = []

dp = Dispatcher()

dp.include_router(user_private_router)
dp.include_router(user_group_router)
dp.include_router(admin_router)


async def on_startup():
    await create_db()


async def on_shutdown():
    print("Bot shutdown")


async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.update.middleware(DatabaseSession(session_pool=session_maker))
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    print(logger)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types(), skip_update=True)


asyncio.run(main())
