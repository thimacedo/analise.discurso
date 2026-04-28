import pandas as pd
import numpy as np
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import networkx as nx
from collections import defaultdict
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import os

class DataMiner:
    def __init__(self, df_processado, output_dir="visualizacoes"):
        self.df = df_processado
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

        # Assume que após o scraper + IA, você tenha uma coluna 'is_hate_speech' (booleano)
        # Se não existir, cria como False para não quebrar o código
        if 'is_hate_speech' not in self.df.columns:
            self.df['is_hate_speech'] = False
            
        self.hate_df = self.df[self.df['is_hate_speech'] == True]

    def extrair_ngrams_periciais(self, coluna='bigrams', top_k=20):
        """Extrai os n-gramas mais comuns de forma eficiente."""
        all_grams = [gram for lista in self.df[coluna] for gram in lista]
        all_grams_str = [" ".join(g) for g in all_grams]
        return Counter(all_grams_str).most_common(top_k)

    def analise_temporal(self):
        if 'timestamp' not in self.df.columns: return None
        # Converte timestamp Unix para DateTime
        self.df['date'] = pd.to_datetime(self.df['timestamp'], unit='s').dt.date
        daily = self.df.groupby('date').agg(
            total=('text', 'count'),
            hate_count=('is_hate_speech', 'sum')
        )
        daily['hate_rate'] = (daily['hate_count'] / daily['total'] * 100).fillna(0)
        
        # Detecta picos estatísticos (Z-Score > 2)
        if len(daily) > 2:
            daily['is_peak'] = (daily['hate_rate'] - daily['hate_rate'].mean()) > (2 * daily['hate_rate'].std())
        return daily

    def thematic_clustering(self):
        """Agrupamento temático usando TF-IDF e KMeans robusto."""
        textos = self.hate_df['texto_limpo'].fillna('')
        if len(textos) < 15: # Mínimo de amostras para clusterizar
            print("⚠️ Poucos dados de ódio para clusterização.")
            return self.hate_df, {}

        vectorizer = TfidfVectorizer(max_features=100)
        X = vectorizer.fit_transform(textos)
        
        # Define clusters dinamicamente (máx 5, ou 1 para cada 15 textos)
        n_clusters = min(5, max(2, len(textos) // 15))
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        self.hate_df = self.hate_df.copy()
        self.hate_df['cluster'] = kmeans.fit_predict(X)
        
        terms = vectorizer.get_feature_names_out()
        topics = {}
        for i in range(n_clusters):
            center = kmeans.cluster_centers_[i]
            top_indices = center.argsort()[-10:][::-1]
            topics[f'Cluster_{i}'] = [terms[idx] for idx in top_indices]
            
        return self.hate_df, topics

    def gerar_nuvem_palavras(self, categoria=None):
        """Gera nuvem de palavras (fpdf2 não suporta imagens diretas, então salvamos em PNG)."""
        if categoria and categoria in self.hate_df.columns:
            texto = " ".join(self.hate_df[self.hate_df['categoria_ia'] == categoria]['texto_limpo'].astype(str))
            nome = f"nuvem_{categoria}.png"
        else:
            texto = " ".join(self.df['texto_limpo'].astype(str))
            nome = "nuvem_geral.png"

        if not texto.strip(): return None

        wc = WordCloud(width=1200, height=800, background_color='white', colormap='inferno').generate(texto)
        plt.figure(figsize=(10, 8))
        plt.imshow(wc, interpolation='bilinear')
        plt.axis("off")
        
        path = os.path.join(self.output_dir, nome)
        plt.savefig(path, bbox_inches='tight')
        plt.close()
        return path
