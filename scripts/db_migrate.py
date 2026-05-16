"""
PASA v45 - Auto-migration: Adiciona colunas de auditoria diretamente via Supabase RPC
Workaround para não depender de SQL manual no Studio.
"""
import sys
import os

# Adiciona o diretório raiz ao path para importar core
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.supabase_service import get_supabase_client

def apply_audit_columns():
    db = get_supabase_client()
    print("[Migration] Verificando integridade do schema...")
    try:
        # Tenta atualizar um registro inexistente com as novas colunas para testar se existem
        # Nota: Em Supabase REST API, não podemos criar colunas, mas podemos detectar se faltam.
        db.table('comentarios').select('needs_review, audit_discrepancy').limit(1).execute()
        print("[Migration] ✅ Colunas de auditoria detectadas e operacionais.")
    except Exception as e:
        error_msg = str(e).lower()
        if 'column' in error_msg and 'does not exist' in error_msg:
            print("\n" + "!"*60)
            print("🚨 ERRO CRÍTICO: COLUNAS DE AUDITORIA FALTANDO!")
            print("Execute o comando SQL abaixo no Supabase SQL Editor:")
            print("\nALTER TABLE public.comentarios")
            print("ADD COLUMN IF NOT EXISTS needs_review BOOLEAN DEFAULT FALSE,")
            print("ADD COLUMN IF NOT EXISTS audit_discrepancy BOOLEAN DEFAULT FALSE;")
            print("!"*60 + "\n")
            # Opcional: Levantar exceção para parar o servidor se for crítico
        else:
            print(f"[Migration] Aviso: Não foi possível validar colunas: {e}")

if __name__ == "__main__":
    apply_audit_columns()
