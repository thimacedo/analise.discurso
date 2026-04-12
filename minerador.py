# minerador.py
from collections import Counter
import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from datetime import datetime

class MineradorCorpus:
    def analisar_frequencia_ngrams(self, df, top_n=30):
        print("⛏️ Iniciando mineração de n-gramas...")
        
        all_tokens = df['tokens'].tolist()
        all_bigrams = []
        all_trigrams = []
        
        for tokens in all_tokens:
            if len(tokens) >= 2:
                all_bigrams.extend(list(zip(tokens, tokens[1:])))
            if len(tokens) >= 3:
                all_trigrams.extend(list(zip(tokens, tokens[2:])))
        
        freq_bg = Counter(all_bigrams).most_common(top_n)
        freq_tg = Counter(all_trigrams).most_common(top_n)
        
        return {
            'bigramas': [{'ngram': ' '.join(ng), 'freq': f} for ng, f in freq_bg],
            'trigramas': [{'ngram': ' '.join(ng), 'freq': f} for ng, f in freq_tg]
        }
    
    def gerar_nuvem_geral(self, freq_dist, filename="nuvem_geral.png"):
        wc = WordCloud(width=1200, height=800, background_color='white', colormap='Reds').generate_from_frequencies(freq_dist)
        plt.figure(figsize=(15, 10))
        plt.imshow(wc, interpolation='bilinear')
        plt.axis('off')
        plt.savefig(filename, dpi=300)
        print(f"🖼️ Nuvem de palavras salva: {filename}")
