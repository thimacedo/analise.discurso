import re
import pandas as pd
import spacy
import nltk
import os
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
from datetime import datetime

# Garantir stopwords
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class ProcessadorCorpus:
    def __init__(self, modelo_spacy="pt_core_news_sm"):
        try:
            self.nlp = spacy.load(modelo_spacy)
        except OSError:
            print(f"⚠️ Instalando modelo {modelo_spacy}...")
            os.system(f"python -m spacy download {modelo_spacy}")
            self.nlp = spacy.load(modelo_spacy)
        
        self.stop_words = set(stopwords.words('portuguese'))
        self.stop_words.update([
            'pra', 'pro', 'tá', 'né', 'vai', 'mais', 'como', 'ser', 'ter', 'você',
            'está', 'estão', 'gente', 'tudo', 'aqui', 'lá', 'fazer', 'querer'
        ])

    def limpar_texto(self, texto):
        if not isinstance(texto, str): return ""
        texto = texto.lower()
        texto = re.sub(r'http\S+|www\S+|@\S+', '', texto) # Limpa URLs e Menções
        texto = re.sub(r'[^\w\s]', '', texto)             # Remove pontuação
        return re.sub(r'\s+', ' ', texto).strip()         # Normaliza espaços

    def tokenizar_lematizar(self, texto):
        doc = self.nlp(texto)
        return [
            token.lemma_ for token in doc 
            if token.text not in self.stop_words 
            and token.is_alpha 
            and len(token.text) > 2
        ]

    def processar_dataframe(self, df, coluna_texto='texto'):
        print(f"🧹 Processando {len(df)} documentos...")
        df_proc = df.copy()
        
        # Limpeza e NLP
        df_proc['texto_limpo'] = df_proc[coluna_texto].apply(self.limpar_texto)
        df_proc['tokens'] = df_proc['texto_limpo'].apply(self.tokenizar_lematizar)
        
        # Filtrar vazios
        df_proc = df_proc[df_proc['tokens'].map(len) > 0]
        
        # Frequência
        todos_tokens = [t for tokens in df_proc['tokens'] for t in tokens]
        freq_dist = Counter(todos_tokens)
        
        print(f"✅ Processamento concluído: {len(freq_dist)} termos únicos encontrados.")
        return df_proc, freq_dist

    def gerar_nuvem_palavras(self, freq_dist, salvar=True):
        if not freq_dist: return
        
        wc = WordCloud(
            width=1200, height=800, 
            background_color='white', 
            max_words=100,
            colormap='inferno'
        ).generate_from_frequencies(freq_dist)
        
        plt.figure(figsize=(15, 10))
        plt.imshow(wc, interpolation='bilinear')
        plt.axis('off')
        
        if salvar:
            filename = f"nuvem_geral_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(filename, dpi=300)
            print(f"🖼️ Nuvem salva em: {filename}")
        
        return filename

    def salvar_corpus(self, df):
        filename = f"corpus_processado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"💾 Corpus processado salvo em: {filename}")
        return filename
