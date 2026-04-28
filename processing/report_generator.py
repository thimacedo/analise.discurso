import os
from fpdf import FPDF
from datetime import datetime
import pandas as pd

class ReportGenerator(FPDF):
    def __init__(self):
        super().__init__()
        # Adiciona fonte com suporte a UTF-8
        try:
            self.add_font('Arial', '', 'C:\\Windows\\Fonts\\arial.ttf')
            self.add_font('Arial', 'B', 'C:\\Windows\\Fonts\\arialbd.ttf')
        except:
            # Fallback para ambientes Linux/Server
            pass

    def header(self):
        self.set_font('Helvetica', 'B', 14)
        self.set_text_color(37, 99, 235)
        self.cell(0, 10, 'SENTINELA DEMOCRÁTICA - DOSSIÊ INTELIGÊNCIA', align="C")
        self.ln(10)
        self.set_draw_color(37, 99, 235)
        self.line(10, 20, 200, 20)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Página {self.page_no()} | Gerado em {datetime.now().strftime("%d/%m/%Y %H:%M")}', align='C')

    def render_item(self, item):
        if self.get_y() > 250:
            self.add_page()

        self.set_fill_color(245, 245, 250)
        self.rect(10, self.get_y(), 190, 35, 'F')
        
        autor = item.get('owner_username', 'Desconhecido')
        post_ref = item.get('post_shortcode', 'N/A')
        
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(0, 0, 0)
        self.cell(0, 6, f'Autor: @{autor} | Post: {post_ref}')
        self.ln(6)

        texto = item.get('text', '')[:300] + "..." if len(item.get('text', '')) > 300 else item.get('text', '')
        self.set_font('Helvetica', '', 8)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5, f"Conteúdo: {texto}")

        is_hate = item.get('is_hate_speech', False)
        status = "AGRESSIVO / DISCURSO DE ÓDIO" if is_hate else "NEUTRO / MONITORADO"
        cor = (220, 38, 38) if is_hate else (37, 99, 235)
        
        self.set_font('Helvetica', 'B', 8)
        self.set_text_color(*cor)
        self.cell(0, 6, f"Status: {status}")
        self.ln(10)

    def generate_pdf(self, df_final, output_path):
        if df_final is None or df_final.empty:
            print("⚠️ DataFrame vazio. Nenhum PDF gerado.")
            return None

        self.add_page()
        self.set_font('Helvetica', '', 10)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 8, f"Análise situacional contendo {len(df_final)} interações mapeadas.")
        self.ln(5)

        for _, row in df_final.iterrows():
            self.render_item(row.to_dict())

        self.output(output_path)
        print(f"📄 Relatório salvo em: {output_path}")
        return output_path
