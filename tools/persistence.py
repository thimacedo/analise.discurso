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
        Garante que metadados (autor, post) e inteligência IA sejam salvos.
        """
        if not self.supabase:
            print("⚠️ [Persistence] Sem conexão com banco. Dados não persistidos.")
            return

        # Mapeamento de colunas do DataFrame para o Schema do Supabase (comentarios)
        # DF Col: 'id', 'owner_username', 'post_shortcode', 'is_hate_speech', 'category', 'confianca', 'cluster'
        # DB Col: 'id', 'autor_username', 'post_id',         'is_hate',         'categoria_ia', 'confianza_ia', 'cluster_id'
        
        mapping = {
            'owner_username': 'autor_username',
            'post_shortcode': 'post_id',
            'is_hate_speech': 'is_hate',
            'category': 'categoria_ia',
            'categoria_ia': 'categoria_ia', # Fallback
            'confianca': 'confianza_ia',
            'cluster': 'cluster_id'
        }

        records_updated = 0
        
        # Filtra apenas colunas que pretendemos atualizar (além do ID)
        df_update = df.copy()
        for df_col, db_col in mapping.items():
            if df_col in df_update.columns and df_col != db_col:
                df_update[db_col] = df_update[df_col]

        # Colunas finais para o payload do banco
        db_columns = ['id', 'autor_username', 'post_id', 'is_hate', 'categoria_ia', 'confianza_ia', 'processado_ia']
        
        for _, row in df_update.iterrows():
            comment_id = row.get('id')
            if not comment_id: continue

            # Prepara payload
            payload = {"processado_ia": True}
            for col in db_columns:
                if col in row and col != 'id':
                    val = row[col]
                    # Remove NaNs e nulos para o Postgres
                    if pd.notna(val):
                        payload[col] = val

            # Não tentar atualizar se só tiver processado_ia
            if len(payload) <= 1:
                continue

            try:
                self.supabase.table('comentarios').update(payload).eq('id', comment_id).execute()
                records_updated += 1
            except Exception as e:
                print(f"❌ [Persistence] Erro ao atualizar comentário {comment_id}: {e}")

        print(f"✅ [Persistence] {records_updated} comentários atualizados com inteligência PASA/Diamond no Supabase.")

if __name__ == "__main__":
    pm = PersistenceManager()
    print("Persistence Manager pronto.")
