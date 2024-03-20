from datetime import datetime, date

from sqlalchemy import select

from database.channels import ChannelsQs
from database.channelsandmsgs import ChannelsAndMsgsQs
from database.db_conn import async_session_factory
from database.models import ScheduledMsgs, BufferCities
from handlers.schedulers import add_scheduler_job


class SchMsgsQs:
    @staticmethod
    async def add_sch_msg_adm(user_id: int, date_time: datetime, text: str, photo: str = None, pin: date = None):
        try:
            async with async_session_factory() as session:
                stmt = ScheduledMsgs(user_id=user_id, msg_text=text, date_time=date_time, photo=photo, pin=pin)
                session.add(stmt)
                await session.commit()

                channels = await ChannelsQs.get_channels_id_ref_admin()
                await ChannelsAndMsgsQs.add_ref(stmt.id, channels)
                await add_scheduler_job(stmt.id, stmt.date_time)
        except Exception as e:
            print(e)

    @staticmethod
    async def add_sch_msg_user(user_id: int, date_time: datetime, text: str, cities: str, photo: str = None, pin: date = None):
        try:
            async with async_session_factory() as session:
                stmt = ScheduledMsgs(user_id=user_id, msg_text=text, date_time=date_time, photo=photo, pin=pin)
                session.add(stmt)
                await session.commit()

                cities_list = cities.split()

                channels = await ChannelsQs.get_channels_id_ref_user(cities_list)
                await ChannelsAndMsgsQs.add_ref(stmt.id, channels)
                await add_scheduler_job(stmt.id, stmt.date_time)
        except Exception as e:
            print(e)

    @staticmethod
    async def add_buffer_cities(user_id: int, country: str, cities: str):
        try:
            async with async_session_factory() as session:
                stmt = BufferCities(user_id=user_id, country=country, cities=cities)
                session.add(stmt)
                await session.commit()
        except Exception as e:
            print(e)

    @staticmethod
    async def get_buffer_cities(user_id: int):
        try:
            async with async_session_factory() as session:
                query = select(BufferCities.country, BufferCities.cities).where(BufferCities.user_id == user_id)
                res = await session.execute(query)
                buffer = res.one()
        except Exception as e:
            print(e)
        else:
            return buffer


    @staticmethod
    async def del_buffer(user_id: int, country: str, cities: str):
        try:
            async with async_session_factory() as session:
                stmt = BufferCities(user_id=user_id, country=country, cities=cities)
                session.add(stmt)
                await session.commit()
        except Exception as e:
            print(e)
