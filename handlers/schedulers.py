import asyncio
from datetime import datetime

from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler_di import ContextSchedulerDecorator

from config import bot, redis_host, redis_pass
from database.channelsandmsgs import ChannelsAndMsgsQs

jobstores = {
    'default': RedisJobStore(jobs_key='dispatched_trips_jobs',
                             run_times_key='dispatched_trips_running',
                             host=redis_host,
                             db=2,
                             port=6379,
                             password=redis_pass)
}

scheduler = ContextSchedulerDecorator(AsyncIOScheduler(timezone='Europe/Moscow', jobstores=jobstores))


async def start_scheduler():
    scheduler.configure({'apscheduler.daemon': False})
    scheduler.start()


async def add_sch_msg_job(sch_msg_id: int, date_time: datetime):
    scheduler.add_job(send_sch_msg, "date", run_date=date_time, kwargs={'sch_msg_id': sch_msg_id},
                      timezone='Europe/Moscow')


async def send_sch_msg(sch_msg_id: int):
    sch_msg = await ChannelsAndMsgsQs.get_ref(sch_msg_id)

    text = sch_msg[0]
    photo = sch_msg[1]
    pin = sch_msg[2]
    channels = sch_msg[3]

    counter = 0

    for channel_id in channels:
        if counter % 10 == 0:
            await asyncio.sleep(1)

        try:
            if photo:
                message = await bot.send_photo(channel_id, photo, caption=text)
            else:
                message = await bot.send_message(channel_id, text)

            if pin:
                await bot.pin_chat_message(channel_id, message.message_id, disable_notification=True)
                await add_unpin_msg_job(sch_msg_id, message.message_id, pin)
            else:
                await ChannelsAndMsgsQs.del_sch_msgs(sch_msg_id)
        except Exception:
            pass

        counter += 1


async def add_unpin_msg_job(sch_msg_id: int, unpin_msg_id: int, date_time: datetime):
    scheduler.add_job(unpin_msg, "date", run_date=date_time, kwargs={'sch_msg_id': sch_msg_id,
                                                                     'msg_id': unpin_msg_id},
                      timezone='Europe/Moscow')


async def unpin_msg(sch_msg_id: int, msg_id: int):
    sch_msg = await ChannelsAndMsgsQs.get_ref(sch_msg_id)

    channels = sch_msg[3]

    for channel_id in channels:
        try:
            await bot.unpin_chat_message(channel_id, msg_id)
        except Exception:
            pass

    await ChannelsAndMsgsQs.del_sch_msgs(sch_msg_id)
