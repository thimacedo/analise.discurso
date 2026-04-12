# processador.py
import re
import pandas as pd
import spacy
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from nltk.corpus import stopwords
import nltk
import os
from datetime import datetime

nltk.download('stopwords', quiet=True)

class ProcessadorCorpus:
    def __init__(self, modelo_spacy="pt_core_news_sm"):
        try:
            self.nlp = spacy.load(modelo_spacy)
        except OSError:
            print(f"⚠️ Modelo {modelo_spacy} não encontrado. Instalando...")
            os.system(f"python -m spacy download {modelo_spacy}")
            self.nlp = spacy.load(modelo_spacy)
        
        self.stop_words = set(stopwords.words('portuguese')).union({
            'pra', 'pro', 'tá', 'né', 'vai', 'mais', 'como', 'ser', 'ter', 'você',
            'aquele', 'aquela', 'isso', 'isto', 'aquilo', 'está', 'estão', 'era'
        })
    
    def limpar_texto(self, texto):
        if not isinstance(texto, str): return ""
        texto = texto.lower()
        texto = re.sub(r'http\S+|www\S+|@\S+', '', texto)
        texto = re.sub(r'[^\w\s]', '', texto)
        return re.sub(r'\s+', ' ', texto).strip()
    
    def tokenizar_lematizar(self, texto):
        doc = self.nlp(texto)
        return [
            token.lemma_ for token in doc 
            if token.text not in self.stop_words and token.is_alpha and len(token.text) > 2
        ]
    
    def processar_dataframe(self, df, coluna_texto='texto'):
        print("🧹 Iniciando pré-processamento...")
        df_proc = df.copy()
        df_proc['texto_limpo'] = df_proc[coluna_texto].apply(self.limpar_texto)
        df_proc['tokens'] = df_proc['texto_limpo'].apply(self.tokenizar_lematizar)
        df_proc = df_proc[df_proc['tokens'].map(len) > 0]
        
        todos_tokens = [t for tokens in df_proc['tokens'] for t in tokens]
        freq_dist = Counter(todos_tokens)
        return df_proc, freq_dist

    def salvar_corpus(self, df):
        fname = f"corpus_processado_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(fname, index=False, encoding='utf-8-sig')
        return fname
