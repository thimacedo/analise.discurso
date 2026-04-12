# minerador.py
from collections import Counter
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from datetime import datetime

class MineradorCorpus:
    def analisar_frequencia_ngrams(self, df, coluna_tokens='tokens', top_n=30):
        print("⛏️ Iniciando mineração do corpus...")
        
        all_tokens = df[coluna_tokens].tolist()
        all_bigrams = []
        all_trigrams = []
        
        for tokens in all_tokens:
            if len(tokens) >= 2:
                all_bigrams.extend(list(zip(tokens, tokens[1:])))
            if len(tokens) >= 3:
                all_trigrams.extend(list(zip(tokens, tokens[2:])))
        
        freq_bigramas = Counter(all_bigrams).most_common(top_n)
        freq_trigramas = Counter(all_trigrams).most_common(top_n)
        
        return {
            'bigramas': [{'ngram': ng, 'freq': freq} for ng, freq in freq_bigramas],
            'trigramas': [{'ngram': ng, 'freq': freq} for ng, freq in freq_trigramas]
        }
    
    def gerar_nuvem_ngrams(self, ngrams_freq, titulo, salvar=False):
        if not ngrams_freq:
            print(f"⚠️ Sem n-gramas para: {titulo}")
            return
        
        # Converte lista de dicts para dict formatado para WordCloud
        freq_dict = {" ".join(item['ngram']): item['freq'] for item in ngrams_freq}
        
        wc = WordCloud(
            width=1200, height=800, 
            background_color='white',
            max_words=50, 
            colormap='viridis'
        ).generate_from_frequencies(freq_dict)
        
        plt.figure(figsize=(15, 10))
        plt.imshow(wc, interpolation='bilinear')
        plt.axis('off')
        plt.title(titulo)
        
        if salvar:
            filename = f"nuvem_{titulo.lower().replace(' ', '_')}_{datetime.now().strftime('%H%M%S')}.png"
            plt.savefig(filename, dpi=300)
            print(f"🖼️ Nuvem salva: {filename}")
        
        return wc

    def analise_temporal(self, df, coluna_data='data_publicacao'):
        print("📊 Analisando evolução temporal...")
        
        # VALIDAÇÃO CONFORME SOLICITADO
        if 'is_hate_speech' not in df.columns:
            print("⚠️ Coluna is_hate_speech não encontrada, inicializando com False")
            df['is_hate_speech'] = False
            
        if coluna_data not in df.columns:
            print("⚠️ Sem coluna de data para análise temporal")
            return pd.DataFrame(), pd.DataFrame()
            
        df['data'] = pd.to_datetime(df[coluna_data]).dt.date
        daily = df.groupby('data').agg(
            total_comentarios=('id', 'count'),
            hate_comentarios=('is_hate_speech', 'sum')
        )
        daily['hate_rate'] = (daily['hate_comentarios'] / daily['total_comentarios']) * 100
        
        # Detecta picos (acima de 2 desvios padrão)
        media = daily['hate_rate'].mean()
        desvio = daily['hate_rate'].std()
        picos = daily[daily['hate_rate'] > media + (2 * desvio)]
        
        print(f"✅ Análise temporal concluída: {len(daily)} dias, {len(picos)} picos detectados")
        return daily, picos
