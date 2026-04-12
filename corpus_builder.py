import pandas as pd
import re
import spacy
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.util import ngrams

nltk.download('stopwords')
nltk.download('punkt')

class CorpusBuilder:
    def __init__(self):
        self.nlp = spacy.load("pt_core_news_lg")
        self.stop_words = set(stopwords.words('portuguese'))
        # Adicionar stopwords específicas para contexto político
        self.stop_words.update(['pra', 'pro', 'tá', 'né', 'vai', 'mais', 'como', 'ser', 'ter', 'você', 'pra', 'aí', 'então'])
    
    def clean_text(self, text):
        """Limpeza e normalização do texto conforme metodologia do prof. Vichi"""
        text = text.lower()
        text = re.sub(r'http\S+|www\S+|@\S+', '', text)  # Remove URLs e menções
        text = re.sub(r'[^\w\s]', '', text)  # Remove pontuação
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def tokenize_lemmatize(self, text):
        """Tokenização e lematização com spaCy"""
        doc = self.nlp(text)
        tokens = [token.lemma_ for token in doc if token.text not in self.stop_words and token.is_alpha and len(token.text) > 2]
        return tokens
    
    def extract_ngrams(self, tokens, n=2):
        """Extração de n-gramas"""
        return list(ngrams(tokens, n))
    
    def build_corpus(self, df, text_column='text'):
        """Pipeline completo de construção do corpus"""
        df['clean_text'] = df[text_column].apply(self.clean_text)
        df['tokens'] = df['clean_text'].apply(self.tokenize_lemmatize)
        df['bigrams'] = df['tokens'].apply(lambda x: self.extract_ngrams(x, 2))
        df['trigrams'] = df['tokens'].apply(lambda x: self.extract_ngrams(x, 3))
        
        # Análise de frequência
        all_tokens = [token for tokens in df['tokens'] for token in tokens]
        freq_dist = Counter(all_tokens)
        
        # Salvar corpus processado
        df.to_csv('corpus_processado.csv', index=False, encoding='utf-8')
        
        # Salvar dicionário de frequência
        freq_df = pd.DataFrame(freq_dist.most_common(100), columns=['termo', 'frequencia'])
        freq_df.to_csv('frequencias_terminos.csv', index=False, encoding='utf-8')
        
        return df, freq_dist

    def save_corpus_stats(self, df, output_path='corpus_stats.json'):
        """Salva estatísticas do corpus para análise posterior"""
        stats = {
            'total_comments': len(df),
            'unique_users': df['username'].nunique() if 'username' in df else 0,
            'avg_comment_length': df['clean_text'].str.len().mean(),
            'total_tokens': sum(df['tokens'].str.len()),
            'unique_tokens': len(set([token for tokens in df['tokens'] for token in tokens])),
            'date_range': {'min': df['timestamp'].min() if 'timestamp' in df else None,
                          'max': df['timestamp'].max() if 'timestamp' in df else None}
        }
        import json
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
        return stats