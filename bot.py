import os
import asyncio
from urllib.parse import quote
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton
)

# Загрузка токена
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')

if not BOT_TOKEN:
    exit("Ошибка: не найден BOT_TOKEN в .env файле")

# Базовый URL веб-приложения (замените на ваш домен в продакшене)
APP_BASE_URL = "http://127.0.0.1:8000/" #Наш домен поставить сюда

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

def generate_game_url(telegram_id: str, username: str = "") -> str:
    """
    Генерирует URL для игры с параметрами пользователя
    :param telegram_id: ID пользователя в Telegram
    :param username: Имя пользователя (опционально)
    :return: Сформированный URL
    """
    params = {
        'telegram_id': str(telegram_id),
        'username': username if username else ""
    }
    query_string = "&".join(f"{k}={quote(v)}" for k, v in params.items() if v)
    return f"{APP_BASE_URL}?{query_string}"

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    """Обработчик команды /start"""
    user = message.from_user
    game_url = generate_game_url(user.id, user.full_name)
    
    game_button = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Играть сейчас", url=game_url)]
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
    user = message.from_user
    game_url = generate_game_url(user.id, user.full_name)
    
    game_btn = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔵 Перейти к игре", url=game_url)]
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

    """
    <script>
    document.addEventListener('DOMContentLoaded', () => {
        // Получаем параметры из URL
        const urlParams = new URLSearchParams(window.location.search);
        const telegramId = urlParams.get('telegram_id');
        
        if (telegramId) {
            // Автоматическое заполнение (поле и скрываем форму регистрации)
            document.getElementById('nameUser').value = telegramId;
            document.getElementById('reg').style.display = "none";
            document.getElementById('clicker').style.display = "flex";
            
            // Сразу устанавливаем соединение (Тоже глянь Макс)
            var ws = new WebSocket("ws://127.0.0.1:8000/ws"); #ТУТ ТОЖЕ!!!!
            
            ws.onopen = function(e) {
                ws.send(telegramId);
            }
            
            // Остальной код обработчиков (пока я сам даже не понял, подрузамеваетсяс WebSocket вроде, нужно, чтобы Макс глянул)
        }
        
        document.getElementById('regbtn').addEventListener('click', () => {
            // Оригинальный код обработки кнопки...
        });
    });
</script>"""
