import asyncio
import logging
import handlers
from aiogram import Dispatcher
from bot import bot
from db.utils import Database

logger = logging.getLogger(__name__)


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format='%(filename)s:%(lineno)d %(levelname)-8s [%(asctime)s] - %(name)s - %(message)s')
    logging.info('Starting bot')
    await Database.init_db()
    loop = asyncio.get_event_loop()
    loop.create_task(handlers.scheduler())

    dp = Dispatcher()
    dp.include_router(handlers.router)

    try:
        # Удаляем вебхук (если использовали webhook ранее)
        await bot.delete_webhook(
            drop_pending_updates=True,
            request_timeout=150
        )

        # Запускаем поллинг для обработки входящих сообщений
        await dp.start_polling(bot)

    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        # Всегда закрываем сессию при завершении
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())

