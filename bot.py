import os
import asyncio
import logging
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
)

# Настройка логов
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("Ошибка: не найден BOT_TOKEN в .env файле")
    exit(1)

WEB_APP_URL = os.getenv("app_url")  # замените на ваш домен

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='🎮 Начать игру'), KeyboardButton(text='🔄 Получить ссылку')]
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    web_app_button = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="▶️ Играть сейчас",
            web_app=WebAppInfo(url=WEB_APP_URL)
        )]
    ])
    await message.answer(
        "🎮 Добро пожаловать в Clicker Game!\n"
        "Нажмите кнопку ниже, чтобы запустить игру в Telegram.",
        reply_markup=main_keyboard
    )
    await message.answer("Запуск MiniApp:", reply_markup=web_app_button)

@dp.message(lambda message: message.text == '🎮 Начать игру')
@dp.message(Command("game"))
async def game_handler(message: types.Message):
    game_button = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🔵 Перейти в MiniApp",
            web_app=WebAppInfo(url=WEB_APP_URL)
        )]
    ])
    await message.answer("Запуск игры в Telegram:", reply_markup=game_button)

@dp.message(lambda message: message.text == '🔄 Получить ссылку')
async def refresh_handler(message: types.Message):
    await game_handler(message)

@dp.message()
async def fallback_handler(message: types.Message):
    await message.answer(
        "Пожалуйста, используйте команды или кнопки ниже.",
        reply_markup=main_keyboard
    )

async def main():
    logger.info("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
