from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Инициализация бота
bot = Bot(token="YOUR_BOT_TOKEN")
dp = Dispatcher(bot)

# Создаем основную клавиатуру
main_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True,
    one_time_keyboard=False
).add(
    KeyboardButton('🎮 Начать игру'),
    KeyboardButton('🔄 Получить ссылку')
)

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    """Обработчик команды /start"""
    # Создаем инлайн-кнопку для старта игры
    start_button = InlineKeyboardMarkup()
    start_button.add(InlineKeyboardButton(
        text="▶️ Играть сейчас", 
        url="https://example-game.com/play"  # Временная ссылка
    ))
    
    await message.answer(
        "🎮 Добро пожаловать в Clicker Game!\n\n"
        "Нажмите кнопку ниже, чтобы начать играть:",
        reply_markup=main_keyboard
    )
    await message.answer(
        "Перейдите в игру:",
        reply_markup=start_button
    )

@dp.message_handler(lambda message: message.text == '🎮 Начать игру')
async def start_game(message: types.Message):
    """Обработчик кнопки начала игры"""
    game_button = InlineKeyboardMarkup()
    game_button.add(InlineKeyboardButton(
        text="🔵 Играть", 
        url="https://example-game.com/play"
    ))
    
    await message.answer(
        "Нажмите кнопку для перехода в игру:",
        reply_markup=game_button
    )

@dp.message_handler(lambda message: message.text == '🔄 Получить ссылку')
@dp.message_handler(commands=['game'])
async def game_link_handler(message: types.Message):
    """Обработчик получения ссылки на игру"""
    game_button = InlineKeyboardMarkup()
    game_button.add(InlineKeyboardButton(
        text="🔗 Перейти к игре", 
        url="https://example-game.com/play"
    ))
    
    await message.answer(
        "Ваша ссылка на игру:",
        reply_markup=game_button
    )

@dp.message_handler()
async def other_messages_handler(message: types.Message):
    """Обработчик всех остальных сообщений"""
    await message.answer(
        "Используйте кнопки ниже для навигации:",
        reply_markup=main_keyboard
    )

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
