"""
PASA v48.1 - Migration Runner: Aplica as columns faltantes diretamente no Postgres
Usa a URI direta para bypassar o RPC do Supabase Studio.
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Pega a URI do .env ou usa a padrão
DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@db.vhamejkldzxbeibqeqpk.supabase.co:5432/postgres")

MIGRATIONS = [
    "ALTER TABLE public.comentarios ADD COLUMN IF NOT EXISTS needs_review BOOLEAN DEFAULT FALSE;",
    "ALTER TABLE public.comentarios ADD COLUMN IF NOT EXISTS audit_discrepancy BOOLEAN DEFAULT FALSE;",
    "ALTER TABLE public.comentarios ADD COLUMN IF NOT EXISTS ccf_density FLOAT DEFAULT 0.0;",
    "ALTER TABLE public.comentarios ADD COLUMN IF NOT EXISTS ccf_sync FLOAT DEFAULT 0.0;",
    "ALTER TABLE public.comentarios ADD COLUMN IF NOT EXISTS ccf_performativity FLOAT DEFAULT 0.0;",
    "ALTER TABLE public.comentarios ADD COLUMN IF NOT EXISTS tipo_conteudo VARCHAR(20) DEFAULT 'POST';",
    "ALTER TABLE public.candidatos ADD COLUMN IF NOT EXISTS shadowban_suspect BOOLEAN DEFAULT FALSE;",
    "ALTER TABLE public.candidatos ADD COLUMN IF NOT EXISTS shadowban_detected_at TIMESTAMPTZ;",
    "ALTER TABLE public.comentarios ADD COLUMN IF NOT EXISTS reels_scraped BOOLEAN DEFAULT FALSE;"
]

def run_migrations():
    print("[MigrationRunner] Conectando ao Postgres...")
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()
        
        print("[MigrationRunner] Executando migrations...")
        for sql in MIGRATIONS:
            cur.execute(sql)
            print(f"  -> OK: {sql[:50]}...")
        
        conn.commit()
        cur.close()
        conn.close()
        print("[MigrationRunner] Todas as migrations aplicadas com sucesso.")
    except Exception as e:
        print(f"[MigrationRunner] Erro ao conectar ou executar: {e}")
        print("Verifique se a DATABASE_URL está configurada no arquivo .env.")

if __name__ == "__main__":
    run_migrations()
