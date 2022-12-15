from aiogram.dispatcher.filters.state import StatesGroup, State


class Register(StatesGroup):
    first_name = State()
    last_name = State()
    phonenumber = State()
