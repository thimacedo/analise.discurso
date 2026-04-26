from fpdf import FPDF
from datetime import datetime

class DossieService(FPDF):
    def header(self):
        # Logo ou Identificador do Sentinela
        self.set_font("helvetica", "B", 15)
        self.set_text_color(37, 99, 235) # Azul Sentinela
        self.cell(0, 10, "SENTINELA DEMOCRÁTICA", ln=1, align="L")
        self.set_font("helvetica", "", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, "Dossiê de Inteligência e Análise Situacional", ln=1, align="L")
        self.line(10, 27, 200, 27)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Página {self.page_no()} | Fundamento Técnico - Uso Informativo", align="C")

    def add_section_title(self, title):
        self.set_font("helvetica", "B", 12)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 10, title, ln=1, fill=True)
        self.ln(5)

    def render_insight(self, item):
        self.set_font("helvetica", "B", 10)
        self.set_text_color(0, 0, 0)
        ctx = item.get('candidatos', {}).get('username', 'Monitorado')
        self.cell(0, 8, f"ALERTA: {ctx}", ln=1)
        
        self.set_font("helvetica", "", 9)
        texto = item.get('texto_bruto', '')
        # fpdf2 lida melhor com unicode, mas sanitização básica é boa prática
        self.multi_cell(0, 5, f"Conteúdo Identificado: {texto}")
        
        status = "AGRESSIVO" if item.get('is_hate') else "NEUTRO"
        color = (220, 38, 38) if item.get('is_hate') else (37, 99, 235)
        self.set_text_color(*color)
        self.set_font("helvetica", "B", 9)
        self.cell(0, 8, f"Status: {status} | Categoria: {item.get('categoria_ia', 'N/A')}", ln=1)
        self.ln(4)

    def generate_dossie(self, data, output_path):
        self.add_page()
        self.add_section_title("RESUMO DE INTELIGÊNCIA DE CLIMA")
        
        self.set_font("helvetica", "", 10)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 10, f"Este relatório apresenta a análise de clima e tendências narrativas em ambiente digital. Total de interações analisadas: {len(data)}")
        self.ln(10)

        for item in data:
            if self.get_y() > 250:
                self.add_page()
            self.render_insight(item)

        self.output(output_path)
        return output_path
