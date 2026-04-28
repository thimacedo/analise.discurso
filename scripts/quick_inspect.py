import sqlite3
import os

DB_PATH = "E:/projetos/sentinela-democratica/data/odio_politica.db"

def inspect():
    if not os.path.exists(DB_PATH):
        print("Banco não encontrado.")
        return
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT texto_bruto, categoria_ia, analise_pericial, data_processamento FROM comentarios WHERE processado_ia = 1 ORDER BY data_processamento DESC LIMIT 3")
    rows = c.fetchall()
    
    print(f"Total processados encontrados: {len(rows)}")
    for r in rows:
        print("\n" + "="*40)
        print(f"TEXTO: {r[0]}")
        print(f"CATEGORIA: {r[1]}")
        print(f"PERITAGEM: {r[2]}")
        print(f"DATA: {r[3]}")
    conn.close()

if __name__ == '__main__':
    inspect()
