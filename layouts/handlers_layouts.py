from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import bot, master_id
from database.channels import ChannelsQs
from database.delete_msgs import DelMsgsQs
from handlers.callback_factories import UserCountryCF, UserCityCF, UserCityStatusCF


async def start_message_lo(msg, kb):
    await msg.answer(f"Здравствуйте, {msg.from_user.full_name}!\n\n"
                     f"Этот бот поможет Вам разместить вакансию или рекламу в сети телеграм каналов Workmarket.",
                     reply_markup=kb())
    await bot.delete_message(msg.from_user.id, msg.message_id)


async def del_messages_lo():
    messages = await DelMsgsQs.get_msgs(master_id)
    for message in messages:
        try:
            await bot.delete_message(master_id, message)
        except Exception:
            pass

    await DelMsgsQs.del_msgs_id(master_id)


async def choice_user_country(callback):
    countries = await ChannelsQs.get_countries()

    def country_kb() -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        if countries:
            for country in countries:
                kb.button(
                    text=f"{country}", callback_data=UserCountryCF(country=f'{country}')
                )
        kb.add(InlineKeyboardButton(
            text="Отмена", callback_data="cancel"
        ))
        kb.adjust(1)
        return kb.as_markup()

    await callback.message.edit_text("Выберите страну")
    await callback.message.edit_reply_markup(reply_markup=country_kb())


async def choice_user_first_city(callback, callback_data, cat):
    cities = await ChannelsQs.get_cities(callback_data.country, cat)

    prices = []

    for price in cities:
        prices.append(price[1])

    def city_kb() -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        if cities:
            for city in cities:
                kb.button(
                    text=f"{city[0]} ({city[1]} руб.)", callback_data=UserCityCF(country=f'{callback_data.country}',
                                                                                 cities=f'{city[0]} ')
                )
            kb.button(
                text=f"Во всех городах ({sum(prices)} руб.)", callback_data=UserCityCF(
                                                                            country=f'{callback_data.country}',
                                                                            cities=' '.join(city[0] for city in cities))
            )
        kb.add(InlineKeyboardButton(
            text="Отмена", callback_data="cancel"
        ))
        kb.adjust(1)
        return kb.as_markup()

    await callback.message.edit_text("Выберите город")
    await callback.message.edit_reply_markup(reply_markup=city_kb())


async def choice_user_more_city(callback, callback_data, cat):
    cities = await ChannelsQs.get_cities(callback_data.country, cat)

    prices = []

    for price in cities:
        prices.append(price[1])

    def city_kb() -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        if cities:
            for city in cities:
                kb.button(
                    text=f"{city[0]} ({city[1]} руб.)", callback_data=UserCityCF(country=f'{callback_data.country}',
                                                                                 cities=callback_data.cities+f'{city[0]} ')
                )
            kb.button(
                text=f"Во всех городах ({sum(prices)} руб.)", callback_data=UserCityCF(
                                                                            country=f'{callback_data.country}',
                                                                            cities=' '.join(city[0] for city in cities))
            )
        kb.add(InlineKeyboardButton(
            text="Отмена", callback_data="cancel"
        ))
        kb.adjust(1)
        return kb.as_markup()

    await callback.message.edit_text("Выберите город")
    await callback.message.edit_reply_markup(reply_markup=city_kb())


async def user_city_add(callback, callback_data):
    def city_add_kb() -> InlineKeyboardMarkup:
        kb = InlineKeyboardBuilder()
        kb.button(
            text=f"Продолжить", callback_data=UserCityStatusCF(
                add=False,
                next=True,
                country=callback_data.country,
                cities=callback_data.cities)
        )
        kb.button(
            text=f"Добавить еще город", callback_data=UserCityStatusCF(
                add=True,
                next=False,
                country=callback_data.country,
                cities=callback_data.cities)
        )
        kb.add(InlineKeyboardButton(
            text="Отмена", callback_data="cancel"
        ))
        kb.adjust(1)
        return kb.as_markup()

    new_line = '\n'

    list_cities = callback_data.cities.split()
    cities = await ChannelsQs.get_user_cities(list_cities)

    await callback.message.edit_text(f"Вы выбрали следующие данные:\n"
                                     f"Страна - {callback_data.country}\n"
                                     f"Города:\n"
                                     f"{new_line.join(f'{city[0]} ({city[1]} руб.)' for city in cities)}")
    await callback.message.edit_reply_markup(reply_markup=city_add_kb())


