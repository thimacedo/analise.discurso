# minerador.py
import pandas as pd
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os

class MineradorCorpus:
    """
    Minerador de Corpus com análise de n-gramas e visualização forense.
    Foca na descoberta de padrões de discurso de ódio.
    """
    def __init__(self, output_dir="visualizacoes"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def extrair_ngrams_periciais(self, df, coluna_tokens='tokens', n=2, top_k=20):
        """Extrai bigramas (n=2) ou trigramas (n=3) que formam expressões de ódio."""
        print(f"⛏️ Minerando {n}-gramas periciais...")
        all_tokens_list = df[coluna_tokens].tolist()
        grams = []
        for tokens in all_tokens_list:
            if len(tokens) >= n:
                # Criamos combinações sequenciais
                grams.extend([" ".join(tokens[i:i+n]) for i in range(len(tokens)-n+1)])
        
        return Counter(grams).most_common(top_k)

    def gerar_nuvem_pericial(self, df, categoria_odio=None, prefixo="nuvem"):
        """Gera nuvens de palavras para categorias específicas de ódio."""
        print(f"☁️ Gerando nuvem de palavras para: {categoria_odio if categoria_odio else 'Geral'}")
        
        if categoria_odio:
            subset = df[df['categoria_odio'] == categoria_odio]
            if subset.empty:
                print(f"⚠️ Sem dados para a categoria {categoria_odio}.")
                return
            texto = " ".join(subset['texto_limpo'].astype(str))
            titulo = f"Nuvem de Palavras - {categoria_odio.upper()}"
            figname = f"{prefixo}_{categoria_odio}.png"
        else:
            texto = " ".join(df['texto_limpo'].astype(str))
            titulo = "Nuvem de Palavras Geral"
            figname = f"{prefixo}_geral.png"

        wc = WordCloud(
            width=1200, height=800, 
            background_color='white',
            colormap='inferno',
            max_words=100
        ).generate(texto)

        plt.figure(figsize=(15, 10))
        plt.imshow(wc, interpolation='bilinear')
        plt.title(titulo, fontsize=20)
        plt.axis("off")
        
        path = os.path.join(self.output_dir, figname)
        plt.savefig(path)
        plt.close()
        return path

    def analise_perfil_odio(self, df):
        """Identifica quais perfis (candidatos) recebem mais ataques e de que tipo."""
        print("👤 Analisando perfil de hostilidade por candidato...")
        perfil = df.groupby(['candidato', 'categoria_odio']).size().unstack(fill_value=0)
        perfil['total_ataques'] = perfil.sum(axis=1)
        # Removemos 'neutro' do cálculo de taxa de hostilidade se ele existir
        if 'neutro' in perfil.columns:
            perfil['taxa_odio'] = (perfil['total_ataques'] - perfil['neutro']) / perfil['total_ataques']
        return perfil.sort_values('total_ataques', ascending=False)
