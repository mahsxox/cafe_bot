import asyncio
import logging
from aiogram import Bot, Dispatcher
from app.handlers import router

# Создаём бота и диспетчер
bot = Bot(token='8046550392:AAFGrOjyqLmSqVs2y8JXXOzG7czsBWw5r8o')
dp = Dispatcher()

async def main():
    dp.include_router(router)  # Подключаем обработчики
    await dp.start_polling(bot)  # Запускаем бота

# Точка входа
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)  # Логирование
    try:
        asyncio.run(main())  # Запуск бота
    except KeyboardInterrupt:
        print('Exit')  # Завершение
