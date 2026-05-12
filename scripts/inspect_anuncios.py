
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
# -*- coding: utf-8 -*-
import os
import sys
from core.db import db_client

def main():
    try:
        # Pega o primeiro registro para ver as chaves (colunas)
        res = db_client.client.table('anuncios').select('*').limit(1).execute()
        if res.data:
            print("COLUNAS ENCONTRADAS:")
            for key in res.data[0].keys():
                print(f"- {key}")
        else:
            print("Nenhum dado encontrado na tabela 'anuncios'.")
    except Exception as e:
        print(f"ERRO AO INSPECIONAR TABELA: {e}")

if __name__ == '__main__':
    main()
