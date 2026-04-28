import os
import asyncio
import subprocess
import pandas as pd
import httpx
from datetime import datetime
from dotenv import load_dotenv

# Importações dos módulos unificados v18.0
from processing.text_processor import TextProcessor
from processing.data_miner import DataMiner
from processing.report_generator import ReportGenerator
from core.qwen_classifier import run_integrated_qwen_classification

load_dotenv()

# Configurações Supabase (Direct API Access)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

class Orchestrator:
    def __init__(self):
        self.tp = TextProcessor()
        self.rg = ReportGenerator()

    async def run_scraper(self):
        print("🚀 [1/5] Iniciando Extração Scrapy (Instagram)...")
        # scrapy crawl instagram
        process = subprocess.run(
            ["scrapy", "crawl", "instagram"],
            capture_output=True, text=True, shell=True
        )
        if process.returncode == 0:
            print("✅ Extração concluída.")
        else:
            print(f"⚠️ Aviso no Scraper: {process.stderr[:200]}")

    def run_ia_classification(self):
        print("🧠 [2/5] Iniciando Classificação PASA (IA Qwen/Groq)...")
        run_integrated_qwen_classification()
        print("✅ Classificação concluída.")

    def fetch_data(self):
        print("📥 [3/5] Coletando dados processados do Supabase...")
        url = f"{SUPABASE_URL}/rest/v1/comentarios?select=*"
        resp = httpx.get(url, headers=HEADERS)
        if resp.status_code == 200:
            df = pd.DataFrame(resp.json())
            # Normalização de nomes de colunas
            if 'texto_bruto' in df.columns:
                df = df.rename(columns={'texto_bruto': 'text'})
            return df
        else:
            print(f"❌ Erro ao buscar dados: {resp.text}")
            return None

    def process_and_mine(self, df):
        print("⛏️ [4/5] Processando NLP e Mineração de Tendências...")
        df_proc = self.tp.processar_dataframe(df)
        
        miner = DataMiner(df_proc)
        peak_data = miner.analise_temporal()
        df_clustered, topics = miner.thematic_clustering()
        
        # Gera nuvem de palavras para o relatório
        miner.gerar_nuvem_palavras()
        
        return df_clustered

    def generate_final_report(self, df_final):
        print("📄 [5/5] Gerando Dossiê PDF Final...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"data/reports/dossie_sentinela_{timestamp}.pdf"
        os.makedirs("data/reports", exist_ok=True)
        
        self.rg.generate_pdf(df_final, output_path)
        return output_path

    async def run_full_pipeline(self):
        print(f"\n🛡️  SENTINELA DEMOCRÁTICA - PIPELINE ATUALIZAÇÃO v18.5")
        print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n" + "="*50)
        
        # 1. Scraper
        await self.run_scraper()
        
        # 2. IA Classification
        self.run_ia_classification()
        
        # 3. Fetch
        df = self.fetch_data()
        if df is None or df.empty:
            print("🛑 Pipeline interrompida: Sem dados novos.")
            return

        # 4. NLP & Mining
        df_final = self.process_and_mine(df)
        
        # 5. Report
        report_path = self.generate_final_report(df_final)
        
        print("\n" + "="*50)
        print(f"✨ PIPELINE FINALIZADA COM SUCESSO!")
        print(f"📊 Total Processado: {len(df_final)} comentários.")
        print(f"📁 Relatório: {report_path}\n")

if __name__ == "__main__":
    orchestrator = Orchestrator()
    asyncio.run(orchestrator.run_full_pipeline())
