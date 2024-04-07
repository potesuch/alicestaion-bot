import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

from .data import config
from .handlers import unauthorized, authorized, conversation


async def on_startup(bot: Bot):
    print(f'{config.BASE_WEBHOOK_URL}{config.WEBHOOK_PATH}')
    await bot.set_webhook(f'{config.BASE_WEBHOOK_URL}{config.WEBHOOK_PATH}')


async def on_shutdown(bot: Bot):
    await bot.delete_webhook()


def main():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s | %(levelname)s : %(message)s')
    storage = RedisStorage.from_url(f'redis://{config.REDIS_HOST}:'
                                    f'{config.REDIS_PORT}/{config.REDIS_DB}')
    dp = Dispatcher(storage=storage)
    dp.include_routers(unauthorized.router, authorized.router,
                       conversation.router)
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    bot = Bot(token=config.BOT_TOKEN)
    app = web.Application()
    webhook_request_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot
    )
    webhook_request_handler.register(app, path=config.WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
    web.run_app(app, host=config.WEB_SERVER_HOST, port=int(config.WEB_SERVER_PORT))


if __name__ == '__main__':
    main()
