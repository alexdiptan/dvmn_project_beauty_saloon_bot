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
    table_db_structure = {"table_name": table_name, "foreign": table_foreign, "items": []}
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
        created_at,
        updated_at,
        removed_at,
    ) = client_fields

    client_data = {
        "tg_user_name": tg_user_name,
        "tg_chat_id": tg_chat_id,
        "first_name": first_name,
        "last_name": last_name,
        "phone": phone,
        "client_orders": [],
        "created_at": date_time,
        "updated_at": updated_at,
        "removed_at": removed_at,
    }

    clients = db_structure["items"][0]["items"]
    f_cl = search_client(clients, phone)

    if not f_cl:
        clients.append(client_data)

    return db_structure


def search_client(clients: dict, phone):
    found_client = None
    for client in clients:
        if phone in client.values():
            found_client = client

    return found_client


def search_client_order():
    pass


def add_client_order():
    pass


def main():
    env = Env()
    env.read_env()
    db_file_name = env.str("DB_FILE_NAME", "db.json")

    db_structure = {"items": []}
    db_file_path = Path(db_file_name)

    test_client_fields = [
        "supernick",
        "1231231234",
        "Dima",
        "Ivanov",
        "+79154127022",
        "",
        "",
        "",
    ]

    create_db(db_file_path, db_structure, db_file_name)
    loaded_db = load_json(db_file_path)
    save_json(add_client(loaded_db, test_client_fields), db_file_name)


if __name__ == "__main__":
    main()
