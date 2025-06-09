import os
import asyncio
from settings import settings
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton
)

# Загрузка из .env
BOT_TOKEN = settings.BOT_TOKEN
app_url = settings.app_url

if not BOT_TOKEN:
    exit("Ошибка: не найден BOT_TOKEN в .env файле")

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Клавиатура главного меню
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='🎮 Начать игру'), KeyboardButton(text='🔄 Получить ссылку')]
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    """Обработчик команды /start"""
    game_button = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Играть сейчас", url=app_url)]
    ])
    
    await message.answer(
        "🎮 Добро пожаловать в Clicker Game!\n\n"
        "Используйте кнопки ниже для навигации:",
        reply_markup=main_keyboard
    )
    await message.answer(
        "Нажмите чтобы начать игру:",
        reply_markup=game_button
    )

@dp.message(lambda message: message.text == '🎮 Начать игру')
@dp.message(Command("game"))
async def game_handler(message: types.Message):
    """Обработчик кнопки игры"""
    game_btn = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔵 Перейти к игре", url=app_url)]
    ])
    await message.answer("Ваша ссылка на игру:", reply_markup=game_btn) 

@dp.message(lambda message: message.text == '🔄 Получить ссылку')
async def refresh_handler(message: types.Message):
    """Обработчик обновления ссылки"""
    await game_handler(message)

@dp.message()
async def any_message_handler(message: types.Message):
    """Обработчик всех остальных сообщений"""
    await message.answer(
        "Используйте кнопки меню или команды:\n"
        "/start - начать работу\n"
        "/game - получить ссылку на игру",
        reply_markup=main_keyboard
    )

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    print("Бот запущен...")
    asyncio.run(main())
