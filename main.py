from pathlib import Path

from environs import Env

import db_methods


def main():
    env = Env()
    env.read_env()
    db_file_name = env.str("DB_FILE_NAME", "db.json")

    db_structure = {"items": []}
    db_file_path = Path(db_file_name)
    print(db_file_path)

    client_example = [
        "supernick",
        "1231231234",
        "Dima",
        "Ivanov",
        "+79154127022",
    ]

    db_methods.create_db(db_file_path, db_structure, db_file_name)
    loaded_db = db_methods.load_json(db_file_path)

    db_methods.add_client(loaded_db, client_example)

    db_methods.save_json(loaded_db, db_file_name)

    clients_table = loaded_db["items"][0]["items"]
    print(db_methods.search_client(clients_table, "+79515521906"))


if __name__ == "__main__":
    main()
