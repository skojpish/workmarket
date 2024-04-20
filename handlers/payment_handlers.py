import hashlib
from datetime import datetime

import aiohttp
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from yoomoney import Client, Quickpay

from config import youmoney_token, payok_shop_id, payok_sk, payok_api_id, payok_token
from database.channels import ChannelsQs
from database.delete_msgs import DelMsgsQs
from database.package_posts import PackagePostsQs
from database.scheduled_msgs import SchMsgsQs
from layouts.handlers_layouts import del_messages_lo, confirm_payment_lo

router = Router()
client = Client(youmoney_token)


@router.callback_query(F.data == 'payment_methods')
async def payment_methods(callback: CallbackQuery, state: FSMContext):
    await DelMsgsQs.add_msg_id(callback.from_user.id, callback.message.message_id)

    data = await state.get_data()

    if 'package_posts' in data:
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

        await PackagePostsQs.subtract_one_publ(callback.from_user.id)
        await PackagePostsQs.delete_package()

        await SchMsgsQs.add_sch_msg_user(**d)
        message = await callback.message.answer(f"Пакетное размещение успешно использовано!\n"
                                                "Посмотреть свои запланированные посты можно с помощью команды /posts")
    else:
        def payment_methods_kb() -> InlineKeyboardMarkup:
            kb = InlineKeyboardBuilder()
            kb.add(InlineKeyboardButton(
                text="Юmoney", callback_data='youmoney'
            ))
            kb.add(InlineKeyboardButton(
                text="Payok", callback_data='payok'
            ))
            kb.adjust(1)
            return kb.as_markup()

        if 'package_sum' in data:
            full_sum = data['package_sum']
        elif 'pin_package_sum' in data:
            full_sum = data['pin_package_sum']
        elif 'all_cities' in data:
            full_sum = int('{:g}'.format(data['all_cities_sum']*0.7))
        else:
            channels = await ChannelsQs.get_user_cities(data['cities'].split(','), data['cat'])
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
async def payment_youmoney(callback: CallbackQuery, state: FSMContext):
    user = client.account_info()

    data = await state.get_data()

    pay_url = Quickpay(receiver=f'{user.account}',
                       quickpay_form="shop",
                       targets="WorkMarketBot",
                       paymentType="SB",
                       sum=data['full_sum'],
                       label=f'{callback.from_user.id}{callback.message.message_id}')

    def youmoney_kb() -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.add(InlineKeyboardButton(
            text="Ссылка на оплату", url=f'{pay_url.redirected_url}'
        ))
        kb.button(
            text="Проверить оплату", callback_data='youmoney_check'
        )
        kb.add(InlineKeyboardButton(
            text="Назад", callback_data='payment_methods'
        ))
        kb.add(InlineKeyboardButton(
            text="Связаться с менеджером", callback_data='help'
        ))
        kb.adjust(1)
        return kb.as_markup()

    await callback.message.edit_text(f"Сумма на оплату: {data['full_sum']} руб.\n\n"
                                     f"<b>Как произведете оплату, ОБЯЗАТЕЛЬНО нажмите на кнопку 'Проверить оплату'!</b>\n\n"
                                     f"Если возникнет проблема при оплате, свяжитесь с нашим менеджером")
    await callback.message.edit_reply_markup(reply_markup=youmoney_kb())


@router.callback_query(F.data == 'youmoney_check')
async def check_youmoney(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    history = client.operation_history(label=f"{callback.from_user.id}{callback.message.message_id}")
    operations = history.operations
    try:
        if operations[0].status == 'success':
            await confirm_payment_lo(callback, state)
    except IndexError:
        pass


@router.callback_query(F.data == 'help')
async def help_bot(callback: CallbackQuery):
    await callback.answer()
    message = await callback.message.answer(f"Аккаунт менеджера: @workmarket_manager")

    await DelMsgsQs.add_msg_id(callback.from_user.id, message.message_id)


@router.callback_query(F.data == 'payok')
async def payment_payok(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    amount = data['full_sum']
    label = f'{callback.from_user.id}{callback.message.message_id}'
    shop_id = payok_shop_id
    currency = 'RUB'
    desc = 'WorkMarketBot'
    secret = payok_sk

    sign = hashlib.md5(f"{amount}|{label}|{shop_id}|{currency}|{desc}|{secret}".encode(
        'utf-8')).hexdigest()
    pay_url = f"https://payok.io/pay?amount={amount}&currency={currency}&payment={label}&desc={desc}&shop={shop_id}&method=cd&sign={sign}"

    def payok_kb() -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.add(InlineKeyboardButton(
            text="Ссылка на оплату", url=pay_url
        ))
        kb.button(
            text="Проверить оплату", callback_data='payok_check'
        )
        kb.add(InlineKeyboardButton(
            text="Назад", callback_data='payment_methods'
        ))
        kb.add(InlineKeyboardButton(
            text="Связаться с менеджером", callback_data='help'
        ))
        kb.adjust(1)
        return kb.as_markup()

    await callback.message.edit_text(f"Сумма на оплату: {data['full_sum']} руб.\n\n"
                                     f"<b>Как произведете оплату, ОБЯЗАТЕЛЬНО нажмите на кнопку 'Проверить оплату'!</b>\n\n"
                                     f"Если возникнет проблема при оплате, свяжитесь с нашим менеджером")
    await callback.message.edit_reply_markup(reply_markup=payok_kb())


@router.callback_query(F.data == 'payok_check')
async def check_payok(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    async with aiohttp.ClientSession() as session:
        request_params = {'API_ID': payok_api_id, 'API_KEY': payok_token, 'shop': payok_shop_id,
                          'payment': int(f'{callback.from_user.id}{callback.message.message_id}')}
        async with session.post('https://payok.io/api/transaction', data=request_params) as response:
            operation = await response.json(content_type=None)
            operation_keys = list(operation.keys())

    try:
        if operation[f'{operation_keys[1]}']['transaction_status']:
            await confirm_payment_lo(callback, state)
    except (IndexError, TypeError):
        pass
