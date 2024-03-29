import logging
import sys

from aiogram import Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from config import bot, REDIS_URL
from handlers import command_handlers, admin_handlers, vac_handlers, payment_handlers, edit_handlers
from handlers.command_handlers import setup_bot_commands
from handlers.schedulers import start_scheduler


redis_instance = Redis.from_url(REDIS_URL)

storage = RedisStorage(redis=redis_instance)

WEB_SERVER_HOST = '127.0.0.1'
WEB_SERVER_PORT = 8080

WEBHOOK_PATH = '/webhook'
BASE_WEBHOOK_URL = f"https://workmarketbot.ru"


async def on_startup() -> None:
    await setup_bot_commands()
    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}")
    await start_scheduler()


def main() -> None:
    dp = Dispatcher(storage=storage)

    dp.include_routers(command_handlers.router, admin_handlers.router, vac_handlers.router,
                       payment_handlers.router, edit_handlers.router)

    dp.startup.register(on_startup)

    app = web.Application()

    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )

    webhook_requests_handler.register(app, path=WEBHOOK_PATH)

    setup_application(app, dp, bot=bot)

    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.basicConfig(level=logging.ERROR, stream=sys.stderr)

