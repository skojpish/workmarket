from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database.db_conn import async_session_factory
from database.models import ChannelsAndMsgs


class ChannelsAndMsgsQs:
    @staticmethod
    async def add_ref(sch_msg: int, channels: list):
        try:
            async with async_session_factory() as session:
                rows = []
                for channel in channels:
                    stmt = ChannelsAndMsgs(msg_id=sch_msg, channel_id=channel)
                    rows.append(stmt)
                session.add_all(rows)
                await session.commit()
        except Exception as e:
            print(e)

    @staticmethod
    async def get_ref(msg_id: int):
        try:
            async with async_session_factory() as session:
                query = select(ChannelsAndMsgs).where(
                    ChannelsAndMsgs.msg_id == msg_id).options(selectinload(ChannelsAndMsgs.msg))
                res = await session.execute(query)
                sch_msg_ref = res.scalars().all()

                query = select(ChannelsAndMsgs).where(
                    ChannelsAndMsgs.msg_id == msg_id).options(selectinload(ChannelsAndMsgs.channel))
                res = await session.execute(query)
                channels_ref = res.scalars().all()

                channels = []

                for ref in channels_ref:
                    channels.append(ref.channel.channel_id)

                sch_msg_data = [sch_msg_ref[0].msg.msg_text, sch_msg_ref[0].msg.photo, channels]

        except Exception as e:
            print(e)
        else:
            return sch_msg_data
