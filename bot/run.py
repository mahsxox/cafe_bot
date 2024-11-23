import asyncio
import logging
from aiogram import Bot, Dispatcher
from app.handlers import router

bot = Bot(token= '8046550392:AAFGrOjyqLmSqVs2y8JXXOzG7czsBWw5r8o')
dp = Dispatcher()

async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
