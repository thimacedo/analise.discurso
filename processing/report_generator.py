import os
import asyncio
from fpdf import FPDF
from datetime import datetime
from dotenv import load_dotenv
import httpx

load_dotenv()

class PDFRelatorio(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 12)
        self.cell(0, 10, 'SENTINELA - PANORAMA ESTRATÉGICO E CLIMA POLÍTICO', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()} | Análise Situacional Gerada em {datetime.now().strftime("%d/%m/%Y %H:%M")}', 0, 0, 'C')

async def fetch_insights():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    
    query = "/rest/v1/comentarios?select=*,candidatos(username)&order=data_publicacao.desc&limit=50"
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{url}{query}", headers=headers)
        return r.json() if r.status_code == 200 else []

def generate_pdf(data, output_path):
    pdf = PDFRelatorio()
    pdf.add_page()
    pdf.set_font("Helvetica", size=10)

    pdf.set_font("Helvetica", 'B', 14)
    pdf.cell(0, 10, "Resumo de Inteligência de Clima", 0, 1)
    pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(0, 10, f"Este relatório apresenta a análise de clima e tendências narrativas em ambiente digital. Total de interações analisadas: {len(data)}")
    pdf.ln(10)

    for idx, item in enumerate(data, 1):
        pdf.set_draw_color(200, 200, 200)
        pdf.set_fill_color(245, 245, 250)
        pdf.rect(pdf.get_x(), pdf.get_y(), 190, 45, 'F')
        
        pdf.set_font("Helvetica", 'B', 10)
        pdf.cell(0, 8, f"INSIGHT #{idx} - REF: {item.get('id_externo', 'ID-UNICO')}", 0, 1)
        
        pdf.set_font("Helvetica", size=9)
        pdf.cell(60, 6, f"Contexto: {item.get('candidatos', {}).get('username', 'Monitorado')}", 0)
        pdf.cell(0, 6, f"Data: {item.get('data_publicacao', 'N/A')}", 0, 1)
        
        pdf.set_font("Helvetica", 'B', 9)
        pdf.cell(0, 6, f"Fonte/Autor: @{item.get('autor_username', 'Oculto')}", 0, 1)
        
        pdf.set_font("Helvetica", 'I', 9)
        # Sanitização básica para latin-1 (limitação do FPDF padrão)
        texto = item.get('texto_bruto', '').encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 5, f"Conteúdo: {texto}")
        
        pdf.set_font("Helvetica", 'B', 9)
        agressividade = "ALTA" if item.get('is_hate') else "ESTÁVEL"
        pdf.set_text_color(245, 158, 11) if item.get('is_hate') else pdf.set_text_color(37, 99, 235)
        pdf.cell(0, 6, f"Status de Agressividade: {agressividade} ({item.get('categoria_ia', 'Analisado')})", 0, 1)
        pdf.set_text_color(0, 0, 0)
        
        pdf.ln(5)
        if pdf.get_y() > 250:
            pdf.add_page()

    pdf.output(output_path)
    print(f"Relatório estratégico gerado: {output_path}")

async def main():
    data = await fetch_insights()
    if not data:
        print("Nenhuma amostragem disponível.")
        return
    
    output_dir = "E:\\Projetos\\sentinela-sandbox-final\\data\\reports"
    os.makedirs(output_dir, exist_ok=True)
    filename = f"panorama_estrategico_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    generate_pdf(data, os.path.join(output_dir, filename))

if __name__ == "__main__":
    asyncio.run(main())
