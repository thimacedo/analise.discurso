
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os
from typing import Optional

class VisualEngine:
    """
    Motor de renderização visual para relatórios executivos.
    Gera gráficos de alta qualidade para incorporação em PDFs.
    """
    
    def __init__(self, output_dir: str = "data/visuals"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        # Configura tema global
        sns.set_theme(style="whitegrid")
        plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica', 'DejaVu Sans']

    def generate_pasa_breakdown(self, df: pd.DataFrame) -> Optional[str]:
        """Gera gráfico de barras das categorias PASA detectadas."""
        if 'category' not in df.columns:
            return None
            
        counts = df[df['is_hate_speech'] == True]['category'].value_counts()
        if counts.empty:
            return None

        plt.figure(figsize=(10, 6))
        # Paleta de cores oficial Sentinela
        palette = ["#ef4444", "#ec4899", "#f97316", "#f59e0b", "#8b5cf6", "#06b6d4"]
        
        ax = sns.barplot(x=counts.index, y=counts.values, hue=counts.index, palette=palette[:len(counts)], legend=False)
        plt.title("BREAKDOWN DE HOSTILIDADE (Protocolo PASA v16.4)", fontsize=14, fontweight='bold', pad=20)
        plt.ylabel("Volume de Interações", fontsize=10)
        plt.xlabel("Categorias de Risco", fontsize=10)
        plt.xticks(rotation=15, ha='right')
        
        # Adiciona rótulos de valores no topo das barras
        for p in ax.patches:
            ax.annotate(format(p.get_height(), '.0f'), 
                       (p.get_x() + p.get_width() / 2., p.get_height()), 
                       ha = 'center', va = 'center', 
                       xytext = (0, 9), 
                       textcoords = 'offset points',
                       fontsize=9, fontweight='bold')

        path = os.path.join(self.output_dir, "pasa_breakdown.png")
        plt.savefig(path, bbox_inches='tight', dpi=150)
        plt.close()
        return path

    def generate_temporal_trend(self, df: pd.DataFrame) -> Optional[str]:
        """Gera gráfico de linha com a evolução do ódio no tempo."""
        # Tenta localizar coluna de tempo
        time_col = None
        for col in ['data_coleta', 'created_at', 'data_publicacao']:
            if col in df.columns:
                time_col = col
                break
        
        if not time_col:
            return None

        try:
            df_temp = df.copy()
            df_temp[time_col] = pd.to_datetime(df_temp[time_col])
            # Agrupa por dia
            daily = df_temp[df_temp['is_hate_speech'] == True].resample('D', on=time_col).size().reset_index()
            daily.columns = ['Data', 'Alertas']
            
            if len(daily) < 2:
                return None

            plt.figure(figsize=(12, 5))
            sns.lineplot(data=daily, x='Data', y='Alertas', marker='o', color='#2563eb', linewidth=2.5)
            plt.fill_between(daily['Data'], daily['Alertas'], color='#2563eb', alpha=0.1)
            
            plt.title("EVOLUÇÃO TEMPORAL DE ALERTAS", fontsize=14, fontweight='bold', pad=20)
            plt.ylabel("Volume", fontsize=10)
            plt.xlabel("Período Analisado", fontsize=10)
            
            path = os.path.join(self.output_dir, "temporal_trend.png")
            plt.savefig(path, bbox_inches='tight', dpi=150)
            plt.close()
            return path
        except Exception as e:
            print(f"⚠️ Erro ao gerar gráfico temporal: {e}")
            return None

visual_engine = VisualEngine()
