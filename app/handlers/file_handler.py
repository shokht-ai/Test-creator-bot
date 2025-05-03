from aiogram import Dispatcher, F
from aiogram.filters import Command

from app.handlers.base_handler import start_command
# -------------------------
from app.view_subscription_price import view_subscription
from app.uploading_file import handle_excel_file
from app.sending_file import send_bank_file
from app.start_poll import start_poll_test, poll_answer_handler, stop_test

from itertools import islice
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from database.banks import get_banks_by_user
from app.generate_pro_keys import generate_unique_id, check_key_used, restart_users, update_capacity
from app.stats import info_bot_stats


def chunked(data, size):
    it = iter(data)
    return iter(lambda: list(islice(it, size)), [])


def create_bank_buttons(banks, command_prefix: str):
    sorted_banks = sorted(banks, key=lambda b: b[1].lower())

    buttons = [
        InlineKeyboardButton(text=bank[1], callback_data=command_prefix + str(bank[2]))
        for bank in sorted_banks
    ]

    return list(chunked(buttons, 3))


async def list_user_banks(message: Message):
    user_id = message.from_user.id
    banks = get_banks_by_user(user_id)

    if message.text in ["📚 Testlarim", "/testlarim"]:
        if not banks:
            await message.answer("📭 Sizda hozircha hech qanday test yo'q.")
            return

        response = "<b>📚 Testlaringiz:</b>\n\n"
        for bank in banks:
            # Sana formatlash
            original_date = bank[0]  # bank[0] dan sana olish
            from datetime import datetime
            date_object = datetime.fromisoformat(original_date)  # ISO formatidagi sanani datetime ob'ektiga aylantirish
            formatted_date = date_object.strftime('%d-%m-%Y')  # Kun-oy-yil formatiga o'tkazish
            response += f"🔹 <b>{bank[1]}</b>\n (Yaratilgan: <code>{formatted_date}</code>)\n\n"
        await message.answer(response)

    elif message.text in ["📥 Savollarni yuklab olish", "🚀 Testni boshlash", "/test", "/savollar"]:
        poll_type = "test:" if message.text in ["🚀 Testni boshlash", "/test"] else "savollar:"
        inline_keyboard = create_bank_buttons(banks, poll_type)
        inline_kb = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
        if len(inline_keyboard) == 0:
            await message.answer("📭 Sizda hozircha hech qanday test yo'q.")
            return
        await message.answer(
            "<b>📚 Testlaringiz:</b>\nIltimos, foydalanmoqchi bo'lgan testizni tanlang...\n\n",
            reply_markup=inline_kb
        )


async def no_commands(msg: Message):
    await start_command(msg, text="🤔 Kechirasiz, bu buyruqni tushunmadim. Menyudan biror amalni tanlang.")


async def check_founder(msg: Message):
    from database.users import get_user_by_id
    user_type = get_user_by_id(msg.from_user.id)
    if user_type[0][0] != "founder":
        await no_commands(msg)
    else:
        await generate_unique_id(msg)


# ______________________________________________


def register_file_handlers(dp: Dispatcher):
    dp.message.register(handle_excel_file, F.document)

    # Slash va matn shaklida test boshlash
    dp.message.register(list_user_banks, Command("test"))
    dp.message.register(list_user_banks, F.text == "🚀 Testni boshlash")

    # Slash va matn shaklida savollarni ko‘rish
    dp.message.register(list_user_banks, Command("savollar"))
    dp.message.register(list_user_banks, F.text == "📥 Savollarni yuklab olish")

    # Slash va matn shaklida banklarni ko‘rish
    dp.message.register(list_user_banks, Command("testlarim"))
    dp.message.register(list_user_banks, F.text == "📚 Testlarim")

    dp.message.register(view_subscription, Command("kabinam"))
    dp.message.register(view_subscription, F.text == "👤 Kabinam")

    # Pro obunani activlashtirish
    dp.message.register(check_key_used, F.text.startswith("/pro "))
    dp.message.register(check_founder, Command("pro"))

    dp.message.register(info_bot_stats, Command("info_bot"))

    dp.message.register(update_capacity, Command("update_capacity"))
    dp.message.register(restart_users, Command("start_users"))
    dp.message.register(no_commands, F.text.startswith("/"))

    dp.message.register(stop_test, F.text == "⛔ Testni to‘xtatish")
    dp.callback_query.register(start_poll_test, lambda c: c.data.startswith("test:"))
    dp.callback_query.register(send_bank_file, lambda c: c.data.startswith("savollar:"))

    dp.poll_answer.register(poll_answer_handler)
