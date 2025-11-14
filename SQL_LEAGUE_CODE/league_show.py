import sqlite3
from league_main import DB_FILE, TABLE_NAME

connection = sqlite3.connect(DB_FILE)
cursor = connection.cursor()

cursor.execute(f'SELECT * FROM {TABLE_NAME}') 


rows = cursor.fetchall() 
if not rows:
    print('Nenhum registro encontrado!')
else:
    for row in rows: # row = linha
        print(row)


cursor.close()

connection.close()