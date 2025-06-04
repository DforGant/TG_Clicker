import os
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo
)

# Загрузка переменных окружения
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    exit("Ошибка: не найден BOT_TOKEN в .env файле")

# Ссылка на MiniApp — обязательно HTTPS в продакшене!
WEB_APP_URL = "https://yourdomain.com/game"  # замените на ваш домен

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Главное меню
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='🎮 Начать игру'), KeyboardButton(text='🔄 Получить ссылку')]
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    """Обработка команды /start"""
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
    """Обработка запуска игры"""
    game_button = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🔵 Перейти в MiniApp",
            web_app=WebAppInfo(url=WEB_APP_URL)
        )]
    ])
    await message.answer("Запуск игры в Telegram:", reply_markup=game_button)

@dp.message(lambda message: message.text == '🔄 Получить ссылку')
async def refresh_handler(message: types.Message):
    """Обработка повторного получения ссылки"""
    await game_handler(message)

@dp.message()
async def fallback_handler(message: types.Message):
    """Обработка всех других сообщений"""
    await message.answer(
        "Пожалуйста, используйте команды или кнопки ниже.",
        reply_markup=main_keyboard
    )

async def main():
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
