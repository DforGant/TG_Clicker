import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.utils.keyboard import InlineKeyboardBuilder

API_TOKEN = 'YOUR_BOT_API_TOKEN'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message()
async def start(message: types.Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="Открыть кликер", web_app=types.WebAppInfo(url="https://yourdomain.com "))
    await message.answer("Добро пожаловать!", reply_markup=kb.as_markup())

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
