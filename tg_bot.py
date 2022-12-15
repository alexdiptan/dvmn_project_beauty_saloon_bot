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

env = Env()
env.read_env()
tg_token = env.str("TG_BOT_TOKEN")
db_file_name = env.str("DB_FILE_NAME", "db.json")
db_file_path = Path(db_file_name)
loaded_db = db_methods.load_json(db_file_path)

logging.basicConfig(level=logging.INFO)
bot = Bot(token=tg_token)
dp = Dispatcher(bot, storage=MemoryStorage())


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
