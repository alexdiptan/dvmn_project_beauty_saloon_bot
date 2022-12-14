import datetime
import json
from pathlib import Path

from environs import Env


def create_db(db_file_path, db_structure, db_file_name) -> None:
    if not db_file_path.exists():
        create_table(db_structure, "client", 1)
        save_json(db_structure, db_file_name)


def load_json(file_name) -> dict:
    with open(file_name, "r", encoding="utf8") as file:
        file_data = json.load(file)

    return file_data


def save_json(db_structure: dict, json_file: str) -> None:
    with open(json_file, "w", encoding="utf-8") as file:
        json.dump(db_structure, file, ensure_ascii=False, indent=2)


def create_table(db_structure, table_name: str, table_foreign: int) -> dict:
    table_db_structure = {
        "table_name": table_name,
        "foreign": table_foreign,
        "items": [],
    }
    db_structure["items"].append(table_db_structure)

    return db_structure


def add_client(db_structure: dict, client_fields: list) -> dict:
    now_date = datetime.datetime.now()
    client_created_at = now_date.strftime("%d.%m.%Y %H:%M:%S")

    (
        tg_user_name,
        tg_user_id,
        first_name,
        last_name,
        phone,
    ) = client_fields

    client_data = {
        "tg_user_name": tg_user_name,
        "tg_user_id": tg_user_id,
        "first_name": first_name,
        "last_name": last_name,
        "phone": phone,
        "client_orders": [],
        "created_at": client_created_at,
    }

    clients_table = db_structure["items"][0]["items"]

    if not search_client(clients_table, tg_user_id):
        clients_table.append(client_data)

    return db_structure


def search_client(clients: dict, tg_user_id: int) -> dict:
    found_client = None
    for client in clients:
        if tg_user_id in client.values():
            found_client = client

    return found_client


def add_client_order(service_db: dict, order_fields: list, tg_user_id: int) -> dict:
    """
    Функция возвращает словарь с добавленным заказом
    :param service_db:
    :param order_fields:
    :param tg_user_id:
    :return: added order
    """
    clients = service_db["items"][0]["items"]
    clients_table = service_db["items"][0]
    clients_table.setdefault("last_order_id", 0)
    now_date = datetime.datetime.now()
    order_created_at = now_date.strftime("%d.%m.%Y %H:%M:%S")
    found_client = search_client(clients, tg_user_id)

    (
        premise_name,
        service_name,
        service_price,
        specialist,
        visit_date,
        timeslot,
    ) = order_fields

    client_order = {
        "order_id": "",
        "premise_name": premise_name,
        "service_name": service_name,
        "service_price": service_price,
        "specialist": specialist,
        "visit_date": visit_date,
        "timeslot": timeslot,
        "is_order_paid": False,
        "created_at": order_created_at,
        "paid_at": "",
    }

    if found_client:
        clients_table["last_order_id"] += 1
        client_order["order_id"] = clients_table["last_order_id"]
        found_client["client_orders"].append(client_order)
        found_client.setdefault("last_client_order", {})
        found_client["last_client_order"] = client_order

    return found_client["last_client_order"]


def last_client_order_pay_confirmation(loaded_db, from_client_id: int) -> dict:
    """
    После того как оплата совершена, нужно в ордере подставить is_order_paid = True и дату, время платежа
    в поле paid_at

    :param loaded_db:
    :param from_client_id:
    :return: confirmed order
    """
    now_date = datetime.datetime.now()
    paid_at = now_date.strftime("%d.%m.%Y %H:%M:%S")
    clients_table = loaded_db["items"][0]["items"]
    client = search_client(clients_table, from_client_id)

    client["last_client_order"]["is_order_paid"] = True
    client["last_client_order"]["paid_at"] = paid_at
    for client_order in client["client_orders"]:
        if client_order["order_id"] == client["last_client_order"]["order_id"]:
            client_order["is_order_paid"] = True
            client_order["paid_at"] = paid_at

    return client["last_client_order"]


def main():
    env = Env()
    env.read_env()
    db_file_name = env.str("DB_FILE_NAME", "db.json")

    db_structure = {"items": []}
    db_file_path = Path(db_file_name)

    client_example = [
        "zero_man",
        75675231234,
        "Igor",
        "Sheremrtiev",
        "+79114210967",
    ]

    order_example = [
        "Салон на Тверской",
        "Тату",
        450,
        "Мастер 7",
        "19.12.2022",
        "11:00",
    ]

    create_db(db_file_path, db_structure, db_file_name)
    loaded_db = load_json(db_file_path)

    add_client(loaded_db, client_example)

    save_json(loaded_db, db_file_name)

    clients_table = loaded_db["items"][0]["items"]

    last_client_order = add_client_order(loaded_db, order_example, 384973490)
    print(f"{last_client_order=}")

    save_json(loaded_db, db_file_name)
    client = search_client(clients_table, 3849734901)

    if client is not None:
        for client_order in client["client_orders"]:
            print(client_order)


if __name__ == "__main__":
    main()
