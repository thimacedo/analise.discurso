# classificador.py
import pandas as pd
from collections import defaultdict
from datetime import datetime

class ClassificadorOdio:
    def __init__(self):
        self.termos_odio = {
            'racismo': ['macaco', 'preto', 'crioulo', 'selvagem', 'negro', 'raça', 'inferior', 'escravo'],
            'homofobia': ['viado', 'bicha', 'gay', 'sapatão', 'bixa', 'veado', 'baitola', 'boiola'],
            'transfobia': ['traveco', 'travesti', 'transexual', 'anormal', 'doente'],
            'misoginia': ['puta', 'vadia', 'cadela', 'vagabunda', 'prostituta', 'piranha', 'safada'],
            'xenofobia': ['nordestino', 'baiano', 'paraíba', 'cearense', 'migrante']
        }
    
    def classificar_texto(self, texto_limpo):
        if not isinstance(texto_limpo, str): return 'neutro', 0
        
        texto_lower = texto_limpo.lower()
        scores = defaultdict(int)
        
        for cat, termos in self.termos_odio.items():
            for t in termos:
                if t in texto_lower:
                    scores[cat] += 1
        
        if not scores: return 'neutro', 0
        
        cat_principal = max(scores, key=scores.get)
        severidade = min(10, scores[cat_principal] * 2)
        return cat_principal, severidade

    def processar_dataframe(self, df):
        print("🏷️ Classificando discurso de ódio...")
        results = df['texto_limpo'].apply(self.classificar_texto)
        df['categoria_odio'], df['severidade'] = zip(*results)
        
        counts = df['categoria_odio'].value_counts()
        print(f"📊 Resultado da Classificação:\n{counts}")
        return df
