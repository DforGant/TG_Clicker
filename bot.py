import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from dotenv import load_dotenv
import os

# Настройка логов
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загружаем переменные окружения
load_dotenv()

# Получаем токен и URL WebApp
BOT_TOKEN = os.getenv("BOT_TOKEN") or '7957287404:AAFvczJbKcoyglv3UTb_Hyw-pdJTN2xfQZ8'  # Замените на свой
WEBAPP_URL = os.getenv("WEBAPP_URL") or 'https://plenty-apes-end.loca.lt'  # HTTPS обязателен

if not BOT_TOKEN:
    logger.error("Ошибка: BOT_TOKEN не найден!")
    exit(1)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Главное меню с кнопкой WebApp
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎮 Открыть игру", web_app=WebAppInfo(url=WEBAPP_URL))]
    ],
    resize_keyboard=True
)

# Inline-кнопка для WebApp (альтернативный вариант)
web_app_inline_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(
            text="▶️ Играть в MiniApp",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )]
    ]
)

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    """Обработчик команды /start"""
    user_id = message.from_user.id  # Получаем ID пользователя
    logger.info(f"Пользователь {user_id} запустил бота")

    # Можно передать user_id в WebApp через URL (если требуется)
    webapp_url_with_user_id = f"{WEBAPP_URL}?tg_user_id={user_id}"

    await message.answer(
        f"🎮 Добро пожаловать в игру, ID {user_id}!\n\n"
        "Нажмите кнопку ниже, чтобы открыть игру в Telegram:",
        reply_markup=main_keyboard
    )
    
    # Альтернативный вариант с Inline-кнопкой
    await message.answer(
        "Или нажмите здесь:",
        reply_markup=web_app_inline_button
    )

@dp.message()
async def default_handler(message: types.Message):
    """Обработчик остальных сообщений"""
    await message.answer(
        "Используйте кнопку ниже для запуска игры или /start.",
        reply_markup=main_keyboard
    )

async def main():
    logger.info("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
