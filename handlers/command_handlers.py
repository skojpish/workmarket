from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from config import master_id
from keyboards.admin_kbs import admin_kb
from keyboards.menu_kbs import start_kb
from layouts.handlers_layouts import start_message_lo

router = Router()


@router.message(Command("start"))
async def cmd_start(msg: Message) -> None:
    if msg.from_user.id == master_id:
        await start_message_lo(msg, admin_kb)
    else:
        await start_message_lo(msg, start_kb)

