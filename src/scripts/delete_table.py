import os

import oracledb
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DSN = os.getenv("DB_DSN")

DELETE_TABLE_SQL = "DROP TABLE soil_data"


def delete_table():
    with oracledb.connect(user=DB_USER, password=DB_PASSWORD, dsn=DB_DSN) as connection:
        with connection.cursor() as cursor:
            cursor.execute(DELETE_TABLE_SQL)
            print("Tabela 'soil_data' removida com sucesso.")
        connection.commit()


if __name__ == "__main__":
    delete_table()
