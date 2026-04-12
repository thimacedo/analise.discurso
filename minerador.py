import pandas as pd
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

class MineradorCorpus:
    def analisar_frequencia_ngrams(self, df, coluna_tokens='tokens', top_n=30):
        print("⛏️ Iniciando mineração de n-gramas...")
        all_tokens = df[coluna_tokens].tolist()
        all_bigrams = []
        all_trigrams = []
        for tokens in all_tokens:
            if len(tokens) >= 2:
                all_bigrams.extend(list(zip(tokens, tokens[1:])))
            if len(tokens) >= 3:
                all_trigrams.extend(list(zip(tokens, tokens[2:])))
        return {
            'bigramas': [{'ngram': ng, 'freq': freq} for ng, freq in Counter(all_bigrams).most_common(top_n)],
            'trigramas': [{'ngram': ng, 'freq': freq} for ng, freq in Counter(all_trigrams).most_common(top_n)]
        }

    def analise_temporal(self, df):
        print("⏳ Processando análise temporal...")
        if 'timestamp' in df.columns:
            df_temp = df.copy()
            df_temp['date'] = pd.to_datetime(df_temp['timestamp']).dt.date
            daily_hate = df_temp.groupby('date')['is_hate_speech'].agg(['count', 'sum'])
            daily_hate['hate_rate'] = daily_hate['sum'] / daily_hate['count'] * 100
            mean_hate = daily_hate['hate_rate'].mean()
            std_hate = daily_hate['hate_rate'].std()
            peaks = daily_hate[daily_hate['hate_rate'] > mean_hate + 2*std_hate]
            return daily_hate, peaks
        return pd.DataFrame(), pd.DataFrame()

    def analise_comportamento_usuario(self, df):
        print("👤 Analisando comportamento de usuários...")
        if 'autor_username' in df.columns:
            user_stats = df.groupby('autor_username').agg({
                'texto': 'count',
                'is_hate_speech': 'sum'
            }).rename(columns={'texto': 'total_comments', 'is_hate_speech': 'hate_comments'})
            user_stats['hate_rate'] = user_stats['hate_comments'] / user_stats['total_comments'] * 100
            user_stats['risk_score'] = user_stats['hate_comments'] * user_stats['hate_rate']
            return user_stats.sort_values('risk_score', ascending=False)
        return pd.DataFrame()

    # CORREÇÃO #7: garantir n_clusters >= 2
    def clusterizacao_tematica(self, df):
        print("🧩 Aplicando clusterização temática...")
        hate_df = df[df['is_hate_speech'] == True].copy()
        if len(hate_df) > 10:
            vectorizer = TfidfVectorizer(max_features=100)
            X = vectorizer.fit_transform(hate_df['texto_limpo'].fillna(''))
            n_clusters = max(2, min(5, len(hate_df)//10))
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
            clusters = kmeans.fit_predict(X)
            terms = vectorizer.get_feature_names_out()
            cluster_topics = {}
            for i in range(kmeans.n_clusters):
                center = kmeans.cluster_centers_[i]
                top_indices = center.argsort()[-10:][::-1]
                cluster_topics[f'cluster_{i}'] = [terms[idx] for idx in top_indices]
            hate_df['cluster'] = clusters
            return hate_df, cluster_topics
        return hate_df, {}