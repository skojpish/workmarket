from datetime import datetime

from sqlalchemy import delete, select, update

from database.db_conn import async_session_factory
from database.models import PackagePins


class PackagePinsQs:
    @staticmethod
    async def add_pins_package(user_id: int, pin_count: int, cat: str, del_datetime: datetime):
        try:
            async with async_session_factory() as session:
                stmt = PackagePins(user_id=user_id, pin_count=pin_count, category=cat, del_datetime=del_datetime)
                session.add(stmt)
                await session.commit()
        except Exception as e:
            print(e)
        else:
            return [stmt.id, stmt.del_datetime]

    @staticmethod
    async def delete_user(package_id: int):
        try:
            async with async_session_factory() as session:
                query = delete(PackagePins).where(PackagePins.id == package_id)
                await session.execute(query)
                await session.commit()
        except Exception as e:
            print(e)

    @staticmethod
    async def get_user(user_id: int):
        try:
            async with async_session_factory() as session:
                query = select(PackagePins.pin_count, PackagePins.category).where(PackagePins.user_id == user_id)
                res = await session.execute(query)
                users_pckg_info = res.one()
        except Exception:
            pass
        else:
            return users_pckg_info

    @staticmethod
    async def subtract_one_pin(user_id: int):
        try:
            async with async_session_factory() as session:
                stmt = update(PackagePins).where(PackagePins.user_id == user_id).values(
                    pin_count=PackagePins.pin_count-1)
                await session.execute(stmt)
                await session.commit()
        except Exception as e:
            print(e)

    @staticmethod
    async def delete_pin_package():
        try:
            async with async_session_factory() as session:
                query = delete(PackagePins).where(PackagePins.pin_count == 0)
                await session.execute(query)
                await session.commit()
        except Exception as e:
            print(e)
