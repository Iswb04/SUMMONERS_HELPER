import sqlite3
from league_main import DB_FILE, TABLE_NAME

connection = sqlite3.connect(DB_FILE)
cursor = connection.cursor()


# ---------------------------------------------------------

"""cursor.execute(
    f'''SELECT * FROM {TABLE_NAME}
'''
)"""

"""cursor.execute(
    f'''SELECT NAME, RELEASE_DATE FROM {TABLE_NAME} 
    WHERE RELEASE_DATE LIKE '%2009%' 
''' 
)"""

"""cursor.execute(
    f'''SELECT NAME FROM {TABLE_NAME}
    WHERE NAME LIKE 'A%' COLLATE NOCASE 
'''
)"""

"""cursor.execute(
    f'''SELECT COUNT(*) AS total_2009 FROM {TABLE_NAME}
    WHERE RELEASE_DATE LIKE '%2009%' 
'''
)"""

"""cursor.execute(
    f''' SELECT NAME, TAGS FROM {TABLE_NAME}
    WHERE TAGS LIKE '%FIGHTER%' AND TAGS LIKE'%ASSASSIN%'
'''
)"""

"""cursor.execute(
    f'''SELECT NAME, TITLE FROM {TABLE_NAME}
    WHERE NAME LIKE 'd%' AND TITLE NOT LIKE 'a%'
'''
)"""

"""cursor.execute(f'''
    SELECT NAME, RELEASE_DATE
    FROM {TABLE_NAME}
    ORDER BY 
        CAST(substr(RELEASE_DATE, 7, 4) AS INTEGER) ASC,  -- ano
        CAST(substr(RELEASE_DATE, 4, 2) AS INTEGER) ASC,  -- mês
        CAST(substr(RELEASE_DATE, 1, 2) AS INTEGER) ASC   -- dia
''')
"""


cursor.execute(
    f'''SELECT NAME, COUNTERS FROM {TABLE_NAME}
    WHERE COUNTERS LIKE '%desconhecido%'
'''
)


"""cursor.execute( 
    f'''SELECT NAME, TAGS FROM {TABLE_NAME}
    WHERE NAME LIKE '%nautilus%'
'''
)"""




"""ALTER TABLE nome_da_tabela
DROP COLUMN advantages;"""

"""cursor.execute(
        f'''ALTER TABLE {TABLE_NAME}
        ADD COLUMN advantages TEXT; '''
)"""



# ---------------------------------------------------------


rows = cursor.fetchall() 
if not rows:
    print('Nenhum registro encontrado!')
else:
    for row in rows: # row = linha
        print(row)

cursor.close()
connection.close()