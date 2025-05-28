import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import (ReplyKeyboardMarkup, 
                          KeyboardButton, 
                          InlineKeyboardMarkup, 
                          InlineKeyboardButton)

# Загрузка токена из .env
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    exit("Ошибка: не найден BOT_TOKEN в .env файле")

# Инициализация бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Главное меню
main_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=False
).row(
    KeyboardButton('🎮 Начать игру'),
    KeyboardButton('🔄 Получить ссылку')
)

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    """Обработчик команды /start"""
    game_button = InlineKeyboardMarkup().add(
        InlineKeyboardButton("▶️ Играть сейчас", url="https://example-game.com/play")
    )
    
    await message.answer(
        "🎮 Добро пожаловать в Clicker Game!\n\n"
        "Используйте кнопки ниже для навигации:",
        reply_markup=main_keyboard
    )
    await message.answer(
        "Нажмите чтобы начать игру:",
        reply_markup=game_button
    )

@dp.message_handler(lambda m: m.text == '🎮 Начать игру')
@dp.message_handler(commands=['game'])
async def game_handler(message: types.Message):
    """Обработчик кнопки игры"""
    game_btn = InlineKeyboardMarkup().add(
        InlineKeyboardButton("🔵 Перейти к игре", url="https://example-game.com/play")
    )
    await message.answer("Ваша ссылка на игру:", reply_markup=game_btn)

@dp.message_handler(lambda m: m.text == '🔄 Получить ссылку')
async def refresh_handler(message: types.Message):
    """Обработчик обновления ссылки"""
    await game_handler(message)

@dp.message_handler()
async def any_message_handler(message: types.Message):
    """Обработчик всех остальных сообщений"""
    await message.answer(
        "Используйте кнопки меню или команды:\n"
        "/start - начать работу\n"
        "/game - получить ссылку на игру",
        reply_markup=main_keyboard
    )

if __name__ == '__main__':
    print("Бот запущен...")
    executor.start_polling(dp, skip_updates=True)
