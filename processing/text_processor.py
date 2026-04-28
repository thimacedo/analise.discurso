import re
import pandas as pd
import spacy
import emoji
from nltk.corpus import stopwords
import nltk

nltk.download('stopwords', quiet=True)

class TextProcessor:
    def __init__(self, modelo_spacy="pt_core_news_lg"):
        try:
            self.nlp = spacy.load(modelo_spacy)
        except OSError:
            print(f"⚠️ Baixando modelo Spacy {modelo_spacy}...")
            import os
            os.system(f"python -m spacy download {modelo_spacy}")
            self.nlp = spacy.load(modelo_spacy)
        
        # Preserva negações para contexto de ódio (ex: "não é corrupto")
        base_stopwords = set(stopwords.words('portuguese'))
        negativas = {'não', 'nem', 'nunca', 'jamais', 'nada', 'ninguém'}
        self.stop_words = (base_stopwords - negativas).union({
            'pra', 'pro', 'tá', 'né', 'vai', 'aqui', 'lá', 'isso', 'isto', 'aquilo'
        })

    def converter_emojis(self, texto):
        return emoji.demojize(texto, language='pt')

    def limpar_texto(self, texto):
        if pd.isna(texto) or not isinstance(texto, str): return ""
        texto = self.converter_emojis(texto)
        texto = texto.lower()
        texto = re.sub(r'http\S+|www\S+|@\S+', '', texto) # Remove URLs e menções
        # Mantém letras com acento, números e espaços. Remove pontuação excessiva.
        texto = re.sub(r'[^a-z0-9áéíóúâêôãõç\s\:\_]', '', texto)
        return re.sub(r'\s+', ' ', texto).strip()
    
    def tokenizar_lematizar(self, texto):
        doc = self.nlp(texto)
        # Mantém tokens alfabéticos ou emojis convertidos (que contêm ':')
        return [
            token.lemma_ for token in doc 
            if (token.text not in self.stop_words and token.is_alpha) or ":" in token.text
            if len(token.text) > 2
        ]
    
    def processar_dataframe(self, df, coluna_texto='text'):
        """Pipeline principal. Recebe o DF do scraper e retorna processado."""
        print("🤖 text_processor.py: Iniciando pipeline forense...")
        df_proc = df.copy()
        
        df_proc['texto_limpo'] = df_proc[coluna_texto].apply(self.limpar_texto)
        df_proc['tokens'] = df_proc['texto_limpo'].apply(self.tokenizar_lematizar)
        
        # Remove linhas que ficaram vazias após limpeza
        df_proc = df_proc[df_proc['tokens'].str.len() > 0].reset_index(drop=True)
        
        # Gera bigramas e trigramas diretamente no DF
        df_proc['bigrams'] = df_proc['tokens'].apply(lambda x: list(nltk.ngrams(x, 2)) if len(x) >= 2 else [])
        df_proc['trigrams'] = df_proc['tokens'].apply(lambda x: list(nltk.ngrams(x, 3)) if len(x) >= 3 else [])
        
        print(f"✅ Processamento concluído: {len(df_proc)} registros válidos.")
        return df_proc
