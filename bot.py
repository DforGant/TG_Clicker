import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo
)
from dotenv import load_dotenv
import os

# Загружаем переменные окружения из .env (если есть)
load_dotenv()

# Получаем токен и URL WebApp из окружения
BOT_TOKEN = os.getenv("BOT_TOKEN") or '7957287404:AAFvczJbKcoyglv3UTb_Hyw-pdJTN2xfQZ8' # Токен бота (на данный момент стоит мой. Изменить)
WEBAPP_URL = os.getenv("WEBAPP_URL") or 'https://plenty-apes-end.loca.lt'  # HTTPS обязательный, (поставите свой)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Главное меню с кнопкой запуска WebApp внутри Telegram
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎮 Открыть игру", web_app=WebAppInfo(url=WEBAPP_URL))]
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    """Обработчик команды /start"""
    await message.answer(
        "🎮 Добро пожаловать в Clicker Game!\n\n"
        "Нажмите кнопку ниже, чтобы открыть игру прямо в Telegram:",
        reply_markup=main_keyboard
    )

@dp.message()
async def default_handler(message: types.Message):
    """Обработчик всех остальных сообщений"""
    await message.answer(
        "Используйте кнопку ниже для запуска игры или команду /start.",
        reply_markup=main_keyboard
    )

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
