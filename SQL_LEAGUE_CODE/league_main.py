
import requests
import sqlite3
from pathlib import Path


ROOT_DIR = Path(__file__).parent
DB_NAME = 'db.sqleague'
DB_FILE = ROOT_DIR / DB_NAME
TABLE_NAME = 'Champions'



URL = "https://ddragon.leagueoflegends.com/cdn/15.9.1/data/pt_BR/champion.json"
COUNTER_URL = "http://127.0.0.1:8000/counters"
ADVANTAGE_URL = "http://127.0.0.1:8000/advantages"


if __name__ == '__main__':
    connection = sqlite3.connect(DB_FILE)
    cursor = connection.cursor()

    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            title TEXT,
            tags TEXT,
            counters TEXT,
            advantages TEXT
        )               
    ''')
    connection.commit()


    get_url = requests.get(URL)
    get_url.raise_for_status()
    champions = get_url.json()['data']

    local_counters = requests.get(COUNTER_URL).json() # dicionario da api local
    local_advantages = requests.get(ADVANTAGE_URL).json() # dicionario da api local

    for champ_info in champions.values():
        name = champ_info["name"]
        title = champ_info.get("title", "")
        tags = ", ".join(champ_info.get("tags", []))
        counters = ", ".join(local_counters.get(name, ["Desconhecido"]))
        advantages = ", ".join(local_advantages.get(name, ["Desconhecido"]))


        cursor.execute(
            f"INSERT INTO {TABLE_NAME} (name, title, tags, counters, advantages) VALUES (?, ?, ?, ?, ?)",
            (name, title, tags, counters, advantages)
        )

    connection.commit()
    cursor.close()
    connection.close()


