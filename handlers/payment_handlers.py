from datetime import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from yoomoney import Client, Quickpay

from config import pay_token
from database.delete_msgs import DelMsgsQs
from database.scheduled_msgs import SchMsgsQs
from handlers.callback_factories import YouMoneyCheckCF
from keyboards.menu_kbs import back_to_menu_kb
from layouts.handlers_layouts import del_messages_lo

router = Router()
client = Client(pay_token)

@router.callback_query(F.data == 'payment_methods')
async def payment_methods(callback: CallbackQuery):
    await DelMsgsQs.add_msg_id(callback.from_user.id, callback.message.message_id)
    await del_messages_lo()

    def payment_methods_kb()-> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.add(InlineKeyboardButton(
            text="Юmoney", callback_data='youmoney_pay_check'
        ))
        kb.adjust(1)
        return kb.as_markup()

    await callback.message.answer("Сумма на оплату: xxx руб.\n\n"
                                  "Выберите способ оплаты", reply_markup=payment_methods_kb())


@router.callback_query(F.data == 'youmoney_pay_check')
async def payment_youmoney_check(callback: CallbackQuery):
    user = client.account_info()
    pay_url = Quickpay(receiver=f'{user.account}',
                       quickpay_form="shop",
                       targets="WorkMarketBot",
                       paymentType="SB",
                       sum=2,
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
            text="Связаться с менеджером", callback_data='dddd'
        ))
        kb.adjust(1)
        return kb.as_markup()

    await callback.message.edit_text("Как произведете оплату, нажмите на кнопку ниже!\n"
                                     "Если возникнет проблема при оплате, свяжитесь с нашим менеджером")
    await callback.message.edit_reply_markup(reply_markup=youmoney_check_kb())


@router.callback_query(YouMoneyCheckCF.filter())
async def check_youmoney(callback: CallbackQuery, callback_data: YouMoneyCheckCF, state: FSMContext):
    history = client.operation_history(label=f"{callback.from_user.id}{callback_data.msg_id+1}")
    operations = history.operations

    if operations[0].status == 'success':
        data = await state.get_data()
        date_time = f"{data['date']} {data['time']}"
        buffer = await SchMsgsQs.get_buffer_cities(callback.from_user.id)

        if 'photo' in data:
            d = {
                'user_id': callback.from_user.id,
                'date_time': datetime.strptime(date_time, "%d.%m.%Y %H:%M:%S"),
                'text': data['text'],
                'cities': buffer[1],
                'photo': data['photo']
            }
        else:
            d = {
                'user_id': callback.from_user.id,
                'date_time': datetime.strptime(date_time, "%d.%m.%Y %H:%M:%S"),
                'text': data['text'],
                'cities': buffer[1]
            }

        await SchMsgsQs.add_sch_msg_user(**d)
        await callback.message.edit_text("Оплата проведена успешно!")
        await callback.message.edit_reply_markup(reply_markup=back_to_menu_kb())
