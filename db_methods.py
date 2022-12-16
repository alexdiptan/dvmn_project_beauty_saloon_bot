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
    date_time = now_date.strftime("%d.%m.%Y %H:%M:%S")

    (
        tg_user_name,
        tg_chat_id,
        first_name,
        last_name,
        phone,
    ) = client_fields

    client_data = {
        "tg_user_name": tg_user_name,
        "tg_chat_id": tg_chat_id,
        "first_name": first_name,
        "last_name": last_name,
        "phone": phone,
        "client_orders": [],
        "created_at": date_time,
    }

    clients_table = db_structure["items"][0]["items"]

    if not search_client(clients_table, phone):
        clients_table.append(client_data)

    return db_structure


def search_client(clients: dict, phone):
    found_client = None
    for client in clients:
        if phone in client.values():
            found_client = client

    return found_client

# Added search client orders, please check
def search_client_order(orders: dict, order_id):
        found_order = None
    for order in orders:
        if order_id in orders.values():
            found_order = order

    return found_order


def add_client_order(db_structure: dict, order_fields: list) -> dict:
    now_date = datetime.datetime.now()
    date_time = now_date.strftime("%d.%m.%Y %H:%M:%S")

    (
        tg_user_name,
        tg_chat_id,
        first_name,
        last_name,
        phone,
        premise_name,
        service_name,
        service_scheduled_date,
        service_scheduled_time,
        order_id,
    ) = order_fields

    order_data = {
        "tg_user_name": tg_user_name,
        "tg_chat_id": tg_chat_id,
        "first_name": first_name,
        "last_name": last_name,
        "phone": phone,
        "created_at": date_time,
        "premise_name": premise_name,
        "service_name": service_name,
        "service_scheduled_date": service_scheduled_date,
        "service_scheduled_time": service_scheduled_time,
        "order_id" = order_id,
    }

    orders_table = db_structure["items"][0]["items"]

    if not search_client_order(orders_table, order_id):
        orders_table.append(order_data)

    return db_structure


def main():
    env = Env()
    env.read_env()
    db_file_name = env.str("DB_FILE_NAME", "db.json")

    db_structure = {"items": []}
    db_file_path = Path(db_file_name)

    example_clients = [
        [
            "supernick",
            "1231231234",
            "Dima",
            "Ivanov",
            "+79154127022",
        ],
        [
            "zaza",
            "31365464567",
            "Sveta",
            "Zhukova",
            "+79515521906",
        ],
    ]

    create_db(db_file_path, db_structure, db_file_name)
    loaded_db = load_json(db_file_path)

    for example_client in example_clients:
        add_client(loaded_db, example_client)

    save_json(loaded_db, db_file_name)

    clients_table = loaded_db["items"][0]["items"]
    print(search_client(clients_table, '+79515521906'))


if __name__ == "__main__":
    main()
