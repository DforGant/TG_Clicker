import sqlite3
from datetime import datetime
from aiogram import Bot, Dispatcher, types

# Инициализация бота и БД
bot = Bot(token="YOUR_BOT_TOKEN")
dp = Dispatcher(bot)
conn = sqlite3.connect('clicker.db')
cursor = conn.cursor()

# Создаем таблицу пользователей при первом запуске
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    telegram_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0,
    last_session_start TEXT,
    last_session_end TEXT
)
''')
conn.commit()

# Хранение активных сессий в памяти
active_sessions = {}  # {telegram_id: {'clicks': int, 'start_time': datetime}}

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    """Обработчик команды /start - регистрирует пользователя и дает ссылку"""
    telegram_id = message.from_user.id
    
    # Добавляем пользователя в БД если его нет
    cursor.execute(
        "INSERT OR IGNORE INTO users (telegram_id, balance) VALUES (?, 0)",
        (telegram_id,)
    )
    conn.commit()
    
    # Отправляем приветствие и ссылку
    await message.answer(
        "Добро пожаловать в Clicker Game!\n\n"
        "Играйте по ссылке: [ваша ссылка на игру]\n"
        "Используйте /game чтобы получить ссылку снова"
    )

@dp.message_handler(commands=['game'])
async def game_link_handler(message: types.Message):
    """Обработчик команды /game - отправляет ссылку на игру"""
    await message.answer("Ваша ссылка на игру: [ваша ссылка на игру]")

@dp.message_handler()
async def other_messages_handler(message: types.Message):
    """Обработчик всех остальных сообщений"""
    await message.answer(
        "Я не понимаю ваше сообщение. Доступные команды:\n"
        "/start - начать работу с ботом\n"
        "/game - получить ссылку на игру"
    )
