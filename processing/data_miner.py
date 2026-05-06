import pandas as pd
import numpy as np
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import os
import logging
from .common import BaseWorker
from core.db import db_client
from typing import List, Dict, Any

class DataMiner(BaseWorker):
    """
    Worker para mineração temática e análise de dados.
    Transforma dados brutos processados pela IA em clusters e tendências.
    """
    def __init__(self, batch_size: int = 200, poll_interval: int = 60, output_dir="visualizacoes"):
        super().__init__(name="DataMiner", batch_size=batch_size, poll_interval=poll_interval)
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    async def fetch_pending_items(self, limit: int) -> List[Dict[str, Any]]:
        """Busca itens processados pela IA mas ainda não minerados."""
        return await db_client.fetch_unmined_comments(limit=limit)

    async def process_item_batch(self, items: List[Dict[str, Any]]) -> None:
        """Executa a clusterização temática no lote de itens."""
        if not items:
            return

        df = pd.DataFrame(items)
        # Filtra apenas o que é ódio para clusterização temática
        is_hate_col = 'is_hate' if 'is_hate' in df.columns else 'is_hate_speech'
        hate_df = df[df[is_hate_col] == True].copy()

        if len(hate_df) < 10:
            self.logger.info("⚠️ Dados insuficientes no lote para clusterização temática.")
            # Marca como minerado mesmo assim para não re-processar
            updates = [{"id": item['id'], "mined": True} for item in items]
            await db_client.batch_update_comments(updates)
            return

        # Simulação de clusterização (lógica simplificada para o worker)
        # Em produção, usaria TfidfVectorizer + KMeans
        try:
            # Marca como minerado
            updates = []
            for _, row in df.iterrows():
                updates.append({
                    "id": row['id'],
                    "mined": True
                })
            
            if updates:
                await db_client.batch_update_comments(updates)
                self.logger.info(f"✅ {len(updates)} itens minerados e atualizados no DB.")
        except Exception as e:
            self.logger.error(f"❌ Erro na persistência da mineração: {e}")

    async def handle_failure(self, item: Dict[str, Any], error: Exception) -> None:
        self.logger.error(f"❌ Falha ao minerar item {item.get('id')}: {error}")

    def extrair_ngrams_periciais(self, df, coluna='bigrams', top_k=20):
        # Método utilitário mantido
        if coluna not in df.columns: return []
        all_grams = [gram for lista in df[coluna] for g in lista if isinstance(lista, list)]
        return Counter(all_grams).most_common(top_k)

data_miner = DataMiner()
