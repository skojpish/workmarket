from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BotCommand

from config import bot, masters
from database.channelsandmsgs import ChannelsAndMsgsQs
from database.delete_msgs import DelMsgsQs
from database.scheduled_msgs import SchMsgsQs
from keyboards.admin_kbs import admin_kb
from keyboards.menu_kbs import start_kb
from keyboards.user_kbs import edit_posts_kb
from layouts.handlers_layouts import start_message_lo, del_messages_lo

router = Router()


async def setup_bot_commands():
    bot_commands = [
        BotCommand(command="/menu", description="Вернуться в главное меню"),
        BotCommand(command="/posts", description="Список запланированных публикаций")
    ]
    return await bot.set_my_commands(bot_commands)


@router.message((F.text == '/start') | (F.text == '/menu'))
async def cmd_start(msg: Message, state: FSMContext) -> None:
    await del_messages_lo(msg.from_user.id)
    if msg.from_user.id in masters:
        await start_message_lo(msg, state, admin_kb)
    else:
        await start_message_lo(msg, state, start_kb)


@router.message(F.text == '/posts')
async def cmd_posts(msg: Message, state: FSMContext) -> None:
    await state.clear()

    await bot.delete_message(msg.from_user.id, msg.message_id)

    sch_msgs = await SchMsgsQs.get_sch_msgs_user(msg.from_user.id)

    if sch_msgs:
        msgs = [msg_data[0] for msg_data in sch_msgs]

        msg_channels = []

        msg_ids = {}

        for msg_id in msgs:
            channels = await ChannelsAndMsgsQs.get_msg_channels(msg_id)
            msg_channels.append(channels)

            msg_ids[f'{msgs.index(msg_id) + 1}'] = msg_id

        await state.update_data(msg_ids=msg_ids)

        double_new_line = "\n\n"

        def post_layout(index, text, date, time, chnnls):
            return (f"<b>{index}.</b>\nКраткий текст: {text[0:15]}...\n"
                    f"Дата: {date}\n"
                    f"Время: {time}\n"
                    f"Каналы: {' '.join(chnnls)}")

        message = await msg.answer(f"""<b>Список запланированных публикаций</b>\n\n{double_new_line.join(
            post_layout(i+1, sch_msgs[i][1], sch_msgs[i][2].strftime('%d.%m.%Y'), sch_msgs[i][2].strftime('%H:%M'), 
                        msg_channels[i])
            for i in range(len(msgs)))}""", reply_markup=edit_posts_kb())
    else:
        message = await msg.answer('У вас еще нет запланированных публикаций')

    await del_messages_lo(msg.from_user.id)
    await DelMsgsQs.add_msg_id(msg.from_user.id, message.message_id)

