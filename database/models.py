from datetime import datetime, date

from sqlalchemy import BigInteger, text, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Channels(Base):
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(primary_key=True)
    channel_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    channel_name: Mapped[str]
    country: Mapped[str] = mapped_column(nullable=True)
    city: Mapped[str] = mapped_column(nullable=True)
    price_vac: Mapped[int] = mapped_column(nullable=True)
    price_ad: Mapped[int] = mapped_column(nullable=True)

    channel_id_ref: Mapped['ChannelsAndMsgs'] = relationship(back_populates='channel')

class DeleteMsgs(Base):
    __tablename__ = "delete_msgs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    msg_id: Mapped[int]


class ScheduledMsgs(Base):
    __tablename__ = "scheduled_msgs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    msg_text: Mapped[str]
    date_time: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('Europe/Moscow', now())"))
    photo: Mapped[str] = mapped_column(nullable=True)
    pin: Mapped[date] = mapped_column(nullable=True)

    msg_id_ref: Mapped['ChannelsAndMsgs'] = relationship(back_populates='msg')


class ChannelsAndMsgs(Base):
    __tablename__ = "channels_and_msgs"

    id: Mapped[int] = mapped_column(primary_key=True)
    msg_id: Mapped[int] = mapped_column(ForeignKey("scheduled_msgs.id"))
    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id"))

    msg: Mapped['ScheduledMsgs'] = relationship(back_populates="msg_id_ref")
    channel: Mapped['Channels'] = relationship(back_populates="channel_id_ref")


class BufferCities(Base):
    __tablename__ = "buffer_cities"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    country: Mapped[str]
    cities: Mapped[str]
