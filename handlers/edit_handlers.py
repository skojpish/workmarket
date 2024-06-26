from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram3_calendar import SimpleCalendar

from database.FSM import EditChannel, MsgAllChannels, UserText, EditPost
from database.channels import ChannelsQs
from database.channelsandmsgs import ChannelsAndMsgsQs
from database.delete_msgs import DelMsgsQs
from database.scheduled_msgs import SchMsgsQs
from handlers.callback_factories import EditPriceCF, EditPostCF
from keyboards.admin_kbs import add_channel_kb
from keyboards.user_kbs import example_kb
from layouts.handlers_layouts import del_messages_lo, order_message_lo

router = Router()


@router.callback_query(F.data == 'edit_channel_info')
async def edit_channel_info(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await DelMsgsQs.add_msg_id(callback.from_user.id, callback.message.message_id)

    await state.set_state(EditChannel.name)
    message = await callback.message.answer('Напишите название канала, где вы хотели бы изменить цену')
    await DelMsgsQs.add_msg_id(callback.from_user.id, message.message_id)


@router.message(EditChannel.name)
async def channel_name_find(msg: Message, state: FSMContext):
    await DelMsgsQs.add_msg_id(msg.from_user.id, msg.message_id)

    channel_name = await ChannelsQs.channel_name_exist(msg.text)

    if channel_name:
        def edit_price_kb() -> InlineKeyboardMarkup:
            kb = InlineKeyboardBuilder()
            kb.button(
                text=f"Цена вакансии", callback_data=EditPriceCF(cat='vac', channel_name=channel_name)
            )
            kb.button(
                text=f"Цена рекламы", callback_data=EditPriceCF(cat='ad', channel_name=channel_name)
            )
            kb.adjust(1)
            return kb.as_markup()

        message = await msg.answer(f"Выбран канал {channel_name}\n\n"
                                   f"Выберите цену чего вы хотели бы изменить", reply_markup=edit_price_kb())
    else:
        await state.set_state(EditChannel.name)
        message = await msg.answer("Вы ввели неправильное название канала, попробуйте еще раз")

    await DelMsgsQs.add_msg_id(msg.from_user.id, message.message_id)


@router.callback_query(EditPriceCF.filter())
async def edit_price(callback: CallbackQuery, callback_data: EditPriceCF, state: FSMContext):
    await state.update_data(channel_name=callback_data.channel_name, cat=callback_data.cat)

    if callback_data.cat == 'vac':
        await state.set_state(EditChannel.price_vac)
    else:
        await state.set_state(EditChannel.price_ad)

    await callback.message.delete_reply_markup()
    await callback.message.edit_text('Введите новую цену')


@router.message(EditChannel.price_vac)
async def edit_vac_price(msg: Message, state: FSMContext):
    await DelMsgsQs.add_msg_id(msg.from_user.id, msg.message_id)

    try:
        await state.update_data(new_price_vac=int(msg.text))
        data = await state.get_data()
        await ChannelsQs.update_price(data['channel_name'], data['new_price_vac'], data['cat'])
        message = await msg.answer(f"Цена вакансии для канала {data['channel_name']} успешно изменена!",
                                   reply_markup=add_channel_kb())
        await del_messages_lo(msg.from_user.id)
    except ValueError:
        await state.set_state(EditChannel.price_vac)
        message = await msg.answer(f"Введите цену одним числом!")

    await DelMsgsQs.add_msg_id(msg.from_user.id, message.message_id)


@router.message(EditChannel.price_ad)
async def edit_vac_price(msg: Message, state: FSMContext):
    await DelMsgsQs.add_msg_id(msg.from_user.id, msg.message_id)

    try:
        await state.update_data(new_price_ad=int(msg.text))
        data = await state.get_data()
        await ChannelsQs.update_price(data['channel_name'], data['new_price_ad'], data['cat'])
        if data['cat'] == 'vac':
            message = await msg.answer(f"Цена вакансии для канала {data['channel_name']} успешно изменена!",
                                       reply_markup=add_channel_kb())
        else:
            message = await msg.answer(f"Цена рекламы для канала {data['channel_name']} успешно изменена!",
                                       reply_markup=add_channel_kb())
        await del_messages_lo(msg.from_user.id)
    except ValueError:
        await state.set_state(EditChannel.price_ad)
        message = await msg.answer(f"Введите цену одним числом!")

    await DelMsgsQs.add_msg_id(msg.from_user.id, message.message_id)


# Edit scheduled msg

@router.callback_query(F.data == 'edit_sch_text_adm')
async def edit_sch_text_adm(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    await state.update_data(edit=True)
    await state.set_state(MsgAllChannels.text)

    message = await callback.message.answer("Напишите новое сообщение")
    await DelMsgsQs.add_msg_id(callback.from_user.id, callback.message.message_id)

    await DelMsgsQs.add_msg_id(callback.from_user.id, message.message_id)


@router.callback_query(F.data == 'edit_sch_text_user')
async def edit_sch_text_user(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    await state.update_data(edit=True)
    await state.set_state(UserText.text)

    data = await state.get_data()

    if data['cat'] == 'vac':
        message = await callback.message.answer("Пожалуйста, отправьте боту готовый текст по следующему образцу:\n"
                                   "1. Название должности, заработная плата, адрес:\n"
                                   "2. Обязанности:\n"
                                   "3. Требования:\n"
                                   "4. Мы предлагаем:\n"
                                   "5. Контакты:\n", reply_markup=example_kb())
    else:
        message = await callback.message.answer("Отправьте боту новый текст рекламного поста")
    await DelMsgsQs.add_msg_id(callback.from_user.id, callback.message.message_id)
    await DelMsgsQs.add_msg_id(callback.from_user.id, message.message_id)


@router.callback_query(F.data == 'edit_sch_photo_adm')
async def edit_sch_photo_adm(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    await state.update_data(edit=True)
    await state.set_state(MsgAllChannels.photo)

    message = await callback.message.answer("Отправьте новое фото")

    await DelMsgsQs.add_msg_id(callback.from_user.id, callback.message.message_id)
    await DelMsgsQs.add_msg_id(callback.from_user.id, message.message_id)


@router.callback_query(F.data == 'edit_sch_photo_user')
async def edit_sch_photo_user(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    await state.update_data(edit=True)
    await state.set_state(UserText.photo)

    message = await callback.message.answer("Отправьте новое фото")
    await DelMsgsQs.add_msg_id(callback.from_user.id, callback.message.message_id)
    await DelMsgsQs.add_msg_id(callback.from_user.id, message.message_id)


@router.callback_query(F.data == 'edit_sch_datetime')
async def edit_sch_datetime(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = await state.get_data()
    if 'time_manually' in data:
        await state.update_data(time_manually=False)

    message = await callback.message.answer("Выберите новую дату публикации",
                                  reply_markup=await SimpleCalendar().start_calendar())
    await DelMsgsQs.add_msg_id(callback.from_user.id, callback.message.message_id)
    await DelMsgsQs.add_msg_id(callback.from_user.id, message.message_id)


@router.callback_query(F.data == 'back_to_order')
async def back_to_order(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = await state.get_data()

    await order_message_lo(callback, state, data)


@router.callback_query(F.data == 'edit_post')
async def edit_post(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    await state.set_state(EditPost.number)
    message = await callback.message.answer("Напишите номер поста, данные в котором вы хотите изменить")
    await DelMsgsQs.add_msg_id(callback.from_user.id, message.message_id)


@router.message(EditPost.number)
async def choose_post(msg: Message, state: FSMContext):
    await DelMsgsQs.add_msg_id(msg.from_user.id, msg.message_id)

    try:
        data = await state.get_data()

        msg_id = data['msg_ids'][f'{int(msg.text)}']

        sch_msg = await SchMsgsQs.get_sch_msg(msg_id)

        channels = await ChannelsAndMsgsQs.get_msg_channels(msg_id)

        data = {
            'photo': sch_msg[0],
            'text': sch_msg[1],
            'date': sch_msg[2].strftime('%d.%m.%Y'),
            'time': sch_msg[2].strftime('%H:%M'),
            'cities': ' '.join(channels),
        }

        def choose_post_info_kb() -> InlineKeyboardMarkup:
            kb = InlineKeyboardBuilder()
            kb.button(
                text=f"Изменить текст", callback_data=EditPostCF(
                    msg_id=msg_id,
                    text=True,
                    photo=False
                )
            )
            if data['photo'] is not None:
                kb.button(
                    text=f"Изменить фото", callback_data=EditPostCF(
                        msg_id=msg_id,
                        text=False,
                        photo=True
                    )
                )
            kb.adjust(1)
            return kb.as_markup()

        if data['photo'] is not None:
            message = await msg.answer_photo(data['photo'], f"{data['text']}\n\n"
                                                               f"Дата: {data['date']}\n"
                                                               f"Время: {data['time']}\n"
                                                               f"Города: {data['cities']}",
                                                reply_markup=choose_post_info_kb())
        else:
            message = await msg.answer(f"{data['text']}\n\n"
                                                    f"Дата: {data['date']}\n"
                                                    f"Время: {data['time']}\n"
                                                    f"Города: {data['cities']}",
                                          reply_markup=choose_post_info_kb())
    except ValueError:
        await state.set_state(EditPost.number)
        message = await msg.answer(f"Введите номер поста")
    except TelegramBadRequest:
        data = await state.get_data()

        msg_id = data['msg_ids'][f'{int(msg.text)}']

        sch_msg = await SchMsgsQs.get_sch_msg(msg_id)

        channels = await ChannelsAndMsgsQs.get_msg_channels(msg_id)

        data = {
            'photo': sch_msg[0],
            'text': sch_msg[1],
            'date': sch_msg[2].strftime('%d.%m.%Y'),
            'time': sch_msg[2].strftime('%H:%M'),
            'cities': ' '.join(channels),
        }

        def choose_post_info_kb() -> InlineKeyboardMarkup:
            kb = InlineKeyboardBuilder()
            kb.button(
                text=f"Изменить текст", callback_data=EditPostCF(
                    msg_id=msg_id,
                    text=True,
                    photo=False
                )
            )
            if data['photo'] is not None:
                kb.button(
                    text=f"Изменить фото", callback_data=EditPostCF(
                        msg_id=msg_id,
                        text=False,
                        photo=True
                    )
                )
            kb.adjust(1)
            return kb.as_markup()

        message_photo = await msg.answer_photo(data['photo'])
        message = await msg.answer(f"{data['text']}\n\n"
                                   f"Дата: {data['date']}\n"
                                   f"Время: {data['time']}\n"
                                   f"Города: {data['cities']}",
                                   reply_markup=choose_post_info_kb())

        if message_photo is not None:
            await DelMsgsQs.add_msg_id(msg.from_user.id, message_photo.message_id)

    await DelMsgsQs.add_msg_id(msg.from_user.id, message.message_id)


@router.callback_query(EditPostCF.filter())
async def edit_post(callback: CallbackQuery, callback_data: EditPostCF, state: FSMContext):
    await callback.answer()

    await state.update_data(msg_id=callback_data.msg_id)

    if callback_data.text:
        await state.set_state(EditPost.text)
        message = await callback.message.answer(f"Введите новый текст")
    else:
        await state.set_state(EditPost.photo)
        message = await callback.message.answer(f"Отправьте новое фото")

    await DelMsgsQs.add_msg_id(callback.from_user.id, message.message_id)


@router.message(EditPost.text)
async def edit_post_text(msg: Message, state: FSMContext):
    await DelMsgsQs.add_msg_id(msg.from_user.id, msg.message_id)

    data = await state.get_data()
    await SchMsgsQs.update_text(data['msg_id'], msg.text)

    message = await msg.answer("Текст публикации успешно изменен!")

    await del_messages_lo(msg.from_user.id)
    await DelMsgsQs.add_msg_id(msg.from_user.id, message.message_id)


@router.message(EditPost.photo)
async def edit_post_photo(msg: Message, state: FSMContext):
    await DelMsgsQs.add_msg_id(msg.from_user.id, msg.message_id)

    if msg.photo:
        data = await state.get_data()
        await SchMsgsQs.update_photo(data['msg_id'], msg.photo[-1].file_id)

        message = await msg.answer("Фото публикации успешно изменено!")

        await del_messages_lo(msg.from_user.id)
    else:
        await state.set_state(EditPost.photo)
        message = await msg.answer("Отправьте новое фото")

    await DelMsgsQs.add_msg_id(msg.from_user.id, message.message_id)
