from datetime import datetime

from sqlalchemy import delete, select, update

from database.db_conn import async_session_factory
from database.models import PackagePosts


class PackagePostsQs:
    @staticmethod
    async def add_posts_package(user_id: int, publ_count: int, cat: str, del_datetime: datetime):
        try:
            async with async_session_factory() as session:
                stmt = PackagePosts(user_id=user_id, publ_count=publ_count, category=cat, del_datetime=del_datetime)
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
                query = delete(PackagePosts).where(PackagePosts.id == package_id)
                await session.execute(query)
                await session.commit()
        except Exception as e:
            print(e)

    @staticmethod
    async def get_user(user_id: int):
        try:
            async with async_session_factory() as session:
                query = select(PackagePosts.publ_count, PackagePosts.category).where(PackagePosts.user_id == user_id)
                res = await session.execute(query)
                users_pckg_info = res.one()
        except Exception:
            pass
        else:
            return users_pckg_info

    @staticmethod
    async def subtract_one_publ(user_id: int):
        try:
            async with async_session_factory() as session:
                stmt = update(PackagePosts).where(PackagePosts.user_id == user_id).values(
                    publ_count=PackagePosts.publ_count-1)
                await session.execute(stmt)
                await session.commit()
        except Exception as e:
            print(e)

    @staticmethod
    async def delete_package():
        try:
            async with async_session_factory() as session:
                query = delete(PackagePosts).where(PackagePosts.publ_count == 0)
                await session.execute(query)
                await session.commit()
        except Exception as e:
            print(e)
