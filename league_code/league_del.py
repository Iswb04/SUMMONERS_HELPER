import sqlite3
from league_main import DB_FILE, TABLE_NAME

connection = sqlite3.connect(DB_FILE)
cursor = connection.cursor()


cursor.execute(
    f'DELETE FROM sqlite_sequence WHERE name="{TABLE_NAME}"' # reiniciar o autoincrement
)
connection.commit()
#
cursor.execute(
    f'DELETE FROM {TABLE_NAME}' # deletar a tebela toda
)
connection.commit()


cursor.close()
connection.close()
