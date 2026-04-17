# processador.py
import re
import pandas as pd
import spacy
import emoji
import os
from datetime import datetime
from nltk.corpus import stopwords
import nltk

nltk.download('stopwords', quiet=True)

class ProcessadorCorpus:
    """
    Processador de Corpus baseado na metodologia de Linguística Forense (Prof. Leonardo Vichi).
    Foca em preservação de sentido, tratamento de emojis e limpeza seletiva.
    """
    def __init__(self, modelo_spacy="pt_core_news_lg"):
        try:
            self.nlp = spacy.load(modelo_spacy)
        except OSError:
            print(f"⚠️ Modelo {modelo_spacy} não encontrado. Instalando versão 'lg' para maior precisão...")
            os.system(f"python -m spacy download {modelo_spacy}")
            self.nlp = spacy.load(modelo_spacy)
        
        # Stopwords customizadas: mantemos negativas e pronomes de tratamento que indicam hierarquia/ironia
        base_stopwords = set(stopwords.words('portuguese'))
        negativas = {'não', 'nem', 'nunca', 'jamais', 'nada', 'ninguém'}
        self.stop_words = (base_stopwords - negativas).union({
            'pra', 'pro', 'tá', 'né', 'vai', 'aqui', 'lá', 'isso', 'isto', 'aquilo'
        })

    def converter_emojis(self, texto):
        """Transforma emojis em texto (ex: 😠 -> :angry_face:) para análise forense."""
        return emoji.demojize(texto, language='pt')

    def limpar_texto_forense(self, texto):
        """Limpeza que preserva marcadores de ódio e intensidade."""
        if not isinstance(texto, str): return ""
        
        # 1. Converter emojis antes de remover pontuação
        texto = self.converter_emojis(texto)
        
        # 2. Lowercase seletivo (preservar CAIXA ALTA pode indicar grito/agressividade futuramente)
        texto = texto.lower()
        
        # 3. Remover URLs e Menções
        texto = re.sub(r'http\S+|www\S+|@\S+', '', texto)
        
        # 4. Remover caracteres especiais mas manter pontuação de intensidade (!!! ???)
        # Para análise de tokens pura, limpamos mais:
        texto = re.sub(r'[^a-z0-9áéíóúâêôãõç\s\:\_]', '', texto)
        
        return re.sub(r'\s+', ' ', texto).strip()
    
    def tokenizar_pericial(self, texto):
        """Tokenização com lematização focada em termos políticos e ofensivos."""
        doc = self.nlp(texto)
        tokens = []
        for token in doc:
            # Filtramos stopwords (exceto as negativas preservadas) e tokens muito curtos (exceto emojis convertidos)
            if (token.text not in self.stop_words and token.is_alpha) or (":" in token.text):
                if len(token.text) > 2:
                    # Usamos o lemma para agrupar variações de uma mesma ofensa
                    tokens.append(token.lemma_)
        return tokens
    
    def processar_dataframe(self, df, coluna_texto='texto'):
        print("🧹 Iniciando pré-processamento forense...")
        df_proc = df.copy()
        
        # Limpeza e conversão
        df_proc['texto_limpo'] = df_proc[coluna_texto].apply(self.limpar_texto_forense)
        
        # Tokenização pericial
        df_proc['tokens'] = df_proc['texto_limpo'].apply(self.tokenizar_pericial)
        
        # Filtro de linhas vazias após processamento
        df_proc = df_proc[df_proc['tokens'].map(len) > 0]
        
        print(f"✅ Processamento concluído: {len(df_proc)} registros válidos.")
        return df_proc

    def salvar_corpus(self, df, prefixo="corpus_processado"):
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        fname = f"{prefixo}_{ts}.csv"
        df.to_csv(fname, index=False, encoding='utf-8-sig')
        return fname
