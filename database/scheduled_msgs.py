from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from database.channels import ChannelsQs
from database.channelsandmsgs import ChannelsAndMsgsQs
from database.db_conn import async_session_factory
from database.models import ScheduledMsgs, ChannelsAndMsgs
from handlers.schedulers import add_sch_msg_job


class SchMsgsQs:
    @staticmethod
    async def add_sch_msg_user(user_id: int, date_time: datetime, text: str, cities: str, photo: str = None,
                               pin: datetime = None):
        try:
            async with async_session_factory() as session:
                stmt = ScheduledMsgs(user_id=user_id, msg_text=text, date_time=date_time, photo=photo, pin=pin)
                session.add(stmt)
                await session.commit()

                cities_list = cities.split(',')

                channels = await ChannelsQs.get_channels_id_ref_user(cities_list)
                await ChannelsAndMsgsQs.add_ref(stmt.id, channels)
                await add_sch_msg_job(stmt.id, stmt.date_time)
        except Exception as e:
            print(e)

    @staticmethod
    async def get_sch_msgs_user(user_id: int):
        try:
            async with async_session_factory() as session:
                query = select(ScheduledMsgs.id, ScheduledMsgs.msg_text, ScheduledMsgs.date_time).where(
                    ScheduledMsgs.user_id == user_id).order_by(ScheduledMsgs.date_time)
                res = await session.execute(query)
                sch_msgs = res.all()

        except Exception as e:
            print(e)
        else:
            return sch_msgs

    @staticmethod
    async def get_sch_msg(msg_id: int):
        try:
            async with async_session_factory() as session:
                query = select(ScheduledMsgs.photo, ScheduledMsgs.msg_text, ScheduledMsgs.date_time).where(
                    ScheduledMsgs.id == msg_id)
                res = await session.execute(query)
                sch_msgs = res.one()

        except Exception as e:
            print(e)
        else:
            return sch_msgs

    @staticmethod
    async def check_time(date_time, cities):
        try:
            async with async_session_factory() as session:
                query = select(ScheduledMsgs.id, ScheduledMsgs.date_time).where(
                    ScheduledMsgs.date_time == date_time)
                res = await session.execute(query)
                exist = res.all()

                if exist:
                    cities_list = cities.split(',')

                    query = select(ChannelsAndMsgs).where(
                        ChannelsAndMsgs.msg_id == exist[0][0]).options(selectinload(ChannelsAndMsgs.channel))
                    res = await session.execute(query)
                    channels_ref = res.scalars().all()

                    for ref in channels_ref:
                        if ref.channel.city in cities_list:
                            flag = True
                            break
                        else:
                            flag = False
                else:
                    flag = False

        except Exception as e:
            print(e)
        else:
            return flag

    @staticmethod
    async def update_text(msg_id: int, text):
        try:
            async with async_session_factory() as session:
                stmt = update(ScheduledMsgs).where(ScheduledMsgs.id == msg_id).values(msg_text=text)
                await session.execute(stmt)
                await session.commit()
        except Exception as e:
            print(e)

    @staticmethod
    async def update_photo(msg_id: int, photo):
        try:
            async with async_session_factory() as session:
                stmt = update(ScheduledMsgs).where(ScheduledMsgs.id == msg_id).values(photo=photo)
                await session.execute(stmt)
                await session.commit()
        except Exception as e:
            print(e)
