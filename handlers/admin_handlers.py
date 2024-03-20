from datetime import datetime

from aiogram import Router, F
from aiogram.filters import ChatMemberUpdatedFilter, IS_NOT_MEMBER, ADMINISTRATOR
from aiogram.fsm.context import FSMContext
from aiogram.types import ChatMemberUpdated, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import bot, master_id
from database.FSM import AddChannel, DelChannel, MsgAllChannels
from database.channels import ChannelsQs
from database.delete_msgs import DelMsgsQs
from database.scheduled_msgs import SchMsgsQs
from handlers.callback_factories import ChannelCountryCF, ChannelNewCountryCF
from keyboards.admin_kbs import add_channel_kb, channels_management_kb, bot_management_kb, sch_admin_final_kb, photo_adm_kb, \
    end_scheduled_kb
from layouts.handlers_layouts import del_messages_lo

router = Router()

# Add bot as admin of channel


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=IS_NOT_MEMBER >> ADMINISTRATOR))
async def bot_added_as_admin(event: ChatMemberUpdated):
    countries = await ChannelsQs.get_countries()

    def country_admin_kb() -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        if countries:
            for country in countries:
                kb.button(
                    text=f"{country}", callback_data=ChannelCountryCF(channel_id=event.chat.id,
                                                                      channel_name=event.chat.title,
                                                                      country=f'{country}')
                )
        kb.button(
            text=f"Добавить страну", callback_data=ChannelNewCountryCF(channel_id=event.chat.id,
                                                                       channel_name=event.chat.title)
        )
        kb.add(InlineKeyboardButton(
            text="Отмена", callback_data="cancel"
        ))
        kb.adjust(1)
        return kb.as_markup()

    await bot.send_message(master_id, f"Вы добавили бота в канал {event.chat.title}!\n"
                                                f"Выберите страну, к которой принадлежит канал",
                                                reply_markup=country_admin_kb())


@router.callback_query(ChannelNewCountryCF.filter())
async def add_new_country_admin(callback: CallbackQuery, callback_data: ChannelNewCountryCF, state: FSMContext):
    messages = await DelMsgsQs.get_msgs(master_id)
    if messages:
        for message in messages:
            try:
                await bot.delete_message(master_id, message)
            except Exception:
                pass

    await DelMsgsQs.del_msgs_id(master_id)

    await ChannelsQs.add_channel(callback_data.channel_id, callback_data.channel_name)
    await DelMsgsQs.add_msg_id(master_id, callback.message.message_id)

    await state.set_state(AddChannel.country)
    message = await callback.message.answer("Напишите название страны")

    await DelMsgsQs.add_msg_id(master_id, message.message_id)
    await callback.answer()


@router.callback_query(ChannelCountryCF.filter())
async def add_country_admin(callback: CallbackQuery, callback_data: ChannelCountryCF, state: FSMContext):
    messages = await DelMsgsQs.get_msgs(master_id)
    if messages:
        for message in messages:
            try:
                await bot.delete_message(master_id, message)
            except Exception:
                pass

    await DelMsgsQs.del_msgs_id(master_id)

    await ChannelsQs.add_channel(callback_data.channel_id, callback_data.channel_name, callback_data.country)
    await DelMsgsQs.add_msg_id(master_id, callback.message.message_id)

    await state.set_state(AddChannel.city)
    message = await callback.message.answer("Напишите город")

    await DelMsgsQs.add_msg_id(master_id, message.message_id)
    await callback.answer()


@router.message(AddChannel.country)
async def add_country_state(msg: Message, state: FSMContext):
    await DelMsgsQs.add_msg_id(master_id, msg.message_id)

    await state.update_data(country=msg.text)
    await state.set_state(AddChannel.city)

    message = await msg.answer("Напишите город")

    await DelMsgsQs.add_msg_id(master_id, message.message_id)


@router.message(AddChannel.city)
async def add_city_state(msg: Message, state: FSMContext):
    await DelMsgsQs.add_msg_id(master_id, msg.message_id)

    await state.update_data(city=msg.text)
    await state.set_state(AddChannel.price_vac)

    message = await msg.answer("Напишите стоимость публикации вакансии")

    await DelMsgsQs.add_msg_id(master_id, message.message_id)


@router.message(AddChannel.price_vac)
async def add_price_val_state(msg: Message, state: FSMContext):
    await DelMsgsQs.add_msg_id(master_id, msg.message_id)

    await state.update_data(price_vac=int(msg.text))
    await state.set_state(AddChannel.price_ad)

    message = await msg.answer("Напишите стоимость публикации рекламы")

    await DelMsgsQs.add_msg_id(master_id, message.message_id)


@router.message(AddChannel.price_ad)
async def add_price_ad_state(msg: Message, state: FSMContext):
    await DelMsgsQs.add_msg_id(master_id, msg.message_id)

    await state.update_data(price_ad=int(msg.text))
    data = await state.get_data()

    if len(data) == 4:
        await ChannelsQs.add_channel_params_new_country(**data)
    else:
        await ChannelsQs.add_channel_params(**data)
    await state.clear()

    await del_messages_lo()

    message = await msg.answer("Данные о канале успешно добавлены!", reply_markup=add_channel_kb())

    await DelMsgsQs.add_msg_id(master_id, message.message_id)

# List of channels


@router.callback_query(F.data == 'channels')
async def list_of_channels(callback: CallbackQuery):
    channels = await ChannelsQs.get_channels()

    await callback.message.edit_text("\n".join(f'{channels.index(channel)+1}. {channel[0]} - {channel[1]}'
                                               for channel in channels))
    await callback.message.edit_reply_markup(reply_markup=channels_management_kb())

# Delete channel


@router.callback_query(F.data == 'del_channel')
async def del_channel(callback: CallbackQuery, state: FSMContext):
    await state.set_state(DelChannel.state)
    await callback.message.delete_reply_markup()
    await callback.message.edit_text("Напишите название канала, который вы хотели бы удалить")

    await DelMsgsQs.add_msg_id(master_id, callback.message.message_id)


@router.message(DelChannel.state)
async def del_channel_state(msg: Message, state: FSMContext):
    await DelMsgsQs.add_msg_id(master_id, msg.message_id)
    await state.clear()

    channel_name = await ChannelsQs.channel_name_exist(msg.text)

    if channel_name:
        message = await msg.answer(f"Канал {channel_name} успешно удален", reply_markup=channels_management_kb())
        await ChannelsQs.del_channel_by_name(msg.text)
        await del_messages_lo()
    else:
        await state.set_state(DelChannel.state)
        message = await msg.answer("Вы ввели неправильное название канала, попробуйте еще раз")

    await DelMsgsQs.add_msg_id(master_id, message.message_id)

# Bot management


@router.callback_query(F.data == 'bot_management')
async def bot_management_start(callback: CallbackQuery):
    await callback.message.edit_text("Выберите раздел")
    await callback.message.edit_reply_markup(reply_markup=bot_management_kb())

@router.callback_query(F.data == 'msg_all_channels')
async def send_message_to_all_channels(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(MsgAllChannels.text)

    await callback.message.delete_reply_markup()
    await callback.message.edit_text("Напишите сообщение")

    await DelMsgsQs.add_msg_id(master_id, callback.message.message_id)


@router.message(MsgAllChannels.text)
async def msg_all_channels_text(msg: Message, state: FSMContext):
    await DelMsgsQs.add_msg_id(master_id, msg.message_id)

    await state.update_data(text=msg.text)
    await state.set_state(MsgAllChannels.photo)

    message = await msg.answer("Отправьте фото к посту", reply_markup=photo_adm_kb())

    await DelMsgsQs.add_msg_id(master_id, message.message_id)


@router.callback_query(F.data == 'without_photo_adm')
async def without_photo(callback: CallbackQuery, state: FSMContext):
    await DelMsgsQs.del_msg_id(master_id, callback.message.message_id)

    await state.set_state(MsgAllChannels.date)

    await callback.message.delete_reply_markup()
    await callback.message.edit_text("Введите дату публикации в следующем формате: ДД.ММ.ГГГГ")


@router.message(MsgAllChannels.photo)
async def msg_all_channels_photo(msg: Message, state: FSMContext):
    await DelMsgsQs.add_msg_id(master_id, msg.message_id)

    if msg.photo:
        await state.update_data(photo=msg.photo[-1].file_id)
        await state.set_state(MsgAllChannels.date)
        message = await msg.answer("Введите дату публикации в следующем формате: ДД.ММ.ГГГГ")
    else:
        await state.set_state(MsgAllChannels.photo)
        message = await msg.answer("Отправьте фото к посту", reply_markup=photo_adm_kb())

    await DelMsgsQs.add_msg_id(master_id, message.message_id)


@router.message(MsgAllChannels.date)
async def msg_all_channels_date(msg: Message, state: FSMContext):
    await DelMsgsQs.add_msg_id(master_id, msg.message_id)

    await state.update_data(date=msg.text)
    await state.set_state(MsgAllChannels.time)

    message = await msg.answer("Введите время публикации в следующем формате: ЧЧ:ММ:СС")

    await DelMsgsQs.add_msg_id(master_id, message.message_id)


@router.message(MsgAllChannels.time)
async def msg_all_channels_time(msg: Message, state: FSMContext):
    await DelMsgsQs.add_msg_id(master_id, msg.message_id)
    await del_messages_lo()

    await state.update_data(time=msg.text)
    data = await state.get_data()

    if 'photo' in data:
        await msg.answer_photo(data['photo'], f"Вы ввели следующие данные:\n"
                                                           f"Сообщение: {data['text']}\n"
                                                           f"Дата: {data['date']}\n"
                                                           f"Время: {data['time']}",
                                                            reply_markup=end_scheduled_kb(data))
    else:
        await msg.answer(f"Вы ввели следующие данные:\n"
                                        f"Сообщение: {data['text']}\n"
                                        f"Дата: {data['date']}\n"
                                        f"Время: {data['time']}",
                                        reply_markup=end_scheduled_kb(data))


@router.callback_query(F.data == 'sch_confirm_all_msgs')
async def get_scheduled_info(callback: CallbackQuery, state: FSMContext):
    data_state = await state.get_data()

    date_time = f"{data_state['date']} {data_state['time']}"

    if 'photo' in data_state:

        data = {
            'user_id': callback.from_user.id,
            'date_time': datetime.strptime(date_time, "%d.%m.%Y %H:%M:%S"),
            'text': data_state['text'],
            'photo': data_state['photo'],
        }

        await DelMsgsQs.add_msg_id(master_id, callback.message.message_id)
        await del_messages_lo()
        await SchMsgsQs.add_sch_msg_adm(**data)
        await state.clear()
        await callback.message.answer("Сообщение успешно запланировано!",
                                            reply_markup=sch_admin_final_kb())
    else:

        data = {
            'user_id': callback.from_user.id,
            'date_time': datetime.strptime(date_time, "%d.%m.%Y %H:%M:%S"),
            'text': data_state['text']
        }

        await SchMsgsQs.add_sch_msg_adm(**data)
        await state.clear()
        await callback.message.edit_text("Сообщение успешно запланировано!")
        await callback.message.edit_reply_markup(reply_markup=sch_admin_final_kb())



