# main.py
import asyncio
import logging
from aiogram import Bot, Dispatcher
from handlers import callbacks
import database as db
import config

async def on_startup(bot: Bot):
    # Создаем таблицы при запуске
    await db.create_tables()
    print("База данных подключена и таблицы созданы.")

async def on_shutdown(bot: Bot):
    # Закрываем сессию CryptoBot
    await callbacks.cryptopay.close()
    print("Бот выключен")

async def main():
    logging.basicConfig(level=logging.INFO)
    
    # Используем токен из конфига
    bot = Bot(token=config.BOT_TOKEN)
    dp = Dispatcher()

    # Регистрируем события старт/стоп
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.include_router(callbacks.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass