import asyncio
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import bot
from database.channelsandmsgs import ChannelsAndMsgsQs

scheduler = AsyncIOScheduler()

async def start_scheduler():
    scheduler.configure({'apscheduler.daemon': False})
    scheduler.start()

async def add_scheduler_job(sch_msg_id: int, date_time: datetime):
    scheduler.add_job(send_sch_msg, "date", run_date=date_time, kwargs={'sch_msg_id': sch_msg_id},
                      timezone='Europe/Moscow')


async def send_sch_msg(sch_msg_id: int):
    sch_msg = await ChannelsAndMsgsQs.get_ref(sch_msg_id)

    text = sch_msg[0]
    photo = sch_msg[1]
    channels = sch_msg[2]

    counter = 0

    for channel_id in channels:
        if counter % 10 == 0:
            await asyncio.sleep(1)

        try:
            if photo:
                await bot.send_photo(channel_id, photo, caption=text)
            else:
                await bot.send_message(channel_id, text)
        except Exception:
            pass

        counter += 1
