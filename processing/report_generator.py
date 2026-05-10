import os
import hashlib
import re
import pandas as pd
from fpdf import FPDF
from datetime import datetime
from processing.visual_engine import visual_engine

class ReportGenerator(FPDF):
    """
    Gerador de relatórios PDF de alto desempenho (Diamond Edition).
    Produz dossiês executivos com visualizações integradas e integridade forense.
    """
    
    def __init__(self):
        super().__init__()
        self.font_family_main = 'Helvetica'
        self._setup_fonts()
        self.primary_color = (37, 99, 235) # Royal Blue

    def _setup_fonts(self):
        """Configura fontes padrão do sistema com suporte a acentuação."""
        try:
            if os.path.exists('C:\\Windows\\Fonts\\arial.ttf'):
                self.add_font('Arial', '', 'C:\\Windows\\Fonts\\arial.ttf')
                self.add_font('Arial', 'B', 'C:\\Windows\\Fonts\\arialbd.ttf')
                self.font_family_main = 'Arial'
        except:
            pass

    def clean_text(self, text):
        if not text: return ""
        # Remove caracteres não compatíveis com Latin-1 do FPDF (emojis, etc)
        return re.sub(r'[^\x00-\xFF]', ' ', str(text))

    def header(self):
        if self.page_no() > 1:
            self.set_font(self.font_family_main, 'B', 8)
            self.set_text_color(150, 150, 150)
            self.cell(0, 10, 'SENTINELA DEMOCRÁTICA | CONFIDENCIAL', align="L")
            self.cell(0, 10, f'ID: {datetime.now().strftime("%Y%m%d")}', align="R")
            self.ln(10)

    def footer(self):
        self.set_y(-20)
        self.set_font(self.font_family_main, 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Página {self.page_no()} | Protocolo PASA v16.4', align='C', ln=True)
        
        # Motor de Viralidade B2B
        self.set_font(self.font_family_main, '', 9)
        self.set_text_color(160, 160, 160)
        self.cell(0, 5, "Gerado por Inteligência Estratégica - Sentinela Democrática. Proteja a sua campanha em sentinelademocratica.com", align='C')

    def render_cover(self, candidato_id, total_amostra):
        """Cria uma capa profissional para o relatório."""
        self.add_page()
        
        # Logo placeholder / Linha decorativa
        self.set_fill_color(*self.primary_color)
        self.rect(0, 0, 210, 40, 'F')
        
        self.set_y(50)
        self.set_font(self.font_family_main, 'B', 28)
        self.set_text_color(30, 41, 59)
        self.cell(0, 20, 'DOSSIÊ DE INTELIGÊNCIA', ln=True, align='C')
        
        self.set_font(self.font_family_main, '', 16)
        self.cell(0, 10, f'Monitoramento Situacional: @{candidato_id}', ln=True, align='C')
        
        self.ln(60)
        self.set_font(self.font_family_main, 'B', 12)
        self.cell(0, 10, 'SUMÁRIO EXECUTIVO', ln=True)
        self.set_font(self.font_family_main, '', 11)
        self.multi_cell(0, 7, (
            f"Este documento apresenta a análise técnica de hostilidade e detecção de ataques coordenados "
            f"baseada em uma amostra de {total_amostra} interações coletadas. "
            f"A classificação segue o Protocolo PASA v16.4 com validação por Inteligência Artificial."
        ))
        
        self.set_y(-60)
        self.set_font(self.font_family_main, 'B', 10)
        self.cell(0, 10, f"DATA DE EMISSÃO: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align='C')
        self.set_font(self.font_family_main, '', 9)
        self.cell(0, 5, "SISTEMA SENTINELA DEMOCRÁTICA - DIAMOND EDITION", align='C')

    def render_analytics_page(self, df):
        """Página com gráficos estatísticos."""
        self.add_page()
        self.set_font(self.font_family_main, 'B', 14)
        self.set_text_color(*self.primary_color)
        self.cell(0, 10, 'ANÁLISE ESTATÍSTICA E TENDÊNCIAS', ln=True)
        self.ln(5)

        # Gráfico 1: Breakdown PASA
        path_pasa = visual_engine.generate_pasa_breakdown(df)
        if path_pasa and os.path.exists(path_pasa):
            self.image(path_pasa, x=15, w=180)
            self.ln(10)

        # Gráfico 2: Tendência Temporal
        path_trend = visual_engine.generate_temporal_trend(df)
        if path_trend and os.path.exists(path_trend):
            self.image(path_trend, x=10, w=190)

    def render_evidence_item(self, item):
        """Renderiza um card de evidência detalhado."""
        if self.get_y() > 230:
            self.add_page()

        # Borda e fundo do card
        current_y = self.get_y()
        self.set_fill_color(248, 250, 252)
        self.rect(10, current_y, 190, 45, 'F')
        self.set_draw_color(226, 232, 240)
        self.rect(10, current_y, 190, 45, 'D')

        # Header do card
        self.set_xy(15, current_y + 5)
        self.set_font(self.font_family_main, 'B', 10)
        self.set_text_color(30, 41, 59)
        autor = self.clean_text(item.get('owner_username') or item.get('autor_username', 'Oculto'))
        self.cell(0, 5, f"FONTE: @{autor} | PLATAFORMA: {item.get('plataforma', 'N/A').upper()}")
        
        # Categoria Badge
        cat = (item.get('category') or item.get('categoria_ia') or 'NEUTRO').upper()
        is_hate = bool(item.get('is_hate_speech') or item.get('is_hate', False))
        
        self.set_xy(150, current_y + 5)
        if is_hate:
            self.set_text_color(220, 38, 38)
            self.cell(40, 5, f"[ {cat} ]", align='R')
        else:
            self.set_text_color(37, 99, 235)
            self.cell(40, 5, "[ NEUTRO ]", align='R')

        # Conteúdo
        self.set_xy(15, current_y + 12)
        self.set_font(self.font_family_main, '', 9)
        self.set_text_color(71, 85, 105)
        texto = self.clean_text(item.get('text', ''))
        self.multi_cell(180, 5, f"CONTEÚDO: {texto[:280]}...")
        
        # Footer do card (Data)
        self.set_xy(15, current_y + 35)
        self.set_font(self.font_family_main, 'I', 8)
        self.set_text_color(148, 163, 184)
        data = item.get('data_coleta') or 'N/A'
        self.cell(0, 5, f"Coletado em: {data}")
        
        self.set_y(current_y + 55)

    def render_integrity_seal(self, df):
        """Selo de integridade forense."""
        self.add_page()
        self.set_y(100)
        self.set_font(self.font_family_main, 'B', 12)
        self.set_text_color(*self.primary_color)
        self.cell(0, 10, 'CERTIFICAÇÃO DE INTEGRIDADE DOS DADOS', ln=True, align='C')
        
        data_str = df.to_json()
        data_hash = hashlib.sha256(data_str.encode()).hexdigest()
        
        self.set_font(self.font_family_main, '', 9)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 6, (
            "Este dossiê foi gerado automaticamente pelo Orquestrador Sentinela Diamond. "
            "A integridade dos dados brutos e processados é garantida pela assinatura criptográfica abaixo. "
            "Qualquer alteração no conteúdo invalidará este hash."
        ), align='C')
        
        self.ln(10)
        self.set_font(self.font_family_main, 'B', 8)
        self.set_fill_color(241, 245, 249)
        self.cell(0, 10, f"SHA-256: {data_hash}", border=1, ln=True, align='C', fill=True)

    def generate_pdf(self, df_final, output_path):
        if df_final is None or df_final.empty:
            return None

        candidato = df_final['candidato_id'].iloc[0] if 'candidato_id' in df_final.columns else "Geral"
        
        # 1. Capa
        self.render_cover(candidato, len(df_final))
        
        # 2. Analytics
        self.render_analytics_page(df_final)
        
        # 3. Evidências (Top 50 hostis)
        self.add_page()
        self.set_font(self.font_family_main, 'B', 14)
        self.set_text_color(*self.primary_color)
        self.cell(0, 10, 'DETALHAMENTO DE EVIDÊNCIAS (TOP SINAIS)', ln=True)
        self.ln(5)
        
        is_hate_col = 'is_hate_speech' if 'is_hate_speech' in df_final.columns else 'is_hate'
        df_report = df_final[df_final[is_hate_col] == True].head(50) if is_hate_col in df_final.columns else df_final.head(10)
        
        if df_report.empty:
            df_report = df_final.head(10)

        for _, row in df_report.iterrows():
            self.render_evidence_item(row.to_dict())

        # 4. Selo de Integridade
        self.render_integrity_seal(df_final)

        self.output(output_path)
        print(f"📄 Dossiê executivo gerado: {output_path}")
        return output_path
