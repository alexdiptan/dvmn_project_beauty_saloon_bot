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

services_db_file_name = env.str("SERVICES_DB_FILE_NAME", "services.json")
services_db_file_path = Path(services_db_file_name)
loaded_services_db = db_methods.load_json(services_db_file_path)

specialists_db_file_name = env.str("SPECIALISTS_DB_FILE_NAME", "specialists.json")
specialists_db_file_path = Path(specialists_db_file_name)
loaded_specialists_db = db_methods.load_json(specialists_db_file_path)

logging.basicConfig(level=logging.INFO)
bot = Bot(token=tg_token)
dp = Dispatcher(bot, storage=MemoryStorage())


# --- Order Counter ---

order_id = 0

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

@dp.message_handler()
async def make_order(message: types.Message):
    """
    This handler will be called when user sends a message
    """
    premises = loaded_premises_db
    if message.text == 'Записаться на процедуру':
        await bot.send_message(message.from_user.id, f"Какой салон Вам больше нравится?\n\n{premises['premises'][0]['premise_name']}: {premises['premises'][0]['premise_address']}\n\n{premises['premises'][1]['premise_name']}: {premises['premises'][1]['premise_address']}\n\n{premises['premises'][2]['premise_name']}: {premises['premises'][2]['premise_address']}\n\n{premises['premises'][3]['premise_name']}: {premises['premises'][3]['premise_address']}\n\n{premises['premises'][4]['premise_name']}: {premises['premises'][4]['premise_address']}\n\n{premises['premises'][5]['premise_name']}: {premises['premises'][5]['premise_address']}", reply_markup = navi.pick_premises_menu)

## When the appointment is tapped the bot will display the list of available premises
## --- Pick Premise ---

    if message.text == 'Beauty Hair Lab Studio':
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

    elif message.text in ['Beauty Hair Lab Studio', 'Birdie', 'Expat Salon', 'Brush Beauty Salon', 'Beauty Point', 'Салон красоты IRIS, Войковская']:
        premise_name = message.text


## When the salon is tapped the bot will display the list of available services
## --- Pick Service ---

    services = loaded_services_db

    if message.text == 'Вернуться к списку услуг':
        await bot.send_message(message.from_user.id, 'Возвращаемся к выбору услуг', reply_markup = navi.pick_service_menu)
        
    elif message.text == 'Макияж':
        service_price = services['services'][0]['Макияж'][0]['service_price']
        await bot.send_message(message.from_user.id, f'Стоимость услуги Макияж: {service_price} RUB', reply_markup = navi.return_or_pick_specialist)

    elif message.text == 'Тату и Пирсинг':
        service_price = services['services'][1]['Тату и Пирсинг'][0]['service_price']
        await bot.send_message(message.from_user.id, f'Стоимость услуги Тату и Пирсинг: {service_price} RUB', reply_markup = navi.return_or_pick_specialist)

    elif message.text == 'Стрижка':
        service_price = services['services'][2]['Стрижка'][0]['service_price']
        await bot.send_message(message.from_user.id, f'Стоимость услуги Стрижка: {service_price} RUB', reply_markup = navi.return_or_pick_specialist)

    elif message.text == 'Косметология':
        service_price = services['services'][3]['Косметология'][0]['service_price']
        await bot.send_message(message.from_user.id, f'Стоимость услуги Косметология: {service_price} RUB', reply_markup = navi.return_or_pick_specialist)

    elif message.text == 'Брови':
        service_price = services['services'][4]['Брови'][0]['service_price']
        await bot.send_message(message.from_user.id, f'Стоимость услуги Брови: {service_price} RUB', reply_markup = navi.return_or_pick_specialist)

    elif message.text == 'Маникюр':
        service_price = services['services'][5]['Маникюр'][0]['service_price']
        await bot.send_message(message.from_user.id, f'Стоимость услуги Маникюр: {service_price} RUB', reply_markup = navi.return_or_pick_specialist)

    elif message.text == 'Педикюр':
        service_price = services['services'][6]['Педикюр'][0]['service_price']
        await bot.send_message(message.from_user.id, f'Стоимость услуги Педикюр: {service_price} RUB', reply_markup = navi.return_or_pick_specialist)

    elif message.text == 'Укладка':
        service_price = services['services'][7]['Укладка'][0]['service_price']
        await bot.send_message(message.from_user.id, f'Стоимость услуги Укладка: {service_price} RUB', reply_markup = navi.return_or_pick_specialist)

    elif message.text == 'Шугаринг':
        service_price = services['services'][8]['Шугаринг'][0]['service_price']
        await bot.send_message(message.from_user.id, f'Стоимость услуги Шугаринг: {service_price} RUB', reply_markup = navi.return_or_pick_specialist)

    elif message.text == 'Покраска':
        service_price = services['services'][9]['Покраска'][0]['service_price']
        await bot.send_message(message.from_user.id, f'Стоимость услуги Покраска: {service_price} RUB', reply_markup = navi.return_or_pick_specialist)

    elif message.text in ['Макияж', 'Тату и Пирсинг', 'Стрижка', 'Косметология', 'Брови', 'Маникюр', 'Педикюр', 'Укладка', 'Шугаринг', 'Покраска']:
        service_name = message.text


## When the service is tapped the bot will display the list of available specialists
## --- Pick Specialist ---

    specialists = loaded_specialists_db

    if message.text == 'Выбрать мастера':
        await bot.send_message(message.from_user.id, 'Какого мастера Вы предпочитаете?', reply_markup = navi.pick_specialist_menu)


    elif message.text in [
        'Brad Pitt', 'Sir Alex Ferguson', 'Mike Myers', 'Leatherface', 'Ilya Osipov', 'Leo Messi', 'Arnold Schwarzenegger', 'Wednesday',
        'Witcher', 'Charlize Theron', 'Jen Aniston', 'Rachel McAdams', 'Benedict Cumberbatch', 'Nathalie Emmanuel', 'Ewan McGregor',
        ]:
        await bot.send_message(message.from_user.id, 'На какую дату Вас записать к мастеру?', reply_markup = navi.pick_date_menu)
        specialist = message.text


## When the specialist is tapped the bot will display the list of available dates
## --- Pick Specialist ---

    elif message.text in [
        '16 декабря, 2022', '17 декабря, 2022', '18 декабря, 2022', '19 декабря, 2022', '20 декабря, 2022',
        ]:
        await bot.send_message(message.from_user.id, 'На какое время Вас записать к мастеру?', reply_markup = navi.pick_time_menu)


    elif message.text in [
        '10-00', '11-00', '12-00', '13-00', '14-00', '15-00', '16-00', '17-00', '18-00', '19-00'
        ]:
        await bot.send_message(message.from_user.id, 'Запись сделана, подтвердите, пожалуйста, регистрацию', reply_markup = navi.registration_menu)



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