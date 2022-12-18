import logging
from datetime import date, timedelta
from datetime import datetime as dt
from pathlib import Path

import phonenumbers
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from environs import Env

import db_methods
from registration import Register

env = Env()
env.read_env()
tg_token = env.str("TG_BOT_TOKEN")
db_file_name = env.str("DB_FILE_NAME", "db.json")
db_file_path = Path(db_file_name)
loaded_db = db_methods.load_json(db_file_path)

premises_db_file_name = env.str("PREMISES_DB_FILE_NAME", "premises.json")
premises_db_file_path = Path(premises_db_file_name)
loaded_premises_db = db_methods.load_json(premises_db_file_path)

services_db_file_name = env.str("SERVICES_DB_FILE_NAME", "services.json")
services_db_file_path = Path(services_db_file_name)
loaded_services_db = db_methods.load_json(services_db_file_path)

specialists_db_file_name = env.str("SPECIALISTS_DB_FILE_NAME", "specialists.json")
specialists_db_file_path = Path(specialists_db_file_name)
loaded_specialists_db = db_methods.load_json(specialists_db_file_path)

logging.basicConfig(level=logging.INFO)
bot = Bot(token=tg_token)
dp = Dispatcher(bot, storage=MemoryStorage())

# --- Order Counter And Globals---

local_time = dt.now()
today = date.today()

order_id = 1
premise_name = ""
service_name = ""
service_price = ""
specialist_name = ""
specialist_index = ""
day_slot_list = []
day_slot_index = ""
day_picked = ""
time_slot_list = []
time_picked = ""
history_orders_list = []  # service_name, premise_name, specialist_name

specialist_finder = {
    "Beauty Hair": {
        "Brad Pitt": 0,
        "Sir Alex Ferguson": 1,
        "Ewan McGregor": 14
    },
    "Birdie": {
        "Mike Myers": 2,
        "Leatherface": 3
    },
    "Expat Salon": {
        "Ilya Osipov": 4,
        "Leo Messi": 5,
        "Benedict Cumberbatch": 12
    },
    "Brush Beauty Salon": {
        "Witcher": 8,
        "Charlize Theron": 9
    },
    "Beauty Point": {
        "Arnold Schwarzenegger": 6,
        "Wednesday": 7
    },
    "Iris": {
        "Jen Aniston": 10,
        "Rachel McAdams": 11,
        "Nathalie Emmanuel": 13
    }
}

# --- TIMESLOTS MANAGER ---
# SHOULD BE EXECUTED ONCE PER DAY
# IS COMMENTED OUT AT THE MOMENT - SHOULD DECIDE WHEN TO RUN IT AND HOW

import json


def timeslots_manager_load():
    with open('specialists.json', 'r', encoding='utf-8') as file:
        specialists = json.load(file)
        if specialists['specialists'][0]['date_available'][0] == str(today):
            for time_slot in specialists['specialists']:
                del time_slot['date_available'][0]
            if (len(specialists['specialists'][0]['date_available'])) < 7:
                for time_slot in specialists['specialists']:
                    time_slot['date_available'].append({str(today + timedelta(days=6)): ['10-00', '11-00', '12-00',
                                                                                         '13-00', '14-00', '15-00',
                                                                                         '16-00', '17-00', '18-00',
                                                                                         '19-00']})
    return specialists


def time_slot_manager_save(spec_data):
    with open('specialists.json', 'w', encoding='utf-8') as file:
        json.dump(spec_data, file)


data2 = timeslots_manager_load()
time_slot_manager_save(data2)


# This one removes time slot when the order is placed
# time_slot_manager_save(data2) can be used to save the data

def remove_timeslot_load():
    with open('specialists.json', 'r', encoding='utf-8') as file:
        specialists = json.load(file)
        specialists['specialists'][specialist_index]['date_available'][day_slot_index][day_picked].remove(time_picked)
    return specialists


# --- Inline Buttons Builder ---

def gen_markup(texts: list, prefix: str, row_width: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=row_width, resize_keyboard=True)
    for num, text in enumerate(texts):
        markup.insert(InlineKeyboardButton(f"{text}", callback_data=f"{prefix}:{num}"))
    return markup


# --- Main Menu ---
# When /start or /help command received the bot would give 2 buttons: "Записаться на процедуру" & "Личный кабинет" (reply_markup = navi.main_menu)

welcome_button = InlineKeyboardButton(text="Записаться на процедуру", callback_data="make_appointment")
order_history_button = InlineKeyboardButton(text="Посмотреть историю заказов", callback_data="order_history_request")
welcome_keyboard = InlineKeyboardMarkup().add(welcome_button, order_history_button)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply("Привет! Я - бот BeautyCity, запишемся на процедуру?", reply_markup=welcome_keyboard)


@dp.callback_query_handler(text=["order_history_request"])
async def welcome(call: types.CallbackQuery):
    order_history_button = InlineKeyboardButton(text="К списку заказов", callback_data="history_requested")
    order_history_keyboard = InlineKeyboardMarkup().add(order_history_button)
    await bot.send_message(call.message.chat.id, "Загружаем историю", reply_markup=order_history_keyboard)


@dp.callback_query_handler(text=["make_appointment"])
async def welcome(call: types.CallbackQuery):
    order_button = InlineKeyboardButton(text="Выбрать салон", callback_data="Записаться на процедуру")
    make_order_keyboard = InlineKeyboardMarkup().add(order_button)
    await bot.send_message(call.message.chat.id, "Давайте выберем салон", reply_markup=make_order_keyboard)


# --- Orders History ---
# Add order repeat here
# Placeholder

@dp.callback_query_handler(text=["history_requested"])
async def make_order(message: types.Message):
    orders_list = []
    loaded_db = db_methods.load_json(db_file_path)
    clients_table = loaded_db["items"][0]["items"]
    client = db_methods.search_client(loaded_db["items"][0]["items"], message.from_user.id)

    if client is not None:
        for client_order in client["client_orders"]:
            orders_list.append(client_order)
        if len(orders_list) == 0:
            no_history_button = InlineKeyboardButton(text="Похоже вы раньше у нас не были, вернемся к выбору салона?",
                                                     callback_data="make_appointment")
            no_history_keyboard = InlineKeyboardMarkup().add(no_history_button)
            await bot.send_message(message.from_user.id,
                                   f"Чтобы повторить заказ (при наличии истории) - нажмите на него",
                                   reply_markup=no_history_keyboard)
        else:
            order_list_temp = []
            for order in orders_list:
                order_list_temp.append(
                    [order['service_name'], order['premise_name'], order['specialist'], order['visit_date']])
                orders_list = order_list_temp
                if len(orders_list) > 1 and len(orders_list) >= 5:
                    new_dict = []
                    for item in range(1, 4):
                        new_dict.append(orders_list[item * -1])
                        new_dict.append(orders_list[0])
                    orders_list = new_dict

                elif len(orders_list) > 1 and len(orders_list) < 5:
                    new_dict = []
                    for item in range(1, len(orders_list)):
                        new_dict.append(orders_list[item * -1])
                    new_dict.append(orders_list[0])
                    orders_list = new_dict

                else:
                    orders_list = orders_list

            global history_orders_list
            history_orders_list = orders_list

            markup = gen_markup(orders_list, "order", 1)
            await bot.send_message(message.from_user.id,
                                   f"Чтобы повторить заказ (при наличии истории) - нажмите на него",
                                   reply_markup=markup)

    else:
        orders_list.append("No prevous orders found")
        no_history_button = InlineKeyboardButton(text="Похоже вы тут впервые, вернемся к выбору салона?",
                                                 callback_data="make_appointment")
        no_history_keyboard = InlineKeyboardMarkup().add(no_history_button)
        await bot.send_message(message.from_user.id, f"Чтобы повторить заказ (при наличии истории) - нажмите на него",
                               reply_markup=no_history_keyboard)


# Catching previous orders
# possible = 5

@dp.callback_query_handler(text=["order:0"])
async def make_order(message: types.Message):
    order_repeat_data = history_orders_list[0]
    # service_name, premise_name, specialist_name
    global service_name
    service_name = history_orders_list[0][0]
    global premise_name
    premise_name = history_orders_list[0][1]
    global specialist_name
    specialist_name = history_orders_list[0][2]

    order_repeat_confirm_button = InlineKeyboardButton(text="Повторить услугу", callback_data="specialist_picked")
    order_repeat_back_button = InlineKeyboardButton(text="Назад к истории заказов", callback_data="history_requested")
    order_repeat_keyboard = InlineKeyboardMarkup().add(order_repeat_confirm_button).add(order_repeat_back_button)
    await bot.send_message(message.from_user.id,
                           f"Вы желаете повторить услугу: {service_name}, в салоне: {premise_name}, у мастера: {specialist_name}",
                           reply_markup=order_repeat_keyboard)


@dp.callback_query_handler(text=["order:1"])
async def make_order(message: types.Message):
    order_repeat_data = history_orders_list[1]
    # service_name, premise_name, specialist_name
    global service_name
    service_name = history_orders_list[1][0]
    global premise_name
    premise_name = history_orders_list[1][1]
    global specialist_name
    specialist_name = history_orders_list[1][2]

    order_repeat_confirm_button = InlineKeyboardButton(text="Повторить услугу", callback_data="specialist_picked")
    order_repeat_back_button = InlineKeyboardButton(text="Назад к истории заказов", callback_data="history_requested")
    order_repeat_keyboard = InlineKeyboardMarkup().add(order_repeat_confirm_button).add(order_repeat_back_button)
    await bot.send_message(message.from_user.id,
                           f"Вы желаете повторить услугу: {service_name}, в салоне: {premise_name}, у мастера: {specialist_name}",
                           reply_markup=order_repeat_keyboard)


@dp.callback_query_handler(text=["order:2"])
async def make_order(message: types.Message):
    order_repeat_data = history_orders_list[2]
    # service_name, premise_name, specialist_name
    global service_name
    service_name = history_orders_list[2][0]
    global premise_name
    premise_name = history_orders_list[2][1]
    global specialist_name
    specialist_name = history_orders_list[2][2]

    order_repeat_confirm_button = InlineKeyboardButton(text="Повторить услугу", callback_data="specialist_picked")
    order_repeat_back_button = InlineKeyboardButton(text="Назад к истории заказов", callback_data="history_requested")
    order_repeat_keyboard = InlineKeyboardMarkup().add(order_repeat_confirm_button).add(order_repeat_back_button)
    await bot.send_message(message.from_user.id,
                           f"Вы желаете повторить услугу: {service_name}, в салоне: {premise_name}, у мастера: {specialist_name}",
                           reply_markup=order_repeat_keyboard)


@dp.callback_query_handler(text=["order:3"])
async def make_order(message: types.Message):
    order_repeat_data = history_orders_list[3]
    # service_name, premise_name, specialist_name
    global service_name
    service_name = history_orders_list[3][0]
    global premise_name
    premise_name = history_orders_list[3][1]
    global specialist_name
    specialist_name = history_orders_list[3][2]

    order_repeat_confirm_button = InlineKeyboardButton(text="Повторить услугу", callback_data="specialist_picked")
    order_repeat_back_button = InlineKeyboardButton(text="Назад к истории заказов", callback_data="history_requested")
    order_repeat_keyboard = InlineKeyboardMarkup().add(order_repeat_confirm_button).add(order_repeat_back_button)
    await bot.send_message(message.from_user.id,
                           f"Вы желаете повторить услугу: {service_name}, в салоне: {premise_name}, у мастера: {specialist_name}",
                           reply_markup=order_repeat_keyboard)


@dp.callback_query_handler(text=["order:4"])
async def make_order(message: types.Message):
    order_repeat_data = history_orders_list[4]
    # service_name, premise_name, specialist_name
    global service_name
    service_name = history_orders_list[4][0]
    global premise_name
    premise_name = history_orders_list[4][1]
    global specialist_name
    specialist_name = history_orders_list[4][2]

    order_repeat_confirm_button = InlineKeyboardButton(text="Повторить услугу", callback_data="specialist_picked")
    order_repeat_back_button = InlineKeyboardButton(text="Назад к истории заказов", callback_data="history_requested")
    order_repeat_keyboard = InlineKeyboardMarkup().add(order_repeat_confirm_button).add(order_repeat_back_button)
    await bot.send_message(message.from_user.id,
                           f"Вы желаете повторить услугу: {service_name}, в салоне: {premise_name}, у мастера: {specialist_name}",
                           reply_markup=order_repeat_keyboard)


# --- Make Appointment ---
# When "Записаться на процедуру" is tapped the bot will display the list of available premises

@dp.callback_query_handler(text=["Записаться на процедуру"])
async def make_order(message: types.Message):
    premises = loaded_premises_db
    list = []
    for i in range(0, len(premises['premises'])):
        list.append(f"{premises['premises'][i]['premise_name']}: {premises['premises'][i]['premise_address']}")
    markup = gen_markup(list, "prefix", 1)
    await bot.send_message(message.from_user.id, f"Какой салон Вам больше нравится?", reply_markup=markup)


# When the appointment is tapped the bot will display the list of available premises
# --- Pick Premise ---

@dp.callback_query_handler(text=["prefix:0"])
async def make_order(message: types.Message):
    premises = loaded_premises_db
    global premise_name
    premise_name = premises['premises'][0]['premise_name']
    salon_button = InlineKeyboardButton(text="Выбрать услугу", callback_data="premise_picked")
    salon_keyboard = InlineKeyboardMarkup().add(salon_button)
    await bot.send_message(message.from_user.id,
                           f"Вы выбрали {premises['premises'][0]['premise_name']}: {premises['premises'][0]['premise_address']}",
                           reply_markup=salon_keyboard)


@dp.callback_query_handler(text=["prefix:1"])
async def make_order(message: types.Message):
    premises = loaded_premises_db
    global premise_name
    premise_name = premises['premises'][1]['premise_name']
    salon_button = InlineKeyboardButton(text="Выбрать услугу", callback_data="premise_picked")
    salon_keyboard = InlineKeyboardMarkup().add(salon_button)

    await bot.send_message(message.from_user.id,
                           f"Вы выбрали {premises['premises'][1]['premise_name']}: {premises['premises'][1]['premise_address']}",
                           reply_markup=salon_keyboard)


@dp.callback_query_handler(text=["prefix:2"])
async def make_order(message: types.Message):
    premises = loaded_premises_db
    global premise_name
    premise_name = premises['premises'][2]['premise_name']
    salon_button = InlineKeyboardButton(text="Выбрать услугу", callback_data="premise_picked")
    salon_keyboard = InlineKeyboardMarkup().add(salon_button)
    await bot.send_message(message.from_user.id,
                           f"Вы выбрали {premises['premises'][2]['premise_name']}: {premises['premises'][2]['premise_address']}",
                           reply_markup=salon_keyboard)


@dp.callback_query_handler(text=["prefix:3"])
async def make_order(message: types.Message):
    premises = loaded_premises_db
    global premise_name
    premise_name = premises['premises'][3]['premise_name']
    salon_button = InlineKeyboardButton(text="Выбрать услугу", callback_data="premise_picked")
    salon_keyboard = InlineKeyboardMarkup().add(salon_button)
    await bot.send_message(message.from_user.id,
                           f"Вы выбрали {premises['premises'][3]['premise_name']}: {premises['premises'][3]['premise_address']}",
                           reply_markup=salon_keyboard)


@dp.callback_query_handler(text=["prefix:4"])
async def make_order(message: types.Message):
    premises = loaded_premises_db
    global premise_name
    premise_name = premises['premises'][4]['premise_name']
    salon_button = InlineKeyboardButton(text="Выбрать услугу", callback_data="premise_picked")
    salon_keyboard = InlineKeyboardMarkup().add(salon_button)
    await bot.send_message(message.from_user.id,
                           f"Вы выбрали {premises['premises'][4]['premise_name']}: {premises['premises'][4]['premise_address']}",
                           reply_markup=salon_keyboard)


@dp.callback_query_handler(text=["prefix:5"])
async def make_order(message: types.Message):
    premises = loaded_premises_db
    salon_button = InlineKeyboardButton(text="Выбрать услугу", callback_data="premise_picked")
    global premise_name
    premise_name = premises['premises'][5]['premise_name']
    salon_keyboard = InlineKeyboardMarkup().add(salon_button)
    await bot.send_message(message.from_user.id,
                           f"Вы выбрали {premises['premises'][5]['premise_name']}: {premises['premises'][5]['premise_address']}",
                           reply_markup=salon_keyboard)


# When the salon is tapped the bot will display the list of available services
# --- Pick Service ---


@dp.callback_query_handler(text="premise_picked")
async def make_order(message: types.Message):
    services = loaded_services_db
    services_list = []
    for service in services['services']:
        services_list.append(service["service_name"])
    service_markup = gen_markup(services_list, "service", 1)
    await bot.send_message(message.from_user.id, f"Какую услугу закажем?", reply_markup=service_markup)


# After picking the service -> printout the price and back button

@dp.callback_query_handler(text=["service:0"])
async def make_order(message: types.Message):
    services = loaded_services_db
    service_button = InlineKeyboardButton(
        text=f"Записаться на {services['services'][0]['service_name']}, стоимость услуги = {services['services'][0]['service_price']} руб.",
        callback_data="service_picked")
    back_button = InlineKeyboardButton(text="Назад к выбору услуги", callback_data="premise_picked")
    service_keyboard = InlineKeyboardMarkup().add(service_button).add(back_button)
    global service_name
    service_name = services['services'][0]['service_name']
    global service_price
    service_price = services['services'][0]['service_price']
    global service_duration
    service_price = services['services'][0]['service_duration']
    await bot.send_message(message.from_user.id, f"Отличный выбор, но можно и вернуться к выбору услуг",
                           reply_markup=service_keyboard)


@dp.callback_query_handler(text=["service:1"])
async def make_order(message: types.Message):
    services = loaded_services_db
    service_button = InlineKeyboardButton(
        text=f"Записаться на {services['services'][1]['service_name']}, стоимость услуги = {services['services'][1]['service_price']} руб.",
        callback_data="service_picked")
    back_button = InlineKeyboardButton(text="Назад к выбору услуги", callback_data="premise_picked")
    service_keyboard = InlineKeyboardMarkup().add(service_button).add(back_button)
    global service_name
    service_name = services['services'][1]['service_name']
    global service_price
    service_price = services['services'][1]['service_price']
    global service_duration
    service_price = services['services'][1]['service_duration']
    await bot.send_message(message.from_user.id, f"Отличный выбор, но можно и вернуться к выбору услуг",
                           reply_markup=service_keyboard)


@dp.callback_query_handler(text=["service:2"])
async def make_order(message: types.Message):
    services = loaded_services_db
    service_button = InlineKeyboardButton(
        text=f"Записаться на {services['services'][2]['service_name']}, стоимость услуги = {services['services'][2]['service_price']} руб.",
        callback_data="service_picked")
    back_button = InlineKeyboardButton(text="Назад к выбору услуги", callback_data="premise_picked")
    service_keyboard = InlineKeyboardMarkup().add(service_button).add(back_button)
    global service_name
    service_name = services['services'][2]['service_name']
    global service_price
    service_price = services['services'][2]['service_price']
    global service_duration
    service_price = services['services'][2]['service_duration']
    await bot.send_message(message.from_user.id, f"Отличный выбор, но можно и вернуться к выбору услуг",
                           reply_markup=service_keyboard)


@dp.callback_query_handler(text=["service:3"])
async def make_order(message: types.Message):
    services = loaded_services_db
    service_button = InlineKeyboardButton(
        text=f"Записаться на {services['services'][3]['service_name']}, стоимость услуги = {services['services'][3]['service_price']} руб.",
        callback_data="service_picked")
    back_button = InlineKeyboardButton(text="Назад к выбору услуги", callback_data="premise_picked")
    service_keyboard = InlineKeyboardMarkup().add(service_button).add(back_button)
    global service_name
    service_name = services['services'][3]['service_name']
    global service_price
    service_price = services['services'][3]['service_price']
    global service_duration
    service_price = services['services'][3]['service_duration']
    await bot.send_message(message.from_user.id, f"Отличный выбор, но можно и вернуться к выбору услуг",
                           reply_markup=service_keyboard)


@dp.callback_query_handler(text=["service:4"])
async def make_order(message: types.Message):
    services = loaded_services_db
    service_button = InlineKeyboardButton(
        text=f"Записаться на {services['services'][4]['service_name']}, стоимость услуги = {services['services'][4]['service_price']} руб.",
        callback_data="service_picked")
    back_button = InlineKeyboardButton(text="Назад к выбору услуги", callback_data="premise_picked")
    service_keyboard = InlineKeyboardMarkup().add(service_button).add(back_button)
    global service_name
    service_name = services['services'][4]['service_name']
    global service_price
    service_price = services['services'][4]['service_price']
    global service_duration
    service_price = services['services'][4]['service_duration']
    await bot.send_message(message.from_user.id, f"Отличный выбор, но можно и вернуться к выбору услуг",
                           reply_markup=service_keyboard)


@dp.callback_query_handler(text=["service:5"])
async def make_order(message: types.Message):
    services = loaded_services_db
    service_button = InlineKeyboardButton(
        text=f"Записаться на {services['services'][5]['service_name']}, стоимость услуги = {services['services'][5]['service_price']} руб.",
        callback_data="service_picked")
    back_button = InlineKeyboardButton(text="Назад к выбору услуги", callback_data="premise_picked")
    service_keyboard = InlineKeyboardMarkup().add(service_button).add(back_button)
    global service_name
    service_name = services['services'][5]['service_name']
    global service_price
    service_price = services['services'][5]['service_price']
    global service_duration
    service_price = services['services'][5]['service_duration']
    await bot.send_message(message.from_user.id, f"Отличный выбор, но можно и вернуться к выбору услуг",
                           reply_markup=service_keyboard)


@dp.callback_query_handler(text=["service:6"])
async def make_order(message: types.Message):
    services = loaded_services_db
    service_button = InlineKeyboardButton(
        text=f"Записаться на {services['services'][6]['service_name']}, стоимость услуги = {services['services'][6]['service_price']} руб.",
        callback_data="service_picked")
    back_button = InlineKeyboardButton(text="Назад к выбору услуги", callback_data="premise_picked")
    service_keyboard = InlineKeyboardMarkup().add(service_button).add(back_button)
    global service_name
    service_name = services['services'][6]['service_name']
    global service_price
    service_price = services['services'][6]['service_price']
    global service_duration
    service_price = services['services'][6]['service_duration']
    await bot.send_message(message.from_user.id, f"Отличный выбор, но можно и вернуться к выбору услуг",
                           reply_markup=service_keyboard)


@dp.callback_query_handler(text=["service:7"])
async def make_order(message: types.Message):
    services = loaded_services_db
    service_button = InlineKeyboardButton(
        text=f"Записаться на {services['services'][7]['service_name']}, стоимость услуги = {services['services'][7]['service_price']} руб.",
        callback_data="service_picked")
    back_button = InlineKeyboardButton(text="Назад к выбору услуги", callback_data="premise_picked")
    service_keyboard = InlineKeyboardMarkup().add(service_button).add(back_button)
    global service_name
    service_name = services['services'][7]['service_name']
    global service_price
    service_price = services['services'][7]['service_price']
    global service_duration
    service_price = services['services'][7]['service_duration']
    await bot.send_message(message.from_user.id, f"Отличный выбор, но можно и вернуться к выбору услуг",
                           reply_markup=service_keyboard)


@dp.callback_query_handler(text=["service:8"])
async def make_order(message: types.Message):
    services = loaded_services_db
    service_button = InlineKeyboardButton(
        text=f"Записаться на {services['services'][8]['service_name']}, стоимость услуги = {services['services'][8]['service_price']} руб.",
        callback_data="service_picked")
    back_button = InlineKeyboardButton(text="Назад к выбору услуги", callback_data="premise_picked")
    service_keyboard = InlineKeyboardMarkup().add(service_button).add(back_button)
    global service_name
    service_name = services['services'][8]['service_name']
    global service_price
    service_price = services['services'][8]['service_price']
    global service_duration
    service_price = services['services'][8]['service_duration']
    await bot.send_message(message.from_user.id, f"Отличный выбор, но можно и вернуться к выбору услуг",
                           reply_markup=service_keyboard)


@dp.callback_query_handler(text=["service:9"])
async def make_order(message: types.Message):
    services = loaded_services_db
    service_button = InlineKeyboardButton(
        text=f"Записаться на {services['services'][9]['service_name']}, стоимость услуги = {services['services'][9]['service_price']} руб.",
        callback_data="service_picked")
    back_button = InlineKeyboardButton(text="Назад к выбору услуги", callback_data="premise_picked")
    service_keyboard = InlineKeyboardMarkup().add(service_button).add(back_button)
    global service_name
    service_name = services['services'][9]['service_name']
    global service_price
    service_price = services['services'][9]['service_price']
    global service_duration
    service_price = services['services'][9]['service_duration']
    await bot.send_message(message.from_user.id, f"Отличный выбор, но можно и вернуться к выбору услуг",
                           reply_markup=service_keyboard)


## When the service is picked the bot will display the list of available specialists
## --- Pick Specialist ---

@dp.callback_query_handler(text=["service_picked"])
async def make_order(message: types.Message):
    premises = loaded_premises_db
    index_set = {
        "Beauty Hair": 0,
        "Birdie": 1,
        "Expat Salon": 2,
        "Brush Beauty Salon": 3,
        "Beauty Point": 4,
        "Iris": 5
    }
    specialist_list = premises['premises'][index_set[f'{premise_name}']]['specialists']
    specialist_markup = gen_markup(specialist_list, "specialist", 1)
    await bot.send_message(message.from_user.id, f"Выберите, пожалуйста, мастера", reply_markup=specialist_markup)


# When specialist is picked - bot displays available dates for this specialist and after date - available time slots

@dp.callback_query_handler(text=["specialist:0"])
async def make_order(message: types.Message):
    premises = loaded_premises_db
    index_set = {
        "Beauty Hair": 0,
        "Birdie": 1,
        "Expat Salon": 2,
        "Brush Beauty Salon": 3,
        "Beauty Point": 4,
        "Iris": 5
    }
    specialist_button = InlineKeyboardButton(text="Выбрать дату оказания услуги", callback_data="specialist_picked")
    service_keyboard = InlineKeyboardMarkup().add(specialist_button)
    global specialist_name
    specialist_name = premises['premises'][index_set[f'{premise_name}']]['specialists'][0]
    await bot.send_message(message.from_user.id, f"Отличный выбор, {specialist_name} просто огонь!",
                           reply_markup=service_keyboard)


@dp.callback_query_handler(text=["specialist:1"])
async def make_order(message: types.Message):
    premises = loaded_premises_db
    index_set = {
        "Beauty Hair": 0,
        "Birdie": 1,
        "Expat Salon": 2,
        "Brush Beauty Salon": 3,
        "Beauty Point": 4,
        "Iris": 5
    }
    specialist_button = InlineKeyboardButton(text="Выбрать дату оказания услуги", callback_data="specialist_picked")
    service_keyboard = InlineKeyboardMarkup().add(specialist_button)
    global specialist_name
    specialist_name = premises['premises'][index_set[f'{premise_name}']]['specialists'][1]
    await bot.send_message(message.from_user.id, f"Отличный выбор, {specialist_name} просто огонь!",
                           reply_markup=service_keyboard)


@dp.callback_query_handler(text=["specialist:2"])
async def make_order(message: types.Message):
    premises = loaded_premises_db
    index_set = {
        "Beauty Hair": 0,
        "Birdie": 1,
        "Expat Salon": 2,
        "Brush Beauty Salon": 3,
        "Beauty Point": 4,
        "Iris": 5
    }
    specialist_button = InlineKeyboardButton(text="Выбрать дату оказания услуги", callback_data="specialist_picked")
    service_keyboard = InlineKeyboardMarkup().add(specialist_button)
    global specialist_name
    specialist_name = premises['premises'][index_set[f'{premise_name}']]['specialists'][2]
    await bot.send_message(message.from_user.id, f"Отличный выбор, {specialist_name} просто огонь!",
                           reply_markup=service_keyboard)


# Here the bot should give available time slots for given specialist:
# First come days

@dp.callback_query_handler(text=["specialist_picked"])
async def make_order(message: types.Message):
    specialists = loaded_specialists_db
    days_list = []
    global specialist_index
    specialist_index = specialist_finder[premise_name][specialist_name]
    for day in range(0, 6):
        for slots in specialists['specialists'][specialist_index]['date_available'][day]:
            # This one detects if the day slot is empty, if it is empty - the bot won't print it:
            if specialists['specialists'][specialist_index]['date_available'][day]:
                days_list.append(slots)
    date_slot_markup = gen_markup(days_list, "day_slot", 1)
    global day_slot_list
    day_slot_list = days_list
    await bot.send_message(message.from_user.id, f"На какую дату Вас записать?", reply_markup=date_slot_markup)


# Fetching the slot number in global day_slot_list:
# Picking the date

@dp.callback_query_handler(text=["day_slot:0"])
async def make_order(message: types.Message):
    day_slot = day_slot_list[0]
    time_slot_button = InlineKeyboardButton(text="Подтвердить", callback_data="date_picked")
    time_slot_back_button = InlineKeyboardButton(text="Выбрать другую дату", callback_data="specialist_picked")
    time_slot_keyboard = InlineKeyboardMarkup().add(time_slot_button).add(time_slot_back_button)
    global day_picked
    day_picked = day_slot_list[0]
    global day_slot_index
    day_slot_index = 0
    await bot.send_message(message.from_user.id, f"Дата оказания услуги: {day_slot}", reply_markup=time_slot_keyboard)


@dp.callback_query_handler(text=["day_slot:1"])
async def make_order(message: types.Message):
    day_slot = day_slot_list[1]
    time_slot_button = InlineKeyboardButton(text="Подтвердить", callback_data="date_picked")
    time_slot_back_button = InlineKeyboardButton(text="Выбрать другую дату", callback_data="specialist_picked")
    time_slot_keyboard = InlineKeyboardMarkup().add(time_slot_button).add(time_slot_back_button)
    global day_picked
    day_picked = day_slot_list[1]
    global day_slot_index
    day_slot_index = 1
    await bot.send_message(message.from_user.id, f"Дата оказания услуги: {day_slot}", reply_markup=time_slot_keyboard)


@dp.callback_query_handler(text=["day_slot:2"])
async def make_order(message: types.Message):
    day_slot = day_slot_list[2]
    time_slot_button = InlineKeyboardButton(text="Подтвердить", callback_data="date_picked")
    time_slot_back_button = InlineKeyboardButton(text="Выбрать другую дату", callback_data="specialist_picked")
    time_slot_keyboard = InlineKeyboardMarkup().add(time_slot_button).add(time_slot_back_button)
    global day_picked
    day_picked = day_slot_list[2]
    global day_slot_index
    day_slot_index = 2
    await bot.send_message(message.from_user.id, f"Дата оказания услуги: {day_slot}", reply_markup=time_slot_keyboard)


@dp.callback_query_handler(text=["day_slot:3"])
async def make_order(message: types.Message):
    day_slot = day_slot_list[3]
    time_slot_button = InlineKeyboardButton(text="Подтвердить", callback_data="date_picked")
    time_slot_back_button = InlineKeyboardButton(text="Выбрать другую дату", callback_data="specialist_picked")
    time_slot_keyboard = InlineKeyboardMarkup().add(time_slot_button).add(time_slot_back_button)
    global day_picked
    day_picked = day_slot_list[3]
    global day_slot_index
    day_slot_index = 3
    await bot.send_message(message.from_user.id, f"Дата оказания услуги: {day_slot}", reply_markup=time_slot_keyboard)


@dp.callback_query_handler(text=["day_slot:4"])
async def make_order(message: types.Message):
    day_slot = day_slot_list[4]
    time_slot_button = InlineKeyboardButton(text="Подтвердить", callback_data="date_picked")
    time_slot_back_button = InlineKeyboardButton(text="Выбрать другую дату", callback_data="specialist_picked")
    time_slot_keyboard = InlineKeyboardMarkup().add(time_slot_button).add(time_slot_back_button)
    global day_picked
    day_picked = day_slot_list[4]
    global day_slot_index
    day_slot_index = 4
    await bot.send_message(message.from_user.id, f"Дата оказания услуги: {day_slot}", reply_markup=time_slot_keyboard)


@dp.callback_query_handler(text=["day_slot:5"])
async def make_order(message: types.Message):
    day_slot = day_slot_list[5]
    time_slot_button = InlineKeyboardButton(text="Подтвердить", callback_data="date_picked")
    time_slot_back_button = InlineKeyboardButton(text="Выбрать другую дату", callback_data="specialist_picked")
    time_slot_keyboard = InlineKeyboardMarkup().add(time_slot_button).add(time_slot_back_button)
    global day_picked
    day_picked = day_slot_list[5]
    global day_slot_index
    day_slot_index = 5
    await bot.send_message(message.from_user.id, f"Дата оказания услуги: {day_slot}", reply_markup=time_slot_keyboard)


@dp.callback_query_handler(text=["day_slot:6"])
async def make_order(message: types.Message):
    day_slot = day_slot_list[6]
    time_slot_button = InlineKeyboardButton(text="Подтвердить", callback_data="date_picked")
    time_slot_back_button = InlineKeyboardButton(text="Выбрать другую дату", callback_data="specialist_picked")
    time_slot_keyboard = InlineKeyboardMarkup().add(time_slot_button).add(time_slot_back_button)
    global day_picked
    day_picked = day_slot_list[6]
    global day_slot_index
    day_slot_index = 6
    await bot.send_message(message.from_user.id, f"Дата оказания услуги: {day_slot}", reply_markup=time_slot_keyboard)


@dp.callback_query_handler(text=["day_slot:7"])
async def make_order(message: types.Message):
    day_slot = day_slot_list[7]
    time_slot_button = InlineKeyboardButton(text="Подтвердить", callback_data="date_picked")
    time_slot_back_button = InlineKeyboardButton(text="Выбрать другую дату", callback_data="specialist_picked")
    time_slot_keyboard = InlineKeyboardMarkup().add(time_slot_button).add(time_slot_back_button)
    global day_picked
    day_picked = day_slot_list[7]
    global day_slot_index
    day_slot_index = 7
    await bot.send_message(message.from_user.id, f"Дата оказания услуги: {day_slot}", reply_markup=time_slot_keyboard)


@dp.callback_query_handler(text=["day_slot:8"])
async def make_order(message: types.Message):
    day_slot = day_slot_list[8]
    time_slot_button = InlineKeyboardButton(text="Подтвердить", callback_data="date_picked")
    time_slot_back_button = InlineKeyboardButton(text="Выбрать другую дату", callback_data="specialist_picked")
    time_slot_keyboard = InlineKeyboardMarkup().add(time_slot_button).add(time_slot_back_button)
    global day_picked
    day_picked = day_slot_list[8]
    global day_slot_index
    day_slot_index = 8
    await bot.send_message(message.from_user.id, f"Дата оказания услуги: {day_slot}", reply_markup=time_slot_keyboard)


@dp.callback_query_handler(text=["date_picked"])
async def make_order(message: types.Message):
    specialists = loaded_specialists_db
    times_list = []
    global specialist_index
    specialist_index = specialist_finder[premise_name][specialist_name]
    for time in specialists['specialists'][specialist_index]['date_available'][day_slot_index][day_picked]:
        times_list.append(time)
    time_slot_markup = gen_markup(times_list, "time_slot", 1)
    global time_slot_list
    time_slot_list = times_list
    await bot.send_message(message.from_user.id, f"На какое время Вас записать?", reply_markup=time_slot_markup)


# 10 slots

@dp.callback_query_handler(text=["time_slot:0"])
async def make_order(message: types.Message):
    time_slot_button = InlineKeyboardButton(text="Подтвердить", callback_data="time_picked")
    time_slot_back_button = InlineKeyboardButton(text="Выбрать другое время", callback_data="date_picked")
    time_slot_keyboard = InlineKeyboardMarkup().add(time_slot_button).add(time_slot_back_button)
    global time_picked
    time_picked = time_slot_list[0]
    global time_slot_index
    time_slot_index = 0
    await bot.send_message(message.from_user.id, f"Время оказания услуги: {time_picked}",
                           reply_markup=time_slot_keyboard)


@dp.callback_query_handler(text=["time_slot:1"])
async def make_order(message: types.Message):
    time_slot_button = InlineKeyboardButton(text="Подтвердить", callback_data="time_picked")
    time_slot_back_button = InlineKeyboardButton(text="Выбрать другое время", callback_data="date_picked")
    time_slot_keyboard = InlineKeyboardMarkup().add(time_slot_button).add(time_slot_back_button)
    global time_picked
    time_picked = time_slot_list[1]
    global time_slot_index
    time_slot_index = 1
    await bot.send_message(message.from_user.id, f"Время оказания услуги: {time_picked}",
                           reply_markup=time_slot_keyboard)


@dp.callback_query_handler(text=["time_slot:2"])
async def make_order(message: types.Message):
    time_slot_button = InlineKeyboardButton(text="Подтвердить", callback_data="time_picked")
    time_slot_back_button = InlineKeyboardButton(text="Выбрать другое время", callback_data="date_picked")
    time_slot_keyboard = InlineKeyboardMarkup().add(time_slot_button).add(time_slot_back_button)
    global time_picked
    time_picked = time_slot_list[2]
    global time_slot_index
    time_slot_index = 2
    await bot.send_message(message.from_user.id, f"Время оказания услуги: {time_picked}",
                           reply_markup=time_slot_keyboard)


@dp.callback_query_handler(text=["time_slot:3"])
async def make_order(message: types.Message):
    time_slot_button = InlineKeyboardButton(text="Подтвердить", callback_data="time_picked")
    time_slot_back_button = InlineKeyboardButton(text="Выбрать другое время", callback_data="date_picked")
    time_slot_keyboard = InlineKeyboardMarkup().add(time_slot_button).add(time_slot_back_button)
    global time_picked
    time_picked = time_slot_list[3]
    global time_slot_index
    time_slot_index = 3
    await bot.send_message(message.from_user.id, f"Время оказания услуги: {time_picked}",
                           reply_markup=time_slot_keyboard)


@dp.callback_query_handler(text=["time_slot:4"])
async def make_order(message: types.Message):
    time_slot_button = InlineKeyboardButton(text="Подтвердить", callback_data="time_picked")
    time_slot_back_button = InlineKeyboardButton(text="Выбрать другое время", callback_data="date_picked")
    time_slot_keyboard = InlineKeyboardMarkup().add(time_slot_button).add(time_slot_back_button)
    global time_picked
    time_picked = time_slot_list[4]
    global time_slot_index
    time_slot_index = 4
    await bot.send_message(message.from_user.id, f"Время оказания услуги: {time_picked}",
                           reply_markup=time_slot_keyboard)


@dp.callback_query_handler(text=["time_slot:5"])
async def make_order(message: types.Message):
    time_slot_button = InlineKeyboardButton(text="Подтвердить", callback_data="time_picked")
    time_slot_back_button = InlineKeyboardButton(text="Выбрать другое время", callback_data="date_picked")
    time_slot_keyboard = InlineKeyboardMarkup().add(time_slot_button).add(time_slot_back_button)
    global time_picked
    time_picked = time_slot_list[5]
    global time_slot_index
    time_slot_index = 5
    await bot.send_message(message.from_user.id, f"Время оказания услуги: {time_picked}",
                           reply_markup=time_slot_keyboard)


@dp.callback_query_handler(text=["time_slot:6"])
async def make_order(message: types.Message):
    time_slot_button = InlineKeyboardButton(text="Подтвердить", callback_data="time_picked")
    time_slot_back_button = InlineKeyboardButton(text="Выбрать другое время", callback_data="date_picked")
    time_slot_keyboard = InlineKeyboardMarkup().add(time_slot_button).add(time_slot_back_button)
    global time_picked
    time_picked = time_slot_list[6]
    global time_slot_index
    time_slot_index = 6
    await bot.send_message(message.from_user.id, f"Время оказания услуги: {time_picked}",
                           reply_markup=time_slot_keyboard)


@dp.callback_query_handler(text=["time_slot:7"])
async def make_order(message: types.Message):
    time_slot_button = InlineKeyboardButton(text="Подтвердить", callback_data="time_picked")
    time_slot_back_button = InlineKeyboardButton(text="Выбрать другое время", callback_data="date_picked")
    time_slot_keyboard = InlineKeyboardMarkup().add(time_slot_button).add(time_slot_back_button)
    global time_picked
    time_picked = time_slot_list[7]
    global time_slot_index
    time_slot_index = 7
    await bot.send_message(message.from_user.id, f"Время оказания услуги: {time_picked}",
                           reply_markup=time_slot_keyboard)


@dp.callback_query_handler(text=["time_slot:8"])
async def make_order(message: types.Message):
    time_slot_button = InlineKeyboardButton(text="Подтвердить", callback_data="time_picked")
    time_slot_back_button = InlineKeyboardButton(text="Выбрать другое время", callback_data="date_picked")
    time_slot_keyboard = InlineKeyboardMarkup().add(time_slot_button).add(time_slot_back_button)
    global time_picked
    time_picked = time_slot_list[8]
    global time_slot_index
    time_slot_index = 8
    await bot.send_message(message.from_user.id, f"Время оказания услуги: {time_picked}",
                           reply_markup=time_slot_keyboard)


@dp.callback_query_handler(text=["time_slot:9"])
async def make_order(message: types.Message):
    time_slot_button = InlineKeyboardButton(text="Подтвердить", callback_data="time_picked")
    time_slot_back_button = InlineKeyboardButton(text="Выбрать другое время", callback_data="date_picked")
    time_slot_keyboard = InlineKeyboardMarkup().add(time_slot_button).add(time_slot_back_button)
    global time_picked
    time_picked = time_slot_list[9]
    global time_slot_index
    time_slot_index = 9
    await bot.send_message(message.from_user.id, f"Время оказания услуги: {time_picked}",
                           reply_markup=time_slot_keyboard)


# Now it is time to register or finalize the order

@dp.callback_query_handler(text=["time_picked"])
async def make_reservation(message: types.Message):
    loaded_db = db_methods.load_json(db_file_path)
    clients_table = loaded_db["items"][0]["items"]
    client = db_methods.search_client(clients_table, message.from_user.id)
    if client:
        await bot.send_message(message.from_user.id, f"Спасибо за заказ")
        data2 = remove_timeslot_load()
        time_slot_manager_save(data2)
        order_example = [
            f"{premise_name}",
            f"{service_name}",
            f"{service_price}",
            f"{specialist_name}",
            f"{day_picked}",
            f"{time_picked}"
        ]

        db_methods.add_client_order(loaded_db, order_example, message.from_user.id)
        db_methods.save_json(loaded_db, db_file_name)

        await bot.send_message(message.from_user.id, f"Спасибо за то, что выбрали нас")
        await bot.send_message(message.from_user.id, f"Вы записались на услугу: {service_name}")
        await bot.send_message(message.from_user.id,
                               f"Ваш мастер: {specialist_name}, будет ожидать Вас в салоне: {premise_name}")
        await bot.send_message(message.from_user.id, f"Дата: {day_picked}")
        await bot.send_message(message.from_user.id, f"Время: {time_picked}")
    else:
        await bot.send_message(message.from_user.id, f"Введите Ваше имя")
        await message.answer('...loading')
        await Register.first_name.set()


@dp.message_handler(state=Register.first_name)
async def get_first_name(message: types.Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    await bot.send_message(message.from_user.id, f"Введите Вашу фамилию")
    await Register.last_name.set()


@dp.message_handler(state=Register.last_name)
async def get_last_name(message: types.Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    await bot.send_message(message.from_user.id, f"Введите Ваш номер мобильного телефона")
    await Register.phonenumber.set()


@dp.message_handler(state=Register.phonenumber)
async def get_phone(message: types.Message, state: FSMContext):
    answer = message.text
    if answer:
        unparsed_number = answer
        parsed_number = phonenumbers.parse(unparsed_number, 'RU')
        if phonenumbers.is_possible_number(parsed_number) and phonenumbers.is_valid_number(parsed_number):
            valid_number = phonenumbers.format_number(parsed_number,
                                                      phonenumbers.PhoneNumberFormat.E164
                                                      )
            await state.update_data(phonenumber=valid_number)
            data = await state.get_data()
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            phonenumber = data.get('phonenumber')

            await message.answer(
                f'Отлично! Теперь Вы официально наш лучший клиент! Свяжемся с Вами в ближайшее время!')
            await bot.send_message(message.from_user.id, "Спасибо за заказ")

            client_data = [
                message.from_user.username,
                message.from_user.id,
                first_name,
                last_name,
                phonenumber
            ]
            db_methods.add_client(loaded_db, client_data)
            db_methods.save_json(loaded_db, db_file_name)

            data2 = remove_timeslot_load()
            time_slot_manager_save(data2)
            order_example = [
                f"{premise_name}",
                f"{service_name}",
                f"{service_price}",
                f"{specialist_name}",
                f"{day_picked}",
                f"{time_picked}"
            ]

            db_methods.add_client_order(loaded_db, order_example, message.from_user.id)
            db_methods.save_json(loaded_db, db_file_name)

            await bot.send_message(message.from_user.id, f"Спасибо за то, что выбрали нас")
            await bot.send_message(message.from_user.id, f"Вы записались на услугу: {service_name}")
            await bot.send_message(message.from_user.id,
                                   f"Ваш мастер: {specialist_name}, будет ожидать Вас в салоне: {premise_name}")
            await bot.send_message(message.from_user.id, f"Дата: {day_picked}")
            await bot.send_message(message.from_user.id, f"Время: {time_picked}")

        else:
            await message.answer('Введите корректный номер телефона.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
