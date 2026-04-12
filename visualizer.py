import matplotlib
matplotlib.use('Agg')  # Para execução sem interface gráfica
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import pandas as pd
from collections import Counter

class DataVisualizer:
    def __init__(self, classified_df, freq_dist):
        self.df = classified_df
        self.freq_dist = freq_dist
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 8)
    
    def create_wordcloud(self, category=None, save_path='wordcloud.png'):
        """Cria nuvem de palavras conforme metodologia do prof. Vichi"""
        if category:
            filtered_texts = self.df[self.df['primary_category'] == category]['clean_text'].dropna()
        else:
            filtered_texts = self.df['clean_text'].dropna()
        
        if len(filtered_texts) == 0:
            return None
            
        all_text = ' '.join(filtered_texts)
        
        wordcloud = WordCloud(
            width=1200,
            height=800,
            background_color='white',
            max_words=100,
            colormap='Reds',
            stopwords=set(['pra', 'pro', 'tá', 'né', 'vai', 'mais', 'como', 'ser', 'ter', 'você'])
        ).generate(all_text)
        
        plt.figure(figsize=(15, 10))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title(f'Nuvem de Palavras - Discurso de Ódio{" - " + category if category else ""}', fontsize=20)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return wordcloud
    
    def plot_hate_timeline(self, daily_hate, peaks, save_path='timeline.png'):
        """Gráfico de evolução temporal do discurso de ódio"""
        if len(daily_hate) == 0:
            return
            
        fig, ax = plt.subplots(figsize=(14, 6))
        
        ax.plot(daily_hate.index, daily_hate['hate_rate'], 
                marker='o', linewidth=2, markersize=4, color='darkred')
        ax.fill_between(daily_hate.index, daily_hate['hate_rate'], alpha=0.3, color='red')
        
        if len(peaks) > 0:
            ax.scatter(peaks.index, peaks['hate_rate'], 
                      color='gold', s=100, zorder=5, label='Picos Detectados')
        
        ax.set_xlabel('Data', fontsize=12)
        ax.set_ylabel('Taxa de Discurso de Ódio (%)', fontsize=12)
        ax.set_title('Evolução Temporal do Discurso de Ódio', fontsize=16)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_category_distribution(self, save_path='categories.png'):
        """Distribuição das categorias de discurso de ódio"""
        hate_df = self.df[self.df['is_hate_speech'] == True]
        if len(hate_df) == 0:
            return
            
        category_counts = hate_df['primary_category'].value_counts()
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Gráfico de barras
        colors = ['#8B0000', '#B22222', '#DC143C', '#FF0000', '#FF6347']
        bars = ax1.bar(category_counts.index, category_counts.values, color=colors)
        ax1.set_xlabel('Categoria', fontsize=12)
        ax1.set_ylabel('Número de Comentários', fontsize=12)
        ax1.set_title('Distribuição por Categoria de Ódio', fontsize=14)
        ax1.tick_params(axis='x', rotation=45)
        
        # Adicionar valores nas barras
        for bar, value in zip(bars, category_counts.values):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                    str(value), ha='center', va='bottom')
        
        # Gráfico de pizza
        ax2.pie(category_counts.values, labels=category_counts.index, 
                autopct='%1.1f%%', colors=colors, startangle=90)
        ax2.set_title('Proporção por Categoria', fontsize=14)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def plot_top_terms(self, n=20, save_path='top_terms.png'):
        """Gráfico de barras com os termos mais frequentes"""
        top_terms = self.freq_dist.most_common(n)
        terms, counts = zip(*top_terms)
        
        plt.figure(figsize=(12, 8))
        bars = plt.barh(terms, counts, color='coral')
        plt.xlabel('Frequência', fontsize=12)
        plt.ylabel('Termos', fontsize=12)
        plt.title(f'Top {n} Termos Mais Frequentes no Corpus', fontsize=16)
        plt.gca().invert_yaxis()
        
        # Adicionar valores
        for bar, count in zip(bars, counts):
            plt.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                    str(count), va='center')
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def generate_report(self, output_path='relatorio_pericial.html'):
        """Gera relatório HTML completo com todas as análises"""
        hate_count = len(self.df[self.df['is_hate_speech'] == True])
        total_count = len(self.df)
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Relatório Pericial - Análise de Discurso de Ódio</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                h1 {{ color: #8B0000; border-bottom: 2px solid #8B0000; }}
                .metric {{ background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                .metric-value {{ font-size: 24px; font-weight: bold; color: #8B0000; }}
                .insight {{ background: #e8f5e9; padding: 15px; margin: 10px 0; border-left: 4px solid #4CAF50; }}
                img {{ max-width: 100%; margin: 20px 0; border: 1px solid #ddd; border-radius: 4px; }}
            </style>
        </head>
        <body>
            <h1>Relatório Pericial - Análise de Discurso de Ódio</h1>
            <p><strong>Data do Relatório:</strong> {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <div class="metric">
                <h3>📊 Estatísticas Gerais</h3>
                <p>Total de Comentários Analisados: <span class="metric-value">{total_count}</span></p>
                <p>Comentários com Discurso de Ódio: <span class="metric-value">{hate_count}</span></p>
                <p>Taxa de Incidência: <span class="metric-value">{hate_count/total_count*100:.2f}%</span></p>
            </div>
            
            <div class="insight">
                <h3>💡 Insights Principais</h3>
                <p>{self._generate_insights()}</p>
            </div>
            
            <h2>📈 Visualizações</h2>
            <img src="nuvem_geral.png" alt="Nuvem de Palavras">
            <img src="categories.png" alt="Distribuição por Categoria">
            <img src="top_terms.png" alt="Termos Mais Frequentes">
            
            <h2>📋 Recomendações</h2>
            <p>{self._generate_recommendations()}</p>
        </body>
        </html>
        """
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Relatório gerado: {output_path}")
    
    def _generate_insights(self):
        """Gera insights automáticos baseados nos dados"""
        hate_df = self.df[self.df['is_hate_speech'] == True]
        top_category = hate_df['primary_category'].mode().iloc[0] if len(hate_df) > 0 else "N/A"
        
        return f"""
        A análise identificou uma taxa de incidência de discurso de ódio de {len(hate_df)/len(self.df)*100:.2f}% 
        nos comentários analisados. A categoria mais frequente é '{top_category}', representando uma parcela 
        significativa dos casos identificados. Recomenda-se atenção especial a usuários com padrões recorrentes 
        de comportamento hostil e monitoramento contínuo durante o período eleitoral.
        """
    
    def _generate_recommendations(self):
        """Gera recomendações baseadas na análise"""
        return """
        1. Implementar moderação proativa com base nos termos identificados
        2. Estabelecer parâmetros para denúncia de discurso de ódio nas plataformas
        3. Criar relatórios periódicos para acompanhamento de tendências
        4. Capacitar equipes de moderação para identificação de nuances contextuais
        5. Documentar casos graves para possível ação judicial
        """