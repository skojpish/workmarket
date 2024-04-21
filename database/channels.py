from sqlalchemy import select, update, delete, distinct, and_

from database.db_conn import async_session_factory
from database.models import Channels, ChannelsInfo


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
    async def get_cities(cat: str, starting_point: int, user_cities: list):
        try:
            async with async_session_factory() as session:
                if cat == 'vac':
                    query = select(Channels.city, Channels.price_vac).where(and_(Channels.country == 'Россия',
                                                                                Channels.city.notin_(user_cities))
                        ).order_by(
                        Channels.city).limit(101).offset(starting_point)
                elif cat == 'ad':
                    query = select(Channels.city, Channels.price_ad).where(Channels.country == 'Россия').order_by(
                        Channels.city).limit(101).offset(starting_point)
                res = await session.execute(query)
                cities = res.all()
        except Exception as e:
            print(e)
        else:
            return cities

    @staticmethod
    async def get_all_cities(cat: str):
        try:
            async with async_session_factory() as session:
                if cat == 'vac':
                    query = select(Channels.city, Channels.price_vac).where(Channels.country == 'Россия').order_by(
                        Channels.city)
                elif cat == 'ad':
                    query = select(Channels.city, Channels.price_ad).where(Channels.country == 'Россия').order_by(
                        Channels.city)
                res = await session.execute(query)
                cities = res.all()
        except Exception as e:
            print(e)
        else:
            return cities

    @staticmethod
    async def get_cities_admin(country: str, starting_point: int, admin_cities: list):
        try:
            async with async_session_factory() as session:
                query = select(Channels.city).where(and_(Channels.country == country,
                                                         Channels.city.notin_(admin_cities))).order_by(
                    Channels.city).limit(101).offset(starting_point)
                res = await session.execute(query)
                cities = res.scalars().all()
        except Exception as e:
            print(e)
        else:
            return cities

    @staticmethod
    async def get_all_cities_admin(country: str):
        try:
            async with async_session_factory() as session:
                query = select(Channels.city).where(Channels.country == country).order_by(
                    Channels.city)
                res = await session.execute(query)
                cities = res.scalars().all()
        except Exception as e:
            print(e)
        else:
            return cities

    @staticmethod
    async def get_user_cities(cities: list, cat: str):
        try:
            async with async_session_factory() as session:
                if cat == 'vac':
                    query = select(Channels.city, Channels.price_vac).where(Channels.city.in_(cities)).order_by(
                        Channels.city)
                else:
                    query = select(Channels.city, Channels.price_ad).where(Channels.city.in_(cities)).order_by(
                        Channels.city)
                res = await session.execute(query)
                cities = res.all()
        except Exception as e:
            print(e)
        else:
            return cities

    @staticmethod
    async def get_channels(starting_point):
        try:
            async with async_session_factory() as session:
                query = select(Channels.channel_name, Channels.country, Channels.price_vac, Channels.price_ad).order_by(
                    Channels.channel_name).limit(11).offset(starting_point)
                res = await session.execute(query)
                channels = res.all()
        except Exception as e:
            print(e)
        else:
            return channels

    @staticmethod
    async def get_all_channels():
        try:
            async with async_session_factory() as session:
                query = select(Channels.channel_name).where(Channels.country == 'Россия').order_by(
                    Channels.channel_name)
                res = await session.execute(query)
                channels = res.scalars().all()
        except Exception as e:
            print(e)
        else:
            return channels

    @staticmethod
    async def get_channels_id_ref_admin(country):
        try:
            async with async_session_factory() as session:
                query = select(Channels.id).where(Channels.country == country)
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
    async def add_channel(ch_id: int, ch_name: str, country: str,
                          city: str = None, price_vac: int = None, price_ad: int = None):
        try:
            async with async_session_factory() as session:
                stmt = Channels(channel_id=ch_id, channel_name=ch_name, country=country, city=city, price_vac=price_vac,
                                price_ad=price_ad)
                session.add(stmt)
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

    @staticmethod
    async def update_price(channel_name, new_price, cat):
        try:
            async with async_session_factory() as session:
                if cat == 'vac':
                    stmt = update(Channels).where(Channels.channel_name == channel_name).values(price_vac=new_price)
                else:
                    stmt = update(Channels).where(Channels.channel_name == channel_name).values(price_ad=new_price)
                await session.execute(stmt)
                await session.commit()
        except Exception as e:
            print(e)

    @staticmethod
    async def add_channel_callback(ch_id: int, ch_name: str):
        try:
            async with async_session_factory() as session:
                stmt = ChannelsInfo(ch_id=ch_id, ch_name=ch_name)
                session.add(stmt)
                await session.commit()
        except Exception as e:
            print(e)
        else:
            return stmt.id

    @staticmethod
    async def get_ch_info(callback_id: int):
        try:
            async with async_session_factory() as session:
                query = select(ChannelsInfo.ch_id, ChannelsInfo.ch_name).where(ChannelsInfo.id == callback_id)
                res = await session.execute(query)
                channel = res.one()

                query = delete(ChannelsInfo).where(ChannelsInfo.id == callback_id)
                await session.execute(query)
                await session.commit()
        except Exception as e:
            print(e)
        else:
            return channel

    @staticmethod
    async def get_channels_names():
        try:
            async with async_session_factory() as session:
                query = select(Channels.channel_id, Channels.channel_name)
                res = await session.execute(query)
                channels_names = res.all()
        except Exception as e:
            print(e)
        else:
            return channels_names

    @staticmethod
    async def update_ch_name(ch_id: int, ch_name: str):
        try:
            async with async_session_factory() as session:
                stmt = update(Channels).where(Channels.channel_id == ch_id).values(channel_name=ch_name)
                await session.execute(stmt)
                await session.commit()
        except Exception as e:
            print(e)
