from datetime import datetime, date

from aiogram import Router, F
from aiogram.filters import ChatMemberUpdatedFilter, IS_NOT_MEMBER, ADMINISTRATOR
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import ChatMemberUpdated, InlineKeyboardMarkup, CallbackQuery, Message, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram3_calendar import SimpleCalendar
from aiogram3_calendar.calendar_types import SimpleCalendarCallback

from config import bot, master_id
from database.FSM import AddChannel, DelChannel, MsgAllChannels, AdminCities
from database.channels import ChannelsQs
from database.delete_msgs import DelMsgsQs
from database.scheduled_msgs import SchMsgsQs
from handlers.callback_factories import TimePickerCF, ChannelCountryCF, ChannelNewCountryCF, MsgAllChannelsCF, \
    ListOfChannelsCF, AdminCityCF, AdminCityStatusCF, PinCF
from keyboards.admin_kbs import add_channel_kb, bot_management_kb, photo_adm_kb
from keyboards.time_picker import time_picker_kb
from keyboards.user_kbs import edit_final_kb
from layouts.handlers_layouts import del_messages_lo, order_message_lo, choice_admin_city, time_picker_lo

router = Router()

# Add bot as admin of channel


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=IS_NOT_MEMBER >> ADMINISTRATOR))
async def bot_added_as_admin(event: ChatMemberUpdated):
    countries = await ChannelsQs.get_countries()

    channel = await ChannelsQs.add_channel_callback(event.chat.id, event.chat.title)

    def country_admin_kb() -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        if countries:
            for country in countries:
                kb.button(
                    text=f"{country}", callback_data=ChannelCountryCF(channel=channel,
                                                                      country=f'{country}')
                )
        kb.button(
            text=f"Добавить страну", callback_data=ChannelNewCountryCF(channel=channel)
        )
        kb.adjust(1)
        return kb.as_markup()

    await bot.send_message(master_id, f"Вы добавили бота в канал {event.chat.title}!\n"
                                                f"Выберите страну, к которой принадлежит канал",
                                                reply_markup=country_admin_kb())


@router.callback_query(ChannelNewCountryCF.filter())
async def add_new_country_admin(callback: CallbackQuery, callback_data: ChannelNewCountryCF, state: FSMContext):
    await callback.answer()
    await state.clear()
    await del_messages_lo(callback.from_user.id)

    channel = await ChannelsQs.get_ch_info(callback_data.channel)

    await state.update_data(channel_id=channel[0], channel_name=channel[1])

    await DelMsgsQs.add_msg_id(callback.from_user.id, callback.message.message_id)

    await state.set_state(AddChannel.country)
    message = await callback.message.answer(f"Напишите название страны, "
                                            f"к которой принадлежит канал {channel[1]}")

    await DelMsgsQs.add_msg_id(callback.from_user.id, message.message_id)


@router.callback_query(ChannelCountryCF.filter())
async def add_country_admin(callback: CallbackQuery, callback_data: ChannelCountryCF, state: FSMContext):
    await state.clear()
    await del_messages_lo(callback.from_user.id)

    channel = await ChannelsQs.get_ch_info(callback_data.channel)

    await state.update_data(channel_id=channel[0], channel_name=channel[1],
                            country=callback_data.country)

    await DelMsgsQs.add_msg_id(callback.from_user.id, callback.message.message_id)

    await state.set_state(AddChannel.city)
    message = await callback.message.answer("Напишите город")

    await DelMsgsQs.add_msg_id(callback.from_user.id, message.message_id)
    await callback.answer()


@router.message(AddChannel.country)
async def add_country_state(msg: Message, state: FSMContext):
    await DelMsgsQs.add_msg_id(msg.from_user.id, msg.message_id)

    await state.update_data(country=msg.text)

    await state.set_state(AddChannel.city)

    message = await msg.answer("Напишите город")

    await DelMsgsQs.add_msg_id(msg.from_user.id, message.message_id)


@router.message(AddChannel.city)
async def add_city_state(msg: Message, state: FSMContext):
    await DelMsgsQs.add_msg_id(msg.from_user.id, msg.message_id)

    data = await state.get_data()

    if data['country'] == "Россия":
        await state.update_data(city=msg.text)
        await state.set_state(AddChannel.price_vac)

        message = await msg.answer("Напишите стоимость публикации вакансии")
    else:
        data = await state.get_data()

        d = {
            'ch_id': data['channel_id'],
            'ch_name': data['channel_name'],
            'country': data['country'],
            'city': msg.text
        }

        await ChannelsQs.add_channel(**d)
        message = await msg.answer("Канал успешно добавлен!", reply_markup=add_channel_kb())
        await del_messages_lo(msg.from_user.id)
    await DelMsgsQs.add_msg_id(msg.from_user.id, message.message_id)


@router.message(AddChannel.price_vac)
async def add_price_val_state(msg: Message, state: FSMContext):
    await DelMsgsQs.add_msg_id(msg.from_user.id, msg.message_id)

    await state.update_data(price_vac=int(msg.text))
    await state.set_state(AddChannel.price_ad)

    message = await msg.answer("Напишите стоимость публикации рекламы")

    await DelMsgsQs.add_msg_id(msg.from_user.id, message.message_id)


@router.message(AddChannel.price_ad)
async def add_price_ad_state(msg: Message, state: FSMContext):
    await DelMsgsQs.add_msg_id(msg.from_user.id, msg.message_id)

    await state.update_data(price_ad=int(msg.text))
    data = await state.get_data()

    d = {
        'ch_id': data['channel_id'],
        'ch_name': data['channel_name'],
        'country': data['country'],
        'city': data['city'],
        'price_vac': data['price_vac'],
        'price_ad': data['price_ad']
    }

    await ChannelsQs.add_channel(**d)

    await state.clear()

    await del_messages_lo(msg.from_user.id)

    message = await msg.answer("Данные о канале успешно добавлены!", reply_markup=add_channel_kb())

    await DelMsgsQs.add_msg_id(msg.from_user.id, message.message_id)

# List of channels


@router.callback_query(ListOfChannelsCF.filter())
async def list_of_channels(callback: CallbackQuery, callback_data: ListOfChannelsCF):
    channels = await ChannelsQs.get_channels(callback_data.starting_point)

    if channels:
        def channels_management_kb() -> InlineKeyboardMarkup:
            kb = InlineKeyboardBuilder()
            kb.add(InlineKeyboardButton(
                text="Изменить цены", callback_data="edit_channel_info"
            ))
            kb.add(InlineKeyboardButton(
                text="Удалить канал", callback_data="del_channel"
            ))
            kb.add(InlineKeyboardButton(
                text="Обновить названия", callback_data="update_ch_names"
            ))
            if len(channels) > 10:
                kb.button(
                    text="Показать еще",
                    callback_data=ListOfChannelsCF(starting_point=callback_data.starting_point + 10)
                )
            if callback_data.starting_point > 0:
                kb.button(
                    text="Назад",
                    callback_data=ListOfChannelsCF(starting_point=callback_data.starting_point - 10)
                )
            kb.adjust(1)
            return kb.as_markup()

        def channels_list_text(channel):
            if channel[1] == "Россия":
                return (f'{channels.index(channel) + 1 + callback_data.starting_point}.\n{channel[0]} - {channel[1]}\n'
                        f'Цена за размещение вакансии: {channel[2]}\n'
                        f'Цена за размещение рекламы: {channel[3]}')
            else:
                return f'{channels.index(channel) + 1}.\n{channel[0]} - {channel[1]}'

        await callback.message.edit_text("\n\n".join(channels_list_text(channel) for channel in channels[0:10]))
        await callback.message.edit_reply_markup(reply_markup=channels_management_kb())
    else:
        await callback.message.delete_reply_markup()
        await callback.message.edit_text("Вы пока что не добавили ни одного канала")


@router.callback_query(F.data == 'update_ch_names')
async def update_channels_names(callback: CallbackQuery):
    ch_names = await ChannelsQs.get_channels_names()

    for ch in ch_names:
        channel = await bot.get_chat(ch[0])
        channel_name = channel.title
        if channel_name != ch[1]:
            await ChannelsQs.update_ch_name(ch[0], channel_name)

    await callback.message.delete_reply_markup()
    await callback.message.edit_text('Названия каналов успешно обновлены!')

# Delete channel


@router.callback_query(F.data == 'del_channel')
async def del_channel(callback: CallbackQuery, state: FSMContext):
    await state.set_state(DelChannel.state)

    message = await callback.message.answer("Напишите название канала, который вы хотели бы удалить")

    await DelMsgsQs.add_msg_id(callback.from_user.id, callback.message.message_id)
    await DelMsgsQs.add_msg_id(callback.from_user.id, message.message_id)
    await callback.answer()


@router.message(DelChannel.state)
async def del_channel_state(msg: Message, state: FSMContext):
    await DelMsgsQs.add_msg_id(msg.from_user.id, msg.message_id)

    channel_name = await ChannelsQs.channel_name_exist(msg.text)

    if channel_name:
        message = await msg.answer(f"Канал {channel_name} успешно удален", reply_markup=add_channel_kb())
        await ChannelsQs.del_channel_by_name(msg.text)
        await del_messages_lo(msg.from_user.id)
    else:
        await state.set_state(DelChannel.state)
        message = await msg.answer("Вы ввели неправильное название канала, попробуйте еще раз")

    await DelMsgsQs.add_msg_id(msg.from_user.id, message.message_id)

# Bot management


@router.callback_query(F.data == 'bot_management')
async def bot_management_start(callback: CallbackQuery, state: FSMContext):
    await state.update_data(role='admin')
    await callback.message.edit_text("Выберите раздел")
    await callback.message.edit_reply_markup(reply_markup=bot_management_kb())


@router.callback_query(F.data == 'msg_all_channels')
async def send_message_to_all_channels(callback: CallbackQuery):
    countries = await ChannelsQs.get_countries()

    def country_all_msg_kb() -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        if countries:
            for country in countries:
                kb.button(
                    text=f"{country}", callback_data=MsgAllChannelsCF(country=f'{country}', all_countries=False)
                )
            kb.button(
                text=f"Во все страны", callback_data=MsgAllChannelsCF(country='', all_countries=True)
            )
        kb.adjust(1)
        return kb.as_markup()

    await callback.message.edit_text("Выберите страну каналов, в которые вы хотели бы отправить сообщение")
    await callback.message.edit_reply_markup(reply_markup=country_all_msg_kb())


@router.callback_query(MsgAllChannelsCF.filter(F.all_countries == False))
async def add_country_admin(callback: CallbackQuery, callback_data: MsgAllChannelsCF, state: FSMContext):
    await callback.answer()

    await state.clear()
    await state.update_data(country=callback_data.country)
    await state.set_state(AdminCities.city)

    await choice_admin_city(callback, 0, state, callback_data.country)

    await DelMsgsQs.add_msg_id(callback.from_user.id, callback.message.message_id)


@router.callback_query(MsgAllChannelsCF.filter(F.all_countries))
async def all_countries_admin(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    cities = await ChannelsQs.get_all_cities_admin()
    cities_all = ','.join(city for city in cities)

    await state.update_data(cities=cities_all)

    await state.update_data(all_cities='Во всех городах сети WorkMarket')

    def pin_kb() -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.button(
            text="Закрепить посуточно", callback_data=PinCF(pin=True,
                                                            format='day')
        )
        kb.button(
            text="Закрепить понедельно", callback_data=PinCF(pin=True,
                                                             format='week')
        )
        kb.button(
            text="Закрепить помесячно", callback_data=PinCF(pin=True,
                                                            format='month')
        )
        kb.button(
            text="Не закреплять", callback_data=PinCF(pin=False,
                                                      format='')
        )
        kb.adjust(1)
        return kb.as_markup()

    await callback.message.edit_text(f"Хотели бы вы закрепить ваше объявление в канале?")
    await callback.message.edit_reply_markup(reply_markup=pin_kb())

    await DelMsgsQs.add_msg_id(callback.from_user.id, callback.message.message_id)


@router.message(AdminCities.city)
async def admin_city_add(msg: Message, state: FSMContext):
    await DelMsgsQs.add_msg_id(msg.from_user.id, msg.message_id)

    data_check = await state.get_data()

    if 'cities' in data_check:
        cities_all = await ChannelsQs.get_all_country_cities_admin(data_check['country'])
        user_cities = data_check['cities'].split(',')
        cities_list = [city for city in cities_all if city not in user_cities]
    else:
        cities = await ChannelsQs.get_all_country_cities_admin(data_check['country'])
        cities_list = [city for city in cities]

    admin_msg_list = msg.text.split(', ')

    if any(city in admin_msg_list for city in cities_list):
        for entered_city in admin_msg_list:
            if entered_city in cities_list:
                data = await state.get_data()
                if 'cities' in data:
                    await state.update_data(cities=f"{data['cities']},{entered_city}")
                else:
                    await state.update_data(cities=f'{entered_city}')
                cities_list.remove(entered_city)

        def city_add_kb() -> InlineKeyboardMarkup:
            kb = InlineKeyboardBuilder()
            kb.button(
                text=f"Продолжить", callback_data=AdminCityStatusCF(
                    add=False,
                    next=True,
                    starting_point=0,
                    back=False
                )
            )
            if len(cities_list) > 0:
                kb.button(
                    text=f"Добавить еще город", callback_data=AdminCityStatusCF(
                        add=True,
                        next=False,
                        starting_point=0,
                        back=False
                    )
                )
            kb.adjust(1)
            return kb.as_markup()

        new_line = '\n'

        data = await state.get_data()

        cities = data['cities'].split(',')

        await msg.answer(f"Вы выбрали следующие города:\n"
                         f"{new_line.join(f'{cities.index(city) + 1}. {city}' for city in cities)}",
                         reply_markup=city_add_kb())
        await del_messages_lo(msg.from_user.id)
    else:
        message = await msg.answer(f"Данного города нет в списке, попробуйте ввести название еще раз!")
        await state.set_state(AdminCities.city)
        await DelMsgsQs.add_msg_id(msg.from_user.id, message.message_id)


@router.callback_query(AdminCityStatusCF.filter(F.add))
async def admin_city_add(callback: CallbackQuery, callback_data: AdminCityStatusCF, state: FSMContext):
    data = await state.get_data()
    await choice_admin_city(callback, callback_data.starting_point, state, data['country'])
    if (callback_data.starting_point == 0) and not callback_data.back:
        await del_messages_lo(callback.from_user.id)
    await DelMsgsQs.add_msg_id(callback.from_user.id, callback.message.message_id)


@router.callback_query(AdminCityCF.filter(F.all))
async def admin_cities(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    cities = await ChannelsQs.get_all_country_cities_admin(data['country'])
    cities_all = ','.join(city for city in cities)

    await state.update_data(cities=cities_all)

    if data['country'] == 'Россия':
        await state.update_data(all_cities='Во всех российских городах сети WorkMarket')

    await DelMsgsQs.add_msg_id(callback.from_user.id, callback.message.message_id)

    def city_all_kb() -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.button(
            text=f"Продолжить", callback_data=AdminCityStatusCF(
                add=False,
                next=True,
                back=False
            )
        )
        kb.adjust(1)
        return kb.as_markup()

    data = await state.get_data()

    new_line = '\n'

    await callback.message.edit_text(f"Вы выбрали следующие города:\n"
                                     f"{data['all_cities'] if 'all_cities' in data else new_line.join(f'{cities.index(city) + 1}. {city}' for city in cities)}")
    await callback.message.edit_reply_markup(reply_markup=city_all_kb())


@router.callback_query(AdminCityStatusCF.filter(F.next))
async def admin_city_next(callback: CallbackQuery):
    def pin_kb() -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.button(
            text="Закрепить посуточно", callback_data=PinCF(pin=True,
                                                            format='day')
        )
        kb.button(
            text="Закрепить понедельно", callback_data=PinCF(pin=True,
                                                             format='week')
        )
        kb.button(
            text="Закрепить помесячно", callback_data=PinCF(pin=True,
                                                            format='month')
        )
        kb.button(
            text="Не закреплять", callback_data=PinCF(pin=False,
                                                      format='')
        )
        kb.adjust(1)
        return kb.as_markup()

    await callback.message.edit_text(f"Хотели бы вы закрепить ваше объявление в канале?")
    await callback.message.edit_reply_markup(reply_markup=pin_kb())

    await DelMsgsQs.add_msg_id(callback.from_user.id, callback.message.message_id)


@router.message(MsgAllChannels.text)
async def msg_all_channels_text(msg: Message, state: FSMContext):
    await DelMsgsQs.add_msg_id(msg.from_user.id, msg.message_id)

    await state.update_data(text=msg.text)
    data = await state.get_data()

    if 'edit' in data:
        message = await msg.answer("Текст сообщения успешно изменен!", reply_markup=edit_final_kb())
    else:
        await state.set_state(MsgAllChannels.photo)

        message = await msg.answer("Отправьте фото к посту", reply_markup=photo_adm_kb())

    await DelMsgsQs.add_msg_id(msg.from_user.id, message.message_id)


@router.callback_query(F.data == 'without_photo_adm')
async def without_photo(callback: CallbackQuery):
    await callback.message.edit_text("Выберите дату публикации")
    await callback.message.edit_reply_markup(reply_markup=await SimpleCalendar().start_calendar())


@router.callback_query(SimpleCalendarCallback.filter())
async def simple_calendar(callback: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    calendar = SimpleCalendar()

    selected, date_cal = await calendar.process_selection(callback, callback_data)
    if selected and (date_cal.date() >= date.today()):
        await state.update_data(date_cal=date_cal.strftime("%d.%m.%Y"))
        await callback.message.edit_text(f'Вы выбрали {date_cal.strftime("%d.%m.%Y")}\n\n'
                                         f'Выберите время публикации (MSK)')
        await callback.message.edit_reply_markup(reply_markup=time_picker_kb(12, 0))
    elif selected and (date_cal.date() < date.today()):
        await callback.message.edit_text(f"<b>Вы выбрали прошедшую дату! ({date_cal.strftime('%d.%m.%Y')})</b>\n"
                                         "Выберите дату публикации еще раз")
        await callback.message.edit_reply_markup(reply_markup=await SimpleCalendar().start_calendar())


@router.callback_query(TimePickerCF.filter(F.up_hour == True))
async def up_hour(callback: CallbackQuery, callback_data: TimePickerCF):
    if callback_data.hour_cur == 23:
        hour = 0
    else:
        hour = callback_data.hour_cur + callback_data.value

    await callback.message.edit_reply_markup(
        reply_markup=time_picker_kb(hour, callback_data.minute_cur)
    )


@router.callback_query(TimePickerCF.filter(F.down_hour == True))
async def down_hour(callback: CallbackQuery, callback_data: TimePickerCF):
    if callback_data.hour_cur == 0:
        hour = 23
    else:
        hour = callback_data.hour_cur-callback_data.value

    await callback.message.edit_reply_markup(
        reply_markup=time_picker_kb(hour, callback_data.minute_cur)
    )


@router.callback_query(TimePickerCF.filter(F.up_min == True))
async def up_minute(callback: CallbackQuery, callback_data: TimePickerCF):
    if callback_data.minute_cur == 55:
        minute = 0
    else:
        minute = callback_data.minute_cur+callback_data.value

    await callback.message.edit_reply_markup(
        reply_markup=time_picker_kb(callback_data.hour_cur, minute)
    )


@router.callback_query(TimePickerCF.filter(F.down_min == True))
async def down_minute(callback: CallbackQuery, callback_data: TimePickerCF):
    if callback_data.minute_cur == 0:
        minute = 55
    else:
        minute = callback_data.minute_cur-callback_data.value

    await callback.message.edit_reply_markup(
        reply_markup=time_picker_kb(callback_data.hour_cur, minute)
    )


@router.message(MsgAllChannels.photo)
async def msg_all_channels_photo(msg: Message, state: FSMContext):
    await DelMsgsQs.add_msg_id(msg.from_user.id, msg.message_id)

    if msg.photo:
        await state.update_data(photo=msg.photo[-1].file_id)
        data = await state.get_data()

        if 'edit' in data:
            message = await msg.answer("Фото успешно изменено!", reply_markup=edit_final_kb())
        else:
            message = await msg.answer("Выберите дату публикации", reply_markup=await SimpleCalendar().start_calendar())
    else:
        await state.set_state(MsgAllChannels.photo)
        message = await msg.answer("Отправьте фото к посту", reply_markup=photo_adm_kb())

    await DelMsgsQs.add_msg_id(msg.from_user.id, message.message_id)


@router.callback_query(TimePickerCF.filter(F.confirm == True))
async def time_confirm(callback: CallbackQuery, callback_data: TimePickerCF, state: FSMContext):
    await callback.answer()

    await DelMsgsQs.add_msg_id(callback.from_user.id, callback.message.message_id)

    data = await state.get_data()

    if 'time_manually' in data:
        if data['time_manually']:
            await order_message_lo(callback, state, data)
        else:
            await time_picker_lo(callback, callback_data, state)
    else:
        await time_picker_lo(callback, callback_data, state)


@router.callback_query(F.data == 'sch_confirm_all_msgs')
async def get_scheduled_info(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    date_time = f"{data['date_cal']} {data['time']}"

    d = {
        'user_id': callback.from_user.id,
        'date_time': datetime.strptime(date_time, "%d.%m.%Y %H:%M"),
        'text': data['text'],
        'cities': data['cities']
    }

    if 'photo' in data:
        d['photo'] = data['photo']

    if data['pin']:
        d['pin'] = datetime.strptime(data['pin'], '%H:%M %Y-%m-%d')

    message = await callback.message.answer("Сообщение успешно запланировано!")
    await DelMsgsQs.add_msg_id(callback.from_user.id, callback.message.message_id)
    await del_messages_lo(callback.from_user.id)

    await DelMsgsQs.add_msg_id(callback.from_user.id, message.message_id)
    await SchMsgsQs.add_sch_msg_user(**d)

