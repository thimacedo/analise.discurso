# classificador.py
import pandas as pd
from collections import defaultdict

class ClassificadorOdio:
    def __init__(self):
        # Dicionário Forense Baseado na Metodologia
        self.termos_odio = {
            'racismo': ['macaco', 'preto', 'crioulo', 'selvagem', 'negro', 'raça', 'inferior', 'escravo'],
            'homofobia': ['viado', 'bicha', 'gay', 'sapatão', 'bixa', 'veado', 'baitola', 'boiola'],
            'transfobia': ['traveco', 'travesti', 'transexual', 'aberração', 'anormal'],
            'misoginia': ['puta', 'vadia', 'cadela', 'vagabunda', 'prostituta', 'piranha'],
            'xenofobia': ['nordestino', 'baiano', 'paraíba', 'cearense', 'norte', 'invasor']
        }
    
    def classificar_comentario(self, texto_limpo):
        if not isinstance(texto_limpo, str): return 'neutro', 0
        
        texto_lower = texto_limpo.lower()
        categorias_encontradas = defaultdict(int)
        
        for categoria, termos in self.termos_odio.items():
            for termo in termos:
                if termo in texto_lower:
                    categorias_encontradas[categoria] += 1
        
        if categorias_encontradas:
            categoria_principal = max(categorias_encontradas, key=categorias_encontradas.get)
            severidade = min(10, categorias_encontradas[categoria_principal] * 2)
            return categoria_principal, severidade
        else:
            return 'neutro', 0
    
    def classificar_dataframe(self, df, coluna_texto='texto_limpo'):
        print("🏷️ Iniciando classificação do discurso de ódio...")
        results = df[coluna_texto].apply(self.classificar_comentario)
        df['categoria_odio'], df['severidade'] = zip(*results)
        
        comentarios_odio = df[df['categoria_odio'] != 'neutro']
        print(f"  → {len(comentarios_odio)} comentários identificados com discurso de ódio.")
        return df
