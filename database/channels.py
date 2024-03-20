from sqlalchemy import select, distinct, update, asc, delete

from database.db_conn import async_session_factory
from database.models import Channels


class ChannelsQs:
    @staticmethod
    async def get_countries():
        try:
            async with async_session_factory() as session:
                query = select(distinct(Channels.country)).order_by(Channels.country)
                res = await session.execute(query)
                countries = res.scalars().all()
        except Exception as e:
            print(e)
        else:
            return countries

    @staticmethod
    async def get_cities(country: str, cat: str):
        try:
            async with async_session_factory() as session:
                if cat == 'vac':
                    query = select(Channels.city, Channels.price_vac).where(Channels.country == country).order_by(
                        Channels.city)
                elif cat == 'ad':
                    query = select(Channels.city, Channels.price_ad).where(Channels.country == country).order_by(
                        Channels.city)
                res = await session.execute(query)
                cities = res.all()
        except Exception as e:
            print(e)
        else:
            return cities

    @staticmethod
    async def get_user_cities(cities: list):
        try:
            async with async_session_factory() as session:
                query = select(Channels.city, Channels.price_vac).where(Channels.city.in_(cities)).order_by(
                    Channels.city)
                res = await session.execute(query)
                cities = res.all()
        except Exception as e:
            print(e)
        else:
            return cities

    @staticmethod
    async def get_channels():
        try:
            async with async_session_factory() as session:
                query = select(Channels.channel_name, Channels.country).order_by(asc(Channels.channel_name))
                res = await session.execute(query)
                channels = res.all()
        except Exception as e:
            print(e)
        else:
            return channels

    @staticmethod
    async def get_channels_id_ref_admin():
        try:
            async with async_session_factory() as session:
                query = select(Channels.id)
                res = await session.execute(query)
                channels_id_ref = res.scalars().all()
        except Exception as e:
            print(e)
        else:
            return channels_id_ref

    @staticmethod
    async def get_channels_id_ref_user(cities: list):
        try:
            async with async_session_factory() as session:
                query = select(Channels.id).where(Channels.city.in_(cities))
                res = await session.execute(query)
                channels_id_ref = res.scalars().all()
        except Exception as e:
            print(e)
        else:
            return channels_id_ref

    @staticmethod
    async def add_channel(ch_id: int, ch_name: str, country: str = None):
        try:
            async with async_session_factory() as session:
                stmt = Channels(channel_id=ch_id, channel_name=ch_name, country=country)
                session.add(stmt)
                await session.commit()
        except Exception as e:
            print(e)

    @staticmethod
    async def add_channel_params_new_country(country: str, city: str, price_vac: int, price_ad: int):
        try:
            async with async_session_factory() as session:
                stmt = update(Channels).where(Channels.channel_id.is_not(None) & Channels.city.is_(None)).values(
                                                                                      country=country,
                                                                                      city=city,
                                                                                      price_vac=price_vac,
                                                                                      price_ad=price_ad)
                await session.execute(stmt)
                await session.commit()
        except Exception as e:
            print(e)

    @staticmethod
    async def add_channel_params(city: str, price_vac: int, price_ad: int):
        try:
            async with async_session_factory() as session:
                stmt = update(Channels).where(Channels.channel_id.is_not(None) & Channels.city.is_(None)).values(
                                                                                      city=city,
                                                                                      price_vac=price_vac,
                                                                                      price_ad=price_ad)
                await session.execute(stmt)
                await session.commit()
        except Exception as e:
            print(e)

    @staticmethod
    async def channel_name_exist(name: str):
        try:
            async with async_session_factory() as session:
                query = select(Channels.channel_name).where(Channels.channel_name == name)
                res = await session.execute(query)
                channel_name = res.scalars().one()
        except Exception as e:
            print(e)
        else:
            return channel_name

    @staticmethod
    async def del_channel_by_name(name: str):
        try:
            async with async_session_factory() as session:
                query = delete(Channels).where(Channels.channel_name == name)
                await session.execute(query)
                await session.commit()
        except Exception as e:
            print(e)

