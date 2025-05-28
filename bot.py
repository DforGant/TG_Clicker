import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Загрузка токена
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

# Инициализация бота
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Главное меню
main_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=False
).add(
    KeyboardButton('🎮 Начать игру'),
    KeyboardButton('🔄 Получить ссылку')
)

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    game_button = InlineKeyboardMarkup()
    game_button.add(InlineKeyboardButton(
        text="▶️ Играть сейчас", 
        url="https://example-game.com/play"
    ))
    
    await message.answer(
        "🎮 Добро пожаловать в Clicker Game!\n\n"
        "Нажмите кнопку ниже, чтобы начать играть:",
        reply_markup=main_keyboard
    )
    await message.answer(
        "Перейдите в игру:",
        reply_markup=game_button
    )

@dp.message_handler(lambda message: message.text == '🎮 Начать игру')
async def start_game(message: types.Message):
    game_button = InlineKeyboardMarkup()
    game_button.add(InlineKeyboardButton(
        text="🔵 Играть", 
        url="https://example-game.com/play"
    ))
    await message.answer("Нажмите кнопку для перехода в игру:", reply_markup=game_button)

@dp.message_handler(lambda message: message.text == '🔄 Получить ссылку')
async def game_link_handler(message: types.Message):
    game_button = InlineKeyboardMarkup()
    game_button.add(InlineKeyboardButton(
        text="🔗 Перейти к игре", 
        url="https://example-game.com/play"
    ))
    await message.answer("Ваша ссылка на игру:", reply_markup=game_button)

@dp.message_handler()
async def other_messages_handler(message: types.Message):
    await message.answer("Используйте кнопки ниже:", reply_markup=main_keyboard)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
