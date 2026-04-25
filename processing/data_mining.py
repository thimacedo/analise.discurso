import pandas as pd
import numpy as np
from scipy import stats
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import networkx as nx
from collections import defaultdict

class DataMiner:
    def __init__(self, classified_df):
        self.df = classified_df
        self.hate_df = self.df[self.df['is_hate_speech'] == True]
    
    def temporal_analysis(self):
        """Análise temporal da ocorrência de discurso de ódio"""
        if 'timestamp' in self.df.columns:
            self.df['date'] = pd.to_datetime(self.df['timestamp']).dt.date
            daily_hate = self.df.groupby('date')['is_hate_speech'].agg(['count', 'sum'])
            daily_hate['hate_rate'] = daily_hate['sum'] / daily_hate['count'] * 100
            
            # Detectar picos
            mean_hate = daily_hate['hate_rate'].mean()
            std_hate = daily_hate['hate_rate'].std()
            peaks = daily_hate[daily_hate['hate_rate'] > mean_hate + 2*std_hate]
            
            return daily_hate, peaks
        return pd.DataFrame(), pd.DataFrame()
    
    def user_behavior_analysis(self):
        """Análise de comportamento por usuário"""
        if 'username' in self.df.columns:
            user_stats = self.df.groupby('username').agg({
                'text': 'count',
                'is_hate_speech': 'sum'
            }).rename(columns={'text': 'total_comments', 'is_hate_speech': 'hate_comments'})
            user_stats['hate_rate'] = user_stats['hate_comments'] / user_stats['total_comments'] * 100
            user_stats['risk_score'] = user_stats['hate_comments'] * user_stats['hate_rate']
            
            return user_stats.sort_values('risk_score', ascending=False)
        return pd.DataFrame()
    
    def thematic_clustering(self):
        """Agrupamento temático dos comentários de ódio"""
        if len(self.hate_df) > 10:
            vectorizer = TfidfVectorizer(max_features=100, stop_words='portuguese')
            X = vectorizer.fit_transform(self.hate_df['clean_text'].fillna(''))
            
            # K-means clustering
            kmeans = KMeans(n_clusters=min(5, len(self.hate_df)//10), random_state=42)
            clusters = kmeans.fit_predict(X)
            
            # Extrair termos mais relevantes por cluster
            terms = vectorizer.get_feature_names_out()
            cluster_topics = {}
            for i in range(kmeans.n_clusters):
                center = kmeans.cluster_centers_[i]
                top_indices = center.argsort()[-10:][::-1]
                top_terms = [terms[idx] for idx in top_indices]
                cluster_topics[f'cluster_{i}'] = top_terms
            
            self.hate_df['cluster'] = clusters
            return self.hate_df, cluster_topics
        return self.hate_df, {}
    
    def co_occurrence_network(self):
        """Rede de co-ocorrência de termos de ódio"""
        # Construir rede de termos que aparecem juntos nos comentários
        co_occurrence = defaultdict(lambda: defaultdict(int))
        
        for text in self.hate_df['clean_text'].fillna(''):
            words = set(text.split())
            words = [w for w in words if len(w) > 3]
            for i, w1 in enumerate(words):
                for w2 in words[i+1:]:
                    co_occurrence[w1][w2] += 1
                    co_occurrence[w2][w1] += 1
        
        # Criar grafo
        G = nx.Graph()
        for w1 in co_occurrence:
            for w2, weight in co_occurrence[w1].items():
                if weight >= 3:  # Threshold mínimo
                    G.add_edge(w1, w2, weight=weight)
        
        return G
