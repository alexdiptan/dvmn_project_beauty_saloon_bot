import logging
from pathlib import Path

import phonenumbers
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from environs import Env
from phonenumbers.phonenumberutil import NumberParseException

from registration import Register
import db_methods
import markups as navi

env = Env()
env.read_env()
tg_token = env.str("TG_BOT_TOKEN")
db_file_name = env.str("DB_FILE_NAME", "db.json")
db_file_path = Path(db_file_name)
loaded_db = db_methods.load_json(db_file_path)

premises_db_file_name = env.str("PREMISES_DB_FILE_NAME", "premises.json")
premises_db_file_path = Path(premises_db_file_name)
loaded_premises_db = db_methods.load_json(premises_db_file_path)

services_db_file_name = env.str("services_DB_FILE_NAME", "services.json")
services_db_file_path = Path(services_db_file_name)
loaded_services_db = db_methods.load_json(services_db_file_path)

logging.basicConfig(level=logging.INFO)
bot = Bot(token=tg_token)
dp = Dispatcher(bot, storage=MemoryStorage())


# --- Main Menu ---
## When /start or /help command received the bot would give 2 buttons: "Записаться на процедуру" & "Личный кабинет" (reply_markup = navi.main_menu)

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await bot.send_message(message.from_user.id, "Привет, {0.first_name}!\nЯ - бот BeautyCity, запишемся на процедуру?".format(message.from_user), reply_markup = navi.main_menu)


# --- Make Appointment ---
## When "Записаться на процедуру" is tapped the bot will display the list of available premises
### Geolocation suggestions might be added later here

premises = loaded_premises_db

@dp.message_handler()
async def bot_message(message: types.Message):
    """
    This handler will be called when user sends a message
    """
    if message.text == 'Записаться на процедуру':
        await bot.send_message(message.from_user.id, f"Какой салон Вам больше нравится?\n\n{premises['premises'][0]['premise_name']}: {premises['premises'][0]['premise_address']}\n\n{premises['premises'][1]['premise_name']}: {premises['premises'][1]['premise_address']}\n\n{premises['premises'][2]['premise_name']}: {premises['premises'][2]['premise_address']}\n\n{premises['premises'][3]['premise_name']}: {premises['premises'][3]['premise_address']}\n\n{premises['premises'][4]['premise_name']}: {premises['premises'][4]['premise_address']}\n\n{premises['premises'][5]['premise_name']}: {premises['premises'][5]['premise_address']}", reply_markup = navi.pick_premises_menu)


## When the salon is tapped the bot will display the list of available services
## --- Pick Premise ---

    elif message.text == 'Beauty Hair Lab Studio"':
        await bot.send_message(message.from_user.id, f"Вы выбрали {premises['premises'][0]['premise_name']} по адресу: {premises['premises'][0]['premise_address']}\n\nКакая услуга Вас интересует?", reply_markup = navi.pick_service_menu)

    elif message.text == 'Birdie':
        await bot.send_message(message.from_user.id, f"Вы выбрали {premises['premises'][1]['premise_name']} по адресу: {premises['premises'][1]['premise_address']}\n\nКакая услуга Вас интересует?", reply_markup = navi.pick_service_menu)

    elif message.text == 'Expat Salon':
        await bot.send_message(message.from_user.id, f"Вы выбрали {premises['premises'][2]['premise_name']} по адресу: {premises['premises'][2]['premise_address']}\n\nКакая услуга Вас интересует?", reply_markup = navi.pick_service_menu)

    elif message.text == 'Brush Beauty Salon':
        await bot.send_message(message.from_user.id, f"Вы выбрали {premises['premises'][3]['premise_name']} по адресу: {premises['premises'][3]['premise_address']}\n\nКакая услуга Вас интересует?", reply_markup = navi.pick_service_menu)

    elif message.text == 'Beauty Point':
        await bot.send_message(message.from_user.id, f"Вы выбрали {premises['premises'][4]['premise_name']} по адресу: {premises['premises'][4]['premise_address']}\n\nКакая услуга Вас интересует?", reply_markup = navi.pick_service_menu)

    elif message.text == 'Салон красоты IRIS, Войковская':
        await bot.send_message(message.from_user.id, f"Вы выбрали {premises['premises'][5]['premise_name']} по адресу: {premises['premises'][5]['premise_address']}\n\nКакая услуга Вас интересует?", reply_markup = navi.pick_service_menu)


premises = loaded_services_db
## --- Pick Service ---

    elif message.text == 'Вернуться к списку услуг':
        await bot.send_message(message.from_user.id, 'Возвращаемся к выбору услуг', reply_markup = navi.pick_service_menu)

    elif message.text == 'Макияж':
        await bot.send_message(message.from_user.id, 'Стоимость услуги Макияж: 3,500.00 USD', reply_markup = navi.return_or_pick_specialist)

    elif message.text == 'Парикмахерские услуги':
        await bot.send_message(message.from_user.id, 'Стоимость услуги Парикмахерские услуги: 500.00 USD', reply_markup = navi.return_or_pick_specialist)

    elif message.text == 'Косметология':
        await bot.send_message(message.from_user.id, 'Стоимость услуги Косметология: 750.00 USD', reply_markup = navi.return_or_pick_specialist)

    elif message.text == 'Тату и пирсинг':
        await bot.send_message(message.from_user.id, 'Стоимость услуги Тату и пирсинг: 1,750.00 USD', reply_markup = navi.return_or_pick_specialist)

    elif message.text == 'Брови':
        await bot.send_message(message.from_user.id, 'Стоимость услуги Брови: 5,750.00 USD', reply_markup = navi.return_or_pick_specialist)









@dp.message_handler(commands=['registration'])
async def make_reservation(message: types.Message):
    name = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='Отменить запись')
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer('Для записи на прием введите ваше имя',
                         reply_markup=name
                         )
    await Register.first_name.set()


@dp.message_handler(state=Register.first_name)
async def get_first_name(message: types.Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    last_name = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='Отменить запись')
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer('Введите вашу фамилию',
                         reply_markup=last_name
                         )
    await Register.last_name.set()


@dp.message_handler(state=Register.last_name)
async def get_last_name(message: types.Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    last_name = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='Отменить запись')
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer('Введите ваш номер мобильного телефона',
                         reply_markup=last_name
                         )
    await Register.phonenumber.set()


@dp.message_handler(state=Register.phonenumber)
async def get_phone(message: types.Message, state: FSMContext):
    answer = message.text
    try:
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
                await message.answer(f'Запись прошла успешно. Свяжемся в ближайшее время!')
                client_data = [
                    message.from_user.username,
                    message.from_user.id,
                    first_name,
                    last_name,
                    phonenumber
                ]
                db_methods.add_client(loaded_db, client_data)
                db_methods.save_json(loaded_db, db_file_name)
            else:
                await message.answer('Введите корректный номер телефона.')
    except NumberParseException:
        await message.answer('Введите корректный номер телефона.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)


#test test test