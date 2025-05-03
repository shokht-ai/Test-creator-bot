from aiogram import Bot

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

API_TOKEN = "7349199816:AAGlN739zzmn-Ny80T8GWBZz8NMqqG_Xejw"

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
