import sqlite3
import os

def inspect_db():
    db_file = "odio_politica.db"
    if os.path.exists(db_file):
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tabelas encontradas: {[t[0] for t in tables]}")
        
        for table in [t[0] for t in tables]:
            cursor.execute(f"PRAGMA table_info({table});")
            columns = cursor.fetchall()
            print(f"Colunas em {table}: {[c[1] for c in columns]}")
        conn.close()
    else:
        print("Banco de dados não encontrado.")

if __name__ == "__main__":
    inspect_db()
