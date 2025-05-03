import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from config import BOT_TOKEN, WEBHOOK_PATH, WEBHOOK_SECRET, BASE_WEBHOOK_URL
from app.handlers.base_handler import register_base_handlers
from app.handlers.file_handler import register_file_handlers
from database.shared import initialize_database

async def main():
    logging.basicConfig(level=logging.INFO)
    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    
    register_base_handlers(dp)
    register_file_handlers(dp)
    await initialize_database()

    app = web.Application()
    SimpleRequestHandler(dispatcher=dp, bot=bot, secret_token=WEBHOOK_SECRET).register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    return app

if __name__ == "__main__":
    web.run_app(main(), host="0.0.0.0", port=8000)
