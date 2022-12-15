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
        "created_at": client_created_at,
    }

    clients_table = db_structure["items"][0]["items"]

    if not search_client(clients_table, phone):
        clients_table.append(client_data)

    return db_structure


def search_client(clients: dict, phone: str) -> dict:
    found_client = None
    for client in clients:
        if phone in client.values():
            found_client = client

    return found_client


def add_client_order(
    service_db: dict, order_fields: list, client_phone: str
):
    clients = service_db["items"][0]["items"]
    clients_table = service_db["items"][0]
    clients_table.setdefault("last_order_id", 0)
    # last_order_id = clients_table["last_order_id"]
    now_date = datetime.datetime.now()
    order_created_at = now_date.strftime("%d.%m.%Y %H:%M:%S")
    found_client = search_client(clients, client_phone)

    (
        service_name,
        service_price,
        specialist,
        timeslot,
    ) = order_fields

    client_order = {
        "order_id": "",
        "service_name": service_name,
        "service_price": service_price,
        "specialist": specialist,
        "timeslot": timeslot,
        "order_status": "",
        "created_at": order_created_at,
        "competed_at": "",
    }

    filled_db = None

    if found_client:
        clients_table["last_order_id"] += 1
        # last_order_id += 1
        client_order["order_id"] = clients_table["last_order_id"]
        found_client["client_orders"].append(client_order)
        found_client.setdefault("last_client_order", {})
        found_client["last_client_order"] = client_order
        filled_db = service_db

    return filled_db


def main():
    env = Env()
    env.read_env()
    db_file_name = env.str("DB_FILE_NAME", "db.json")

    db_structure = {"items": []}
    db_file_path = Path(db_file_name)

    client_example = [
        "supernick",
        "1231231234",
        "Dima",
        "Ivanov",
        "+79154127022",
    ]

    order_example = [
        "Укладка",
        "900 RUR",
        "Мастер 32",
        "15:00",
    ]

    create_db(db_file_path, db_structure, db_file_name)
    loaded_db = load_json(db_file_path)

    add_client(loaded_db, client_example)

    save_json(loaded_db, db_file_name)

    clients_table = loaded_db["items"][0]["items"]
    print(search_client(clients_table, "+79515521901"))
    print(add_client_order(loaded_db, order_example, "+79154127022"))
    save_json(loaded_db, db_file_name)


if __name__ == "__main__":
    main()
