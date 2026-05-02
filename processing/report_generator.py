import os
from fpdf import FPDF
from datetime import datetime
import pandas as pd
import re

class ReportGenerator(FPDF):
    def __init__(self):
        super().__init__()
        # Tenta carregar fonte com suporte estendido
        self.font_family_main = 'Helvetica'
        try:
            # Em ambientes Windows, tentamos usar Arial para melhor suporte
            if os.path.exists('C:\\Windows\\Fonts\\arial.ttf'):
                self.add_font('ArialCustom', '', 'C:\\Windows\\Fonts\\arial.ttf')
                self.add_font('ArialCustom', 'B', 'C:\\Windows\\Fonts\\arialbd.ttf')
                self.font_family_main = 'ArialCustom'
        except Exception as e:
            print(f"⚠️ Aviso ao carregar fontes: {e}")

    def clean_text(self, text):
        """Remove caracteres que causam quebra no FPDF (emojis, etc)"""
        if not text: return ""
        # Mantém apenas caracteres básicos e acentuação comum
        return re.sub(r'[^\x00-\x7Fà-úÀ-Ú]', ' ', str(text))

    def header(self):
        self.set_font(self.font_family_main, 'B', 14)
        self.set_text_color(37, 99, 235)
        self.cell(0, 10, 'SENTINELA DEMOCRÁTICA - DOSSIÊ INTELIGÊNCIA', align="C")
        self.ln(10)
        self.set_draw_color(37, 99, 235)
        self.line(10, 20, 200, 20)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font(self.font_family_main, '', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Página {self.page_no()} | Gerado em {datetime.now().strftime("%d/%m/%Y %H:%M")}', align='C')

    def render_item(self, item):
        if self.get_y() > 240: # Margem de segurança
            self.add_page()

        self.set_fill_color(245, 245, 250)
        self.rect(10, self.get_y(), 190, 35, 'F')
        
        autor = self.clean_text(item.get('owner_username') or item.get('autor_username') or 'Desconhecido')
        post_ref = self.clean_text(item.get('post_shortcode') or item.get('post_id') or 'N/A')
        
        self.set_font(self.font_family_main, 'B', 9)
        self.set_text_color(0, 0, 0)
        self.cell(0, 6, f'Autor: @{autor} | Post: {post_ref}')
        self.ln(6)

        texto_original = item.get('text', '')
        texto = self.clean_text(texto_original[:300]) + ("..." if len(texto_original) > 300 else "")
        self.set_font(self.font_family_main, '', 8)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5, f"Conteúdo: {texto}")

        # LÓGICA PASA BASEADA NA IA (Diamond v19.2.8)
        is_hate = bool(item.get('is_hate_speech') or item.get('is_hate', False))
        categoria = item.get('category') or item.get('categoria_ia') or 'NEUTRO'
        
        if is_hate:
            status = f"HOSTIL / {categoria.upper()}"
            cor = (220, 38, 38) # Vermelho
        else:
            status = "NEUTRO / NÃO HOSTIL"
            cor = (37, 99, 235) # Azul
        
        self.set_font(self.font_family_main, 'B', 8)
        self.set_text_color(*cor)
        self.cell(0, 6, f"Status: {status}")
        self.ln(10)

    def render_forensic_integrity(self, df):
        self.add_page()
        self.set_font(self.font_family_main, 'B', 12)
        self.set_text_color(37, 99, 235)
        self.cell(0, 10, 'INTEGRIDADE DE DADOS E RASTREABILIDADE', ln=True)
        self.ln(5)
        
        self.set_font(self.font_family_main, '', 9)
        self.set_text_color(0, 0, 0)
        
        import hashlib
        # Gera hash dos dados processados
        data_str = df.to_json()
        data_hash = hashlib.sha256(data_str.encode()).hexdigest()
        
        self.multi_cell(0, 6, self.clean_text(f"Este documento foi gerado pelo sistema Sentinela Democrática utilizando o Protocolo PASA v16.4. Os dados contidos neste relatório possuem integridade verificável através do hash SHA-256 abaixo:"))
        self.ln(2)
        
        self.set_font(self.font_family_main, 'B', 8)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 8, f" SHA-256: {data_hash} ", border=1, ln=True, fill=True)
        self.ln(10)
        
        self.set_font(self.font_family_main, '', 9)
        self.multi_cell(0, 6, self.clean_text("Certificação de Origem:\nOrquestrador Sentinela Diamond v20.5\nID de Sessão Informativa: " + hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:8].upper()))
        
        # Placeholder para assinatura
        self.ln(20)
        self.line(10, self.get_y(), 80, self.get_y())
        self.set_font(self.font_family_main, 'I', 7)
        self.cell(0, 5, 'Validado por Sentinela AI - Núcleo de Processamento de Dados')

    def generate_pdf(self, df_final, output_path):
        if df_final is None or df_final.empty:
            print("⚠️ DataFrame vazio. Nenhum PDF gerado.")
            return None

        self.add_page()
        self.set_font(self.font_family_main, '', 10)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 8, self.clean_text(f"Análise situacional contendo {len(df_final)} interações mapeadas."))
        self.ln(5)

        # Prioriza ódio para o relatório, mas mantém fallback se vazio
        df_report = df_final[df_final['is_hate_speech'] == True].head(100)
        if df_report.empty:
            df_report = df_final.head(10)

        for _, row in df_report.iterrows():
            self.render_item(row.to_dict())

        # Adiciona seção de integridade
        self.render_forensic_integrity(df_final)

        self.output(output_path)
        print(f"📄 Relatório salvo em: {output_path}")
        return output_path
