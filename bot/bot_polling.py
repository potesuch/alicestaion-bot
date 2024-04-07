import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from .data import config
from .handlers import unauthorized, authorized, conversation

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s | %(levelname)s : %(message)s')

storage = RedisStorage.from_url(f'redis://{config.REDIS_HOST}:'
                                f'{config.REDIS_PORT}/{config.REDIS_DB}')
bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(storage=storage)


async def main():
    dp.include_routers(unauthorized.router, authorized.router,
                       conversation.router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
