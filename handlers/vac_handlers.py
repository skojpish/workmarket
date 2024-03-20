from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.FSM import UserText
from database.delete_msgs import DelMsgsQs
from database.scheduled_msgs import SchMsgsQs
from handlers.callback_factories import UserCountryCF, UserCityCF, UserCityStatusCF, PinCF
from keyboards.user_kbs import example_kb, back_user_text_kb, photo_user_kb, end_scheduled_user_kb
from layouts.handlers_layouts import choice_user_country, choice_user_first_city, user_city_add, choice_user_more_city, \
    del_messages_lo

router = Router()


@router.callback_query(F.data == 'vacancy')
async def vacancy_country(callback: CallbackQuery):
    await choice_user_country(callback)


@router.callback_query(UserCountryCF.filter())
async def vacancy_city(callback: CallbackQuery, callback_data: UserCountryCF):
    await choice_user_first_city(callback, callback_data, 'vac')


@router.callback_query(UserCityCF.filter())
async def vacancy_first_city_add(callback: CallbackQuery, callback_data: UserCityCF):
    await user_city_add(callback, callback_data)


@router.callback_query(UserCityStatusCF.filter(F.add))
async def vacancy_city_add(callback: CallbackQuery, callback_data: UserCityCF):
    await choice_user_more_city(callback, callback_data, 'vac')


@router.callback_query(UserCityStatusCF.filter(F.next))
async def vacancy_city_next(callback: CallbackQuery, callback_data: UserCityStatusCF):
    def pin_kb() -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.button(
            text="Закрепить посуточно", callback_data=PinCF(pin=True,
                                                            country=callback_data.country,
                                                            cities=callback_data.cities,
                                                            format='day')
        )
        kb.button(
            text="Закрепить понедельно", callback_data=PinCF(pin=True,
                                                             country=callback_data.country,
                                                             cities=callback_data.cities,
                                                             format='week')
        )
        kb.button(
            text="Не закреплять", callback_data=PinCF(pin=False,
                                                      country=callback_data.country,
                                                      cities=callback_data.cities,
                                                      format='')
        )
        kb.adjust(1)
        return kb.as_markup()

    await callback.message.edit_text(f"Хотели бы вы закрепить ваше объявление в канале?\n\n"
                                     f"Стоимость размещения с закреплением:\n"
                                     f" + 300 руб. / сутки\n"
                                     f" + 1500 руб. / неделя")
    await callback.message.edit_reply_markup(reply_markup=pin_kb())


@router.callback_query(PinCF.filter(F.pin == True))
async def vacancy_city_add(callback: CallbackQuery, state: FSMContext, callback_data: PinCF):
    await SchMsgsQs.add_buffer_cities(callback.from_user.id, callback_data.country, callback_data.cities)

    if callback_data.format == 'day':
        await state.set_state(UserText.pin_day)
        await callback.message.delete_reply_markup()
        await callback.message.edit_text(f"Напишите количество дней")
    elif callback_data.format == 'week':
        await state.set_state(UserText.pin_week)
        await callback.message.delete_reply_markup()
        await callback.message.edit_text(f"Напишите количество недель")

    await DelMsgsQs.add_msg_id(callback.from_user.id, callback.message.message_id)


@router.message(UserText.pin_day)
async def pin_days(msg: Message, state: FSMContext):
    await DelMsgsQs.add_msg_id(msg.from_user.id, msg.message_id)

    await state.update_data(day=msg.text)
    await state.set_state(UserText.text)

    message = await msg.answer("Пожалуйста, отправьте боту готовый текст по следующему образцу:\n"
                               "1. Название должности, заработная плата, адрес:\n"
                               "2. Обязанности:\n"
                               "3. Требования:\n"
                               "4. Мы предлагаем:\n"
                               "5. Контакты:\n", reply_markup=example_kb())

    await DelMsgsQs.add_msg_id(msg.from_user.id, message.message_id)


@router.message(UserText.pin_week)
async def pin_days(msg: Message, state: FSMContext):
    await DelMsgsQs.add_msg_id(msg.from_user.id, msg.message_id)

    await state.update_data(week=msg.text)
    await state.set_state(UserText.text)

    message = await msg.answer("Пожалуйста, отправьте боту готовый текст по следующему образцу:\n"
                               "1. Название должности, заработная плата, адрес:\n"
                               "2. Обязанности:\n"
                               "3. Требования:\n"
                               "4. Мы предлагаем:\n"
                               "5. Контакты:", reply_markup=example_kb())

    await DelMsgsQs.add_msg_id(msg.from_user.id, message.message_id)


@router.callback_query(F.data == 'example')
async def example(callback: CallbackQuery):
    await callback.message.edit_text("Кассир-операционист (метро Пражская)\n"
                                     "От 50 000 ₽ на руки\n\n"
                                     "Обязанности:\n"
                                     "• Кассовое обслуживание физических лиц\n"
                                     "• Валютно-обменные операции\n"
                                     "• Денежные переводы без открытия счета\n"
                                     "• Прием платежей\n"
                                     "• Инкассация\n"
                                     "• Отчетность\n\n"
                                     "Требования:\n"
                                     "• Образование не ниже среднего специального\n"
                                     "• Опыт работы с денежной наличностью в любой сфере\n"
                                     "• Уверенное владение ПК\n"
                                     "• Навыки работы с сетью Интернет\n"
                                     "• Грамотная устная и письменная речь на русском языке\n"
                                     "• Общительность, доброжелательность, готовность к обучению\n\n"
                                     "Мы предлагаем:\n"
                                     "• Оформление в штат в соответствии с ТК РФ\n"
                                     "• Профессиональное обучение\n"
                                     "• График работы 2/2\n"
                                     "• Фитнес и корпоративные скидки\n"
                                     "• Участие в спортивных мероприятиях\n"
                                     "• Поддержку куратора\n"
                                     "• Профессиональный и карьерный рост\n\n"
                                     "Контакты:\n"
                                     "+74952270179\n"
                                     "e.zaharova@unistream.com\n")
    await callback.message.edit_reply_markup(reply_markup=back_user_text_kb())


@router.callback_query(F.data == 'user_text_back')
async def user_text_back(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserText.text)

    await callback.message.edit_text("Пожалуйста, отправьте боту готовый текст по следующему образцу:\n"
                                     "1. Название должности, заработная плата, адрес:\n"
                                     "2. Обязанности:\n"
                                     "3. Требования:\n"
                                     "4. Мы предлагаем:\n"
                                     "5. Контакты:")
    await callback.message.edit_reply_markup(reply_markup=example_kb())


@router.message(UserText.text)
async def user_text(msg: Message, state: FSMContext):
    await DelMsgsQs.add_msg_id(msg.from_user.id, msg.message_id)

    await state.update_data(text=msg.text)
    await state.set_state(UserText.photo)

    message = await msg.answer("Отправьте фото к посту", reply_markup=photo_user_kb())

    await DelMsgsQs.add_msg_id(msg.from_user.id, message.message_id)


@router.message(UserText.photo)
async def user_photo(msg: Message, state: FSMContext):
    await DelMsgsQs.add_msg_id(msg.from_user.id, msg.message_id)

    if msg.photo:
        await state.update_data(photo=msg.photo[-1].file_id)
        await state.set_state(UserText.date)
        message = await msg.answer("Введите дату публикации в следующем формате: ДД.ММ.ГГГГ")
    else:
        await state.set_state(UserText.photo)
        message = await msg.answer("Отправьте фото к посту", reply_markup=photo_user_kb())

    await DelMsgsQs.add_msg_id(msg.from_user.id, message.message_id)


@router.callback_query(F.data == 'without_photo_user')
async def without_photo(callback: CallbackQuery, state: FSMContext):
    await DelMsgsQs.del_msg_id(callback.from_user.id, callback.message.message_id)

    await state.set_state(UserText.date)

    await callback.message.delete_reply_markup()
    message = await callback.message.edit_text("Введите дату публикации в следующем формате: ДД.ММ.ГГГГ")

    await DelMsgsQs.add_msg_id(callback.from_user.id, message.message_id)


@router.message(UserText.date)
async def msg_user_date(msg: Message, state: FSMContext):
    await DelMsgsQs.add_msg_id(msg.from_user.id, msg.message_id)

    await state.update_data(date=msg.text)
    await state.set_state(UserText.time)

    message = await msg.answer("Введите время публикации в следующем формате: ЧЧ:ММ:СС")

    await DelMsgsQs.add_msg_id(msg.from_user.id, message.message_id)


@router.message(UserText.time)
async def user_time(msg: Message, state: FSMContext):
    await DelMsgsQs.add_msg_id(msg.from_user.id, msg.message_id)
    await del_messages_lo()

    await state.update_data(time=msg.text)
    data = await state.get_data()

    buffer = await SchMsgsQs.get_buffer_cities(msg.from_user.id)

    country = buffer[0]
    cities = buffer[1].replace(' ', ', ')

    if 'photo' in data:
        await msg.answer_photo(data['photo'], f"Вы ввели следующие данные:\n\n"
                                              f"{data['text']}\n\n"
                                              f"Дата: {data['date']}\n"
                                              f"Время: {data['time']}\n\n"
                                              f"Страна: {country}\n"
                                              f"Города: \n{cities}",
                                              reply_markup=end_scheduled_user_kb(data))
    else:
        await msg.answer(f"Вы ввели следующие данные:\n\n"
                              f"{data['text']}\n\n"
                              f"Дата: {data['date']}\n"
                              f"Время: {data['time']}\n\n"
                              f"Страна: {country}\n"
                              f"Города: \n{cities}",
                              reply_markup=end_scheduled_user_kb(data))


