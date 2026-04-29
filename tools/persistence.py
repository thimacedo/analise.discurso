# SENTINELA | Diamond Edition - Persistence Manager
# Gerencia a gravação de inteligência forense de volta no Supabase

import os
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class PersistenceManager:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            print("⚠️ [Persistence] Variáveis SUPABASE_URL/KEY não encontradas.")
            self.supabase = None
        else:
            self.supabase: Client = create_client(url, key)

    def update_forensic_data(self, df: pd.DataFrame):
        """
        Persiste os dados do PASA e Clusters no Supabase.
        Assume que o DataFrame possui a coluna 'comment_id' (ou 'id') e os campos de inteligência.
        """
        if self.supabase is None:
            return

        # Colunas de inteligência esperadas
        # 'is_hate_speech', 'category', 'confianca', 'cluster'
        
        # Mapeamento para o schema do Supabase (tabela comments)
        # Campos no DB: is_hate, categoria_ia, confianca, cluster_id
        
        records_updated = 0
        
        # Usamos iterrows para update individual (Supabase API REST via patch)
        for _, row in df.iterrows():
            comment_id = row.get('comment_id') or row.get('id')
            if not comment_id: continue

            # Prepara payload de inteligência
            payload = {
                "is_hate": bool(row.get('is_hate_speech', False)),
                "categoria_ia": row.get('category') or row.get('categoria_ia'),
                "processado_ia": True
            }
            
            if 'cluster' in row:
                payload["cluster_id"] = int(row['cluster'])
            
            # Limpa valores nulos
            payload = {k: v for k, v in payload.items() if v is not None and v == v}

            try:
                # Realiza o update no Supabase usando o comment_id como filtro
                # O ID no Supabase é a PRIMARY KEY
                self.supabase.table('comentarios').update(payload).eq('id', comment_id).execute()
                records_updated += 1
            except Exception as e:
                print(f"❌ [Persistence] Erro ao atualizar comentário {comment_id}: {e}")

        print(f"✅ [Persistence] {records_updated} comentários atualizados com inteligência PASA/Diamond.")

if __name__ == "__main__":
    # Teste rápido de carga
    print("Iniciando Persistence Manager...")
    pm = PersistenceManager()
    print("Pronto para persistência técnica.")
