"""
Этот модуль является точкой входа для запуска бота. Он создает экземпляры бота и диспетчера, настраивает логирование,
подключает обработчики команд и запускает процесс опроса с помощью метода start_polling.

Основная цель — запуск бота и обеспечение его работы с использованием асинхронных функций.
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from app.handlers import router

# Создаём бота и диспетчер
bot = Bot(token='8046550392:AAFGrOjyqLmSqVs2y8JXXOzG7czsBWw5r8o')
dp = Dispatcher()

async def main():
    """
    Основная асинхронная функция для запуска бота.

    Эта функция подключает маршрутизатор router, который содержит обработчики для различных команд и событий,
    и запускает бота с использованием метода start_polling, чтобы он начал обрабатывать запросы и события.

    Процесс будет продолжаться до тех пор, пока не будет завершен вручную (например, через KeyboardInterrupt).
    """
    dp.include_router(router)  # Подключаем обработчики
    await dp.start_polling(bot)  # Запускаем бота

# Точка входа
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)  # Логирование
    try:
        asyncio.run(main())  # Запуск бота
    except KeyboardInterrupt:
        print('Exit')  # Завершение
