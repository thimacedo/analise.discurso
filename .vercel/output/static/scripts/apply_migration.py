import os
import sys
import psycopg2
from dotenv import load_dotenv

# Força UTF-8 no Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

# Tenta obter a string de conexão direta do PostgreSQL
# Supabase geralmente fornece uma URL como: postgres://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
DB_URL = os.getenv("DATABASE_URL") or os.getenv("DIRECT_URL")

def apply_sql_file(file_path, conn):
    print(f"📄 [MIGRATION] Aplicando arquivo: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    with conn.cursor() as cur:
        try:
            cur.execute(sql)
            conn.commit()
            print(f"✅ [MIGRATION] Sucesso: {file_path}")
        except Exception as e:
            conn.rollback()
            print(f"❌ [MIGRATION] Erro ao aplicar {file_path}: {e}")
            raise e

def main():
    if not DB_URL:
        print("❌ [MIGRATION] DATABASE_URL não encontrada no .env. Não é possível rodar SQL puro sem conexão direta.")
        sys.exit(1)

    try:
        print("🔌 [MIGRATION] Conectando ao banco de dados...")
        conn = psycopg2.connect(DB_URL)
        
        # 1. Criar a tabela base se não existir
        apply_sql_file(r".\scripts\create_anuncios_table.sql", conn)
        
        # 2. Aplicar a migração PASA v16.4
        apply_sql_file(r".\scripts\migration_v22.1_anuncios_pasa.sql", conn)
        
        conn.close()
        print("✨ [MIGRATION] Processo concluído com sucesso!")
        
    except Exception as e:
        print(f"💥 [MIGRATION] Falha crítica: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
