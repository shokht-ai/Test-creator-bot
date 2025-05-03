# bot.py
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand


from database import initialize_database
from database.banks import update_capacity_by_time
from core.bot_instance import bot as b


dp = Dispatcher(storage=MemoryStorage())

commands = [
        BotCommand(command="start", description="Botni ishga tushirish"),
        BotCommand(command="help", description="Yordam olish"),
        BotCommand(command="testlarim", description="Testlaringizni ko‘rish"),
        BotCommand(command="kabinam", description="Mening profilim"),
        BotCommand(command="test", description="Testni boshlash"),
        BotCommand(command="savollar", description="Savollarni yuklab olish"),
    ]

async def set_bot_commands(bot: Bot):
    await bot.set_my_commands(commands)

# Barcha handlerlarni ro‘yxatdan o‘tkazamiz
def setup_handlers():
    from app.handlers.file_handler import register_file_handlers
    from app.handlers.base_handler import register_base_handlers
    register_base_handlers(dp)
    register_file_handlers(dp)

check_time = True
async def wait_until_first_of_month():
    global check_time
    now = datetime.now()
    # Agar hozirgi sana 1-sana bo'lsa
    if now.day == 1:
        update_capacity_by_time()
    # Hozirgi oyning 1-sanasini hisoblash
    if now.month == 12:
        next_month = datetime(now.year + 1, 1, 1)
    else:
        next_month = datetime(now.year, now.month + 1, 1)
    wait_time = (next_month - now).total_seconds()
    check_time = False
    print("salom")
    await asyncio.sleep(wait_time)
    check_time = True

async def main():
    print("✅ Bot ishga tushdi...")
    initialize_database()    # botni birinchi ishlatishdan oldin izohdan olinsin, bu faqat birmarta ishlatilinnsa yetarli
    setup_handlers()
    # if check_time:
    #     await wait_until_first_of_month()
    await b.delete_webhook(drop_pending_updates=True)
    await set_bot_commands(b)
    await dp.start_polling(b)

if __name__ == "__main__":
    try:
		import asyncio
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot to‘xtatildi.")
