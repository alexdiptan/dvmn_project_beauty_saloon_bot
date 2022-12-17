from pathlib import Path

from aiogram import Bot
from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.types.message import ContentTypes
from aiogram.utils import executor
from environs import Env

import db_methods

env = Env()
env.read_env()
tg_token = env.str("TG_BOT_TOKEN_TEST")
db_file_name = env.str("DB_FILE_NAME", "db.json")
db_file_path = Path(db_file_name)
loaded_db = db_methods.load_json(db_file_path)

payments_token = env.str("PAYMENTS_PROVIDER_TOKEN")

bot = Bot(tg_token)
dp = Dispatcher(bot)

client_order = {
    "order_id": 11,
    "premise_name": "Салон на Тверской",
    "service_name": "Тату",
    "service_price": 450,
    "specialist": "Мастер 7",
    "visit_date": "19.12.2022",
    "timeslot": "11:00",
    "is_order_paid": False,
    "created_at": "17.12.2022 21:53:41",
    "competed_at": "",
}

prices = [
    types.LabeledPrice(
        label=client_order["service_name"], amount=client_order["service_price"] * 100
    )
]


@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    await message.answer("Для оплаты введите /pay")


@dp.message_handler(commands=["pay"])
async def cmd_buy(message: types.Message):
    await bot.send_message(
        message.chat.id,
        f"Ваш заказ №{client_order['order_id']}: \n"
        f"Услуга: {client_order['service_name']}\n"
        f"Салон: {client_order['premise_name']}\n"
        f"Ваш мастер: {client_order['specialist']}\n"
        f"Дата и время услуги: {client_order['visit_date']} {client_order['timeslot']}\n"
        f"Сумма услуги: {client_order['service_price']}₽",
        parse_mode="Markdown",
    )
    await bot.send_invoice(
        message.chat.id,
        title=f'{client_order["service_name"]}',
        description=f"После оплаты вам будет доступен чек!",
        provider_token=payments_token,
        currency="rub",
        is_flexible=False,  # True If you need to set up Shipping Fee
        prices=prices,
        start_parameter="service_payment",
        payload="order payment",
    )


@dp.pre_checkout_query_handler(lambda query: True)
async def checkout(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(
        pre_checkout_query.id,
        ok=True,
        error_message="Aliens tried to steal your card's CVV,"
        " but we successfully protected your credentials,"
        " try to pay again in a few minutes, we need a small rest.",
    )


@dp.message_handler(content_types=ContentTypes.SUCCESSFUL_PAYMENT)
async def got_payment(message: types.Message):
    # Оплата прошла успешно. Проставляем в БД is_order_paid = True
    clients_table = loaded_db["items"][0]["items"]
    client = db_methods.search_client(clients_table, message.from_user.id)
    client["last_client_order"]["is_order_paid"] = True
    for processed_order in client["client_orders"]:
        if processed_order["order_id"] == client_order["order_id"]:
            processed_order["is_order_paid"] = True
    db_methods.save_json(loaded_db, db_file_name)

    await bot.send_message(
        message.chat.id,
        f"Вы успешно оплатили услугу на сумму: {message.successful_payment.total_amount / 100} "
        f"{message.successful_payment.currency}\n"
        f"Спасибо что вы с нами!",
        parse_mode="Markdown",
    )


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
