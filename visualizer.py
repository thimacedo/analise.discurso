# visualizer.py
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import pandas as pd

class DataVisualizer:
    def __init__(self, df, freq_dist):
        self.df = df
        self.freq_dist = freq_dist
        sns.set_style("whitegrid")

    def create_wordcloud(self, save_path='wordcloud.png'):
        if not self.freq_dist:
            print("Sem dados para nuvem de palavras.")
            return
        wc = WordCloud(width=1200, height=800, background_color='white', max_words=100, colormap='Reds')
        wc.generate_from_frequencies(self.freq_dist)
        plt.figure(figsize=(15,10))
        plt.imshow(wc, interpolation='bilinear')
        plt.axis('off')
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✅ Nuvem salva: {save_path}")

    def plot_category_distribution(self, save_path='categories.png'):
        hate_df = self.df[self.df['is_hate_speech'] == True]
        if hate_df.empty:
            print("Sem discurso de ódio para gerar gráfico de categorias.")
            return
        cat_counts = hate_df['categoria_odio'].value_counts()
        plt.figure(figsize=(10,6))
        cat_counts.plot(kind='bar', color='coral')
        plt.title('Distribuição por categoria de ódio')
        plt.xlabel('Categoria')
        plt.ylabel('Número de ocorrências')
        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        plt.close()

    def plot_top_terms(self, n=20, save_path='top_terms.png'):
        top = self.freq_dist.most_common(n)
        if not top:
            return
        termos, freqs = zip(*top)
        plt.figure(figsize=(12,8))
        plt.barh(termos, freqs, color='teal')
        plt.gca().invert_yaxis()
        plt.title(f'Top {n} termos mais frequentes')
        plt.xlabel('Frequência')
        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        plt.close()

    def plot_hate_timeline(self, daily_hate, peaks, save_path='timeline.png'):
        if daily_hate.empty:
            return
        plt.figure(figsize=(12,6))
        plt.plot(daily_hate.index, daily_hate['hate_rate'], marker='o', color='darkred')
        if not peaks.empty:
            plt.scatter(peaks.index, peaks['hate_rate'], color='gold', s=80, label='Picos')
        plt.title('Evolução temporal do discurso de ódio')
        plt.xlabel('Data')
        plt.ylabel('Taxa de ódio (%)')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300)
        plt.close()

    def generate_report(self, output_path='relatorio_pericial.html'):
        total = len(self.df)
        hate = (self.df['is_hate_speech'] == True).sum()
        html = f"""<!DOCTYPE html>
        <html><head><meta charset='UTF-8'><title>Relatório ForenseNet</title></head>
        <body><h1>Relatório de Análise de Discurso</h1>
        <p>Total de comentários: {total}</p>
        <p>Com discurso de ódio: {hate} ({hate/total*100:.2f}%)</p>
        <img src='nuvem_geral.png' width='80%'>
        <img src='categories.png' width='80%'>
        <img src='top_terms.png' width='80%'>
        </body></html>"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"📄 Relatório gerado: {output_path}")