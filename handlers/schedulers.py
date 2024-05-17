import asyncio
from datetime import datetime

from aiogram.exceptions import TelegramBadRequest
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler_di import ContextSchedulerDecorator

from config import bot, redis_host, redis_pass
from database.channelsandmsgs import ChannelsAndMsgsQs
from database.package_pins import PackagePinsQs
from database.package_posts import PackagePostsQs
from keyboards.user_kbs import channel_msg_links_kb

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
    country = sch_msg[3]
    channels = sch_msg[4]

    counter = 0

    for channel_id in channels:
        if counter % 10 == 0:
            await asyncio.sleep(1)

        try:
            if photo:
                try:
                    message = await bot.send_photo(channel_id, photo, caption=text, reply_markup=channel_msg_links_kb(country))
                except TelegramBadRequest:
                    await bot.send_photo(channel_id, photo)
                    message = await bot.send_message(channel_id, text, reply_markup=channel_msg_links_kb(country))
            else:
                message = await bot.send_message(channel_id, text, reply_markup=channel_msg_links_kb(country))

            if pin:
                await bot.pin_chat_message(channel_id, message.message_id, disable_notification=True)
                await add_unpin_msg_job(sch_msg_id, message.message_id, pin)
        except Exception as e:
            print(e)

        counter += 1

    if pin:
        pass
    else:
        await ChannelsAndMsgsQs.del_sch_msgs(sch_msg_id)


async def add_unpin_msg_job(sch_msg_id: int, unpin_msg_id: int, date_time: datetime):
    scheduler.add_job(unpin_msg, "date", run_date=date_time, kwargs={'sch_msg_id': sch_msg_id,
                                                                     'msg_id': unpin_msg_id},
                                                                    timezone='Europe/Moscow')


async def unpin_msg(sch_msg_id: int, msg_id: int):
    sch_msg = await ChannelsAndMsgsQs.get_ref(sch_msg_id)

    channels = sch_msg[4]

    for channel_id in channels:
        try:
            await bot.unpin_chat_message(channel_id, msg_id)
        except Exception as e:
            print(e)

    await ChannelsAndMsgsQs.del_sch_msgs(sch_msg_id)


async def add_package_posts_job(package_id: int, date_time: datetime):
    scheduler.add_job(del_package_posts, "date", run_date=date_time, kwargs={'package_id': package_id},
                      timezone='Europe/Moscow')


async def del_package_posts(package_id: int):
    try:
        await PackagePostsQs.delete_user(package_id)
    except Exception:
        pass


async def add_package_pins_job(package_id: int, date_time: datetime):
    scheduler.add_job(del_package_pins, "date", run_date=date_time, kwargs={'package_id': package_id},
                      timezone='Europe/Moscow')


async def del_package_pins(package_id: int):
    try:
        await PackagePinsQs.delete_user(package_id)
    except Exception:
        pass

