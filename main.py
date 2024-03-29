import asyncio

from aiogram import Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from config import bot, REDIS_URL
from handlers import command_handlers, admin_handlers, vac_handlers, payment_handlers, edit_handlers
from handlers.command_handlers import setup_bot_commands
from handlers.schedulers import start_scheduler


redis_instance = Redis.from_url(REDIS_URL)

storage = RedisStorage(redis=redis_instance)


async def on_startup() -> None:
    await start_scheduler()


async def main() -> None:
    dp = Dispatcher(storage=storage)

    dp.include_routers(command_handlers.router, admin_handlers.router, vac_handlers.router,
                       payment_handlers.router, edit_handlers.router)

    dp.startup.register(on_startup)

    try:
        await setup_bot_commands()
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception:
        print("there is an exception")


if __name__ == "__main__":
    asyncio.run(main())
