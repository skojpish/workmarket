from sqlalchemy import select, delete

from database.db_conn import async_session_factory
from database.models import DeleteMsgs


class DelMsgsQs:
    @staticmethod
    async def add_msg_id(user_id, msg_id):
        try:
            async with async_session_factory() as session:
                msg = DeleteMsgs(user_id=user_id, msg_id=msg_id)
                session.add(msg)
                await session.commit()
        except Exception as e:
            print(e)

    @staticmethod
    async def get_msgs(user_id):
        try:
            async with async_session_factory() as session:
                query = select(DeleteMsgs.msg_id).where(DeleteMsgs.user_id == user_id).order_by(DeleteMsgs.id)
                res = await session.execute(query)
                msgs = res.scalars().all()
        except Exception as e:
            print(e)
        else:
            return msgs

    @staticmethod
    async def del_msgs_id(user_id):
        try:
            async with async_session_factory() as session:
                query = delete(DeleteMsgs).where(DeleteMsgs.user_id == user_id)
                await session.execute(query)
                await session.commit()
        except Exception as e:
            print(e)

    @staticmethod
    async def del_msg_id(user_id, msg_id):
        try:
            async with async_session_factory() as session:
                query = delete(DeleteMsgs).where((DeleteMsgs.user_id == user_id) & (DeleteMsgs.msg_id == msg_id))
                await session.execute(query)
                await session.commit()
        except Exception as e:
            print(e)
