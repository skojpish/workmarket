import asyncio

from aiogram import Dispatcher

from config import bot
from handlers import command_handlers, admin_handlers, vac_handlers, payment_handlers
from handlers.schedulers import start_scheduler


async def on_startup() -> None:
    await start_scheduler()

async def main() -> None:
    dp = Dispatcher()

    dp.include_routers(command_handlers.router, admin_handlers.router, vac_handlers.router,
                       payment_handlers.router)

    dp.startup.register(on_startup)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except:
        print("there is an exception")


if __name__ == "__main__":
    asyncio.run(main())
