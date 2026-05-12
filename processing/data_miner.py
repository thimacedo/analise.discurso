
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
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

        # Garante que a coluna de ódio existe e é booleana
        if is_hate_col not in df.columns:
            df[is_hate_col] = False
        else:
            df[is_hate_col] = df[is_hate_col].fillna(False).astype(bool)

        hate_df = df[df[is_hate_col] == True].copy()

        if len(hate_df) < 5:
            self.logger.info("⚠️ Dados insuficientes no lote para clusterização temática real. Marcando apenas como minerados.")
            updates = [{"id": item['id'], "mined": True} for item in items]
            await db_client.batch_update_comments(updates)
            return

        try:
            # Mineração Real: TF-IDF + KMeans
            # Usamos o 'texto_limpo' se disponível, caso contrário 'text'
            text_col = 'texto_limpo' if 'texto_limpo' in hate_df.columns else 'text'
            textos = hate_df[text_col].fillna('').astype(str)

            if textos.str.strip().replace('', np.nan).dropna().empty:
                self.logger.warning("⚠️ Textos vazios no lote de ódio. Pulando clusterização.")
                updates = [{"id": item['id'], "mined": True} for item in items]
                await db_client.batch_update_comments(updates)
                return

            vectorizer = TfidfVectorizer(max_features=100, stop_words=None) # Stopwords já tratadas no TextProcessor
            X = vectorizer.fit_transform(textos)

            # Define clusters (mínimo 2, máximo 5)
            n_clusters = min(5, max(2, len(hate_df) // 3))
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            hate_df['cluster'] = kmeans.fit_predict(X)

            # Prepara updates para o banco
            updates_map = {item['id']: {"id": item['id'], "mined": True, "cluster_id": None} for item in items}

            for _, row in hate_df.iterrows():
                item_id = row['id']
                if item_id in updates_map:
                    updates_map[item_id]["cluster_id"] = int(row['cluster'])

            updates = list(updates_map.values())

            if updates:
                await db_client.batch_update_comments(updates)
                self.logger.info(f"✅ {len(updates)} itens minerados ({len(hate_df)} clusterizados em {n_clusters} grupos) e atualizados no DB.")

        except Exception as e:
            self.logger.error(f"❌ Erro na mineração temática real: {e}", exc_info=True)
            # Fallback: marca como minerado para não travar a fila
            updates = [{"id": item['id'], "mined": True} for item in items]
            await db_client.batch_update_comments(updates)


    async def handle_failure(self, item: Dict[str, Any], error: Exception) -> None:
        self.logger.error(f"❌ Falha ao minerar item {item.get('id')}: {error}")

    def extrair_ngrams_periciais(self, df, coluna='bigrams', top_k=20):
        # Método utilitário mantido
        if coluna not in df.columns: return []
        all_grams = [gram for lista in df[coluna] for g in lista if isinstance(lista, list)]
        return Counter(all_grams).most_common(top_k)

data_miner = DataMiner()
