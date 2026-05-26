
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

    # REMOVE A TABELA ANTIGA PARA GARANTIR QUE O NOVO FORMATO SEJA APLICADO
    print("[INFO] Resetando banco de dados...")
    cursor.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")

    cursor.execute(f'''
        CREATE TABLE {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            title TEXT,
            tags TEXT,
            counters TEXT,
            advantages TEXT,
            image_full TEXT,
            blurb TEXT
        )               
    ''')
    connection.commit()

    print(f"[INFO] Buscando dados da Riot (v15.9.1)...")
    get_url = requests.get(URL)
    get_url.raise_for_status()
    champions = get_url.json()['data']

    try:
        local_counters = requests.get(COUNTER_URL).json() # dicionario da api local
        local_advantages = requests.get(ADVANTAGE_URL).json() # dicionario da api local
    except requests.exceptions.ConnectionError:
        print("\n[ERRO] Não foi possível conectar à API local (http://127.0.0.1:8000).")
        print("Certifique-se de que o servidor está rodando com: uvicorn API_main:app --reload")
        connection.close()
        exit(1)

    for champ_info in champions.values():
        name = champ_info["name"]
        title = champ_info.get("title", "")
        tags = ", ".join(champ_info.get("tags", []))
        counters = ", ".join(local_counters.get(name, ["Desconhecido"]))
        advantages = ", ".join(local_advantages.get(name, ["Desconhecido"]))
        
        image_full = champ_info["image"]["full"]
        blurb = champ_info.get("blurb", "")


        cursor.execute(
            f"INSERT INTO {TABLE_NAME} (name, title, tags, counters, advantages, image_full, blurb) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, title, tags, counters, advantages, image_full, blurb)
        )

    connection.commit()
    cursor.close()
    connection.close()


