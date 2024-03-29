from datetime import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from yoomoney import Client, Quickpay

from config import pay_token
from database.channels import ChannelsQs
from database.delete_msgs import DelMsgsQs
from database.scheduled_msgs import SchMsgsQs
from handlers.callback_factories import YouMoneyCheckCF
from layouts.handlers_layouts import del_messages_lo

router = Router()
client = Client(pay_token)


@router.callback_query(F.data == 'payment_methods')
async def payment_methods(callback: CallbackQuery, state: FSMContext):
    await DelMsgsQs.add_msg_id(callback.from_user.id, callback.message.message_id)

    def payment_methods_kb() -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.add(InlineKeyboardButton(
            text="Юmoney", callback_data='youmoney'
        ))
        kb.adjust(1)
        return kb.as_markup()

    data = await state.get_data()

    channels = await ChannelsQs.get_user_cities(data['cities'].split(), data['cat'])
    price = []

    for channel in channels:
        price.append(channel[1])

    full_sum = sum(price)

    if 'pin_sum' in data:
        full_sum += data['pin_sum']

    await state.update_data(full_sum=full_sum)

    message = await callback.message.answer(f"Сумма на оплату: {full_sum} руб.\n\n"
                                  f"Выберите способ оплаты", reply_markup=payment_methods_kb())

    await del_messages_lo(callback.from_user.id)
    await DelMsgsQs.add_msg_id(callback.from_user.id, message.message_id)


@router.callback_query(F.data == 'youmoney')
async def payment_youmoney_check(callback: CallbackQuery, state: FSMContext):
    user = client.account_info()

    data = await state.get_data()

    pay_url = Quickpay(receiver=f'{user.account}',
                       quickpay_form="shop",
                       targets="WorkMarketBot",
                       paymentType="SB",
                       sum=data['full_sum'],
                       label=f'{callback.from_user.id}{callback.message.message_id + 1}')

    def youmoney_check_kb() -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.add(InlineKeyboardButton(
            text="Ссылка на оплату", url=f'{pay_url.redirected_url}'
        ))
        kb.button(
            text="Проверить оплату", callback_data=YouMoneyCheckCF(msg_id=callback.message.message_id)
        )
        kb.add(InlineKeyboardButton(
            text="Связаться с менеджером", callback_data='help'
        ))
        kb.adjust(1)
        return kb.as_markup()

    await callback.message.edit_text(f"Сумма на оплату: {data['full_sum']} руб.\n\n"
                                     f"<b>Как произведете оплату, ОБЯЗАТЕЛЬНО нажмите на кнопку ниже!</b>\n\n"
                                     f"Если возникнет проблема при оплате, свяжитесь с нашим менеджером")
    await callback.message.edit_reply_markup(reply_markup=youmoney_check_kb())


@router.callback_query(YouMoneyCheckCF.filter())
async def check_youmoney(callback: CallbackQuery, callback_data: YouMoneyCheckCF, state: FSMContext):
    await callback.answer()

    history = client.operation_history(label=f"{callback.from_user.id}{callback_data.msg_id+1}")
    operations = history.operations
    try:
        if operations[0].status == 'success':
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
            elif data['pin']:
                d['pin'] = datetime.strptime(data['pin'], '%H:%M %Y-%m-%d')

            await SchMsgsQs.add_sch_msg_user(**d)

            await state.clear()
            await callback.message.edit_text("Оплата проведена успешно!\n"
                                             "Посмотреть свои запланированные посты можно с помощью команды /posts")
    except IndexError:
        pass


@router.callback_query(F.data == 'help')
async def help_bot(callback: CallbackQuery):
    message = await callback.message.answer(f"Аккаунт менеджера: @alexander_ivanovsky")

    await DelMsgsQs.add_msg_id(callback.from_user.id, message.message_id)
