import datetime
import json
from pathlib import Path

from environs import Env


def load_json(file_name):
    with open(file_name, "r", encoding="utf8") as file:
        file_data = json.load(file)

    return file_data


def save_json(db_structure: dict, json_file: str) -> None:
    with open(json_file, "w", encoding="utf-8") as file:
        json.dump(db_structure, file, ensure_ascii=False, indent=2)


def create_table(db_structure, table_name: str, table_foreign: int):
    table_db_structure = {"table_name": table_name, "foreign": table_foreign, "items": []}
    db_structure["items"].append(table_db_structure)

    return db_structure


def add_client(db_structure: dict, client_fields: list):
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
    if len(clients) == 0:
        clients.append(client_data)

    for client in clients:
        if tg_user_name not in client.values():
            clients.append(client_data)

    return db_structure


def main():
    env = Env()
    env.read_env()
    db_file_name = env.str("DB_FILE_NAME", "")

    db_structure = {"items": []}
    db_file_path = Path(db_file_name)

    client_fields = [
        "alexdiptan",
        "1231231234",
        "Alex",
        "Diptan",
        "+79134127021",
        "",
        "",
        "",
    ]

    if not db_file_path.exists():
        create_table(db_structure, "client", 1)
        save_json(db_structure, db_file_name)

    loaded_db = load_json(db_file_path)
    save_json(add_client(loaded_db, client_fields), db_file_name)


if __name__ == "__main__":
    main()
