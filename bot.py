from aiogram import Bot, Dispatcher, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import Config
from models import User
import asyncio

bot = Bot(token=Config.BOT_TOKEN)
dp = Dispatcher()

@dp.message(commands=['start'])
async def cmd_start(message: types.Message):
    user, created = await User.get_or_create(
        telegram_id=message.from_user.id,
        defaults={'total_clicks': 0}
    )
    
    kb = InlineKeyboardBuilder()
    kb.button(text="Открыть кликер", web_app=types.WebAppInfo(
        url=f"{Config.SERVER_URL}/game?user_id={message.from_user.id}"
    ))
    
    text = "Вы зарегистрированы! " if created else "С возвращением! "
    await message.answer(f"{text}Ваш баланс: {user.total_clicks} кликов", 
                        reply_markup=kb.as_markup())

@dp.message(commands=['game'])
async def cmd_game(message: types.Message):
    if not await User.exists(telegram_id=message.from_user.id):
        await message.answer("Сначала зарегистрируйтесь с помощью /start")
        return
        
    kb = InlineKeyboardBuilder()
    kb.button(text="Открыть кликер", web_app=types.WebAppInfo(
        url=f"{Config.SERVER_URL}/game?user_id={message.from_user.id}"
    ))
    await message.answer("Играть", reply_markup=kb.as_markup())

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
