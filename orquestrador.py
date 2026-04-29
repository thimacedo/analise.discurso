import os
import sys
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
from tools.persistence import PersistenceManager
from core.discord_alerter import send_alert

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
        # python -m scrapy crawl instagram
        process = subprocess.run(
            [sys.executable, "-m", "scrapy", "crawl", "instagram"],
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
            # Normalização para motores v18.0
            if 'texto_bruto' in df.columns:
                df = df.rename(columns={'texto_bruto': 'text'})
            if 'autor_username' in df.columns:
                df['owner_username'] = df['autor_username']
            if 'post_id' in df.columns:
                df['post_shortcode'] = df['post_id']
            if 'is_hate' in df.columns:
                df['is_hate_speech'] = df['is_hate']
            if 'categoria_ia' in df.columns:
                df['category'] = df['categoria_ia']
            return df
        else:
            print(f"❌ Erro ao buscar dados: {resp.text}")
            return None

    def process_and_mine(self, df):
        print("⛏️ [4/5] Processando NLP e Mineração de Tendências...")
        df_proc = self.tp.processar_dataframe(df)
        
        miner = DataMiner(df_proc)
        temporal_results = miner.analise_temporal()
        df_clustered, topics, clusters = miner.thematic_clustering()
        
        # Persistência Diamond Edition
        print("💾 [4.5/5] Persistindo Inteligência Forense no Supabase...")
        pm = PersistenceManager()
        pm.update_forensic_data(df_clustered)
        
        self.persist_daily_metrics(df_proc)
        self.persist_networks(clusters, df_proc)
        self.check_and_create_alerts(temporal_results, df_proc)
        
        # Gera nuvem de palavras para o relatório
        miner.gerar_nuvem_palavras()
        
        return df_clustered

    def persist_daily_metrics(self, df):
        """Salva agregações do dia na tabela metricas_diarias"""
        hoje = datetime.now().strftime('%Y-%m-%d')
        total = len(df)
        hate = df['is_hate_speech'].sum() if 'is_hate_speech' in df.columns else 0
        resiliencia = round(100 - ((hate / total) * 100), 2) if total > 0 else 100.0
        
        pasa = {}
        if 'category' in df.columns:
            pasa = df[df['is_hate_speech'] == True]['category'].value_counts().to_dict()
        
        # Mock UF breakdown (necessário dado real de geolocalização no futuro)
        uf = {"SP": int(hate * 0.4), "RJ": int(hate * 0.3), "DF": int(hate * 0.3)}
        
        payload = {
            "p_data": hoje,
            "p_total_coletado": int(total),
            "p_total_hate": int(hate),
            "p_total_neutro": int(total - hate),
            "p_resiliencia": float(resiliencia),
            "p_pasa_breakdown": pasa,
            "p_uf_breakdown": uf,
        }
        
        try:
            httpx.post(f"{SUPABASE_URL}/rest/v1/rpc/upsert_metrica_diaria", json=payload, headers=HEADERS)
            print(f"📊 Métricas diárias persistidas para {hoje}.")
        except Exception as e:
            print(f"⚠️ Erro ao persistir métricas: {e}")

    def persist_networks(self, clusters, df):
        """Salva redes coordenadas detectadas."""
        for c in clusters:
            if c['event_count'] < 3: continue
            
            severity = min(100, int((c['event_count'] / len(df)) * 1000)) if len(df) > 0 else 0
            nome = f"Rede Coordenada {c['cluster_id']} - {datetime.now().strftime('%d/%m')}"
            
            payload = {
                "nome": nome,
                "status": "ATIVA" if severity > 50 else "MONITORANDO",
                "descricao": f"Detectada rede com {len(c['alvos'])} alvos e {c['event_count']} eventos.",
                "alvos_vinculados": len(c['alvos']),
                "eventos_count": c['event_count'],
                "cluster_labels": c['alvos'],
                "palavras_chave": c['keywords'],
                "severidade": severity
            }
            try:
                httpx.post(f"{SUPABASE_URL}/rest/v1/redes_coordenadas", json=payload, headers=HEADERS)
            except Exception: pass

    def check_and_create_alerts(self, temporal_results, df):
        """Verifica picos e cria alertas."""
        for peak in temporal_results.get('peaks', []):
            severity = 'CRITICAL' if peak['z_score'] > 3.0 else 'WARNING'
            payload = {
                "severidade": severity,
                "titulo": f"Alerta de Hostilidade: {peak['data']}",
                "descricao": f"Pico detectado com Z-Score {peak['z_score']:.2f}. Volume atípico de ódio.",
                "volume_eventos": peak['event_count'],
                "z_score": peak['z_score'],
                "status": "ATIVO"
            }
            try:
                httpx.post(f"{SUPABASE_URL}/rest/v1/alertas_ativos", json=payload, headers=HEADERS)
                
                # Push Notification via Discord
                if peak['z_score'] > 3.0:
                    title = "🚨 Pico de Hostilidade Detectado!"
                    msg = (
                        f"**Data:** `{peak['data']}`\n"
                        f"**Z-Score:** `{peak['z_score']:.2f}`\n"
                        f"**Eventos:** {peak['event_count']}"
                    )
                    send_alert(title, msg, color=16711680) # Vermelho
            except Exception: pass

        # Verificação de Ameaças Físicas (Push Direto)
        if 'category' in df.columns:
            ameacas = df[df['category'] == 'AMEACA']
            for _, row in ameacas.iterrows():
                title = "⚠️ Ameaça Física Detectada!"
                autor = row.get('owner_username') or row.get('autor_username') or 'desconhecido'
                msg = f"**Alvo:** `{row.get('candidato_username', 'N/A')}`\n**Autor:** @{autor}\n**Texto:** {row['text'][:200]}..."
                send_alert(title, msg, color=16753920) # Laranja

    def generate_final_report(self, df_final):
        print("📄 [5/5] Gerando Dossiê PDF Final...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"data/reports/dossie_sentinela_{timestamp}.pdf"
        os.makedirs("data/reports", exist_ok=True)
        
        self.rg.generate_pdf(df_final, output_path)
        return output_path

    async def run_full_pipeline(self):
        print(f"\n🛡️  SENTINELA DEMOCRÁTICA - PIPELINE ATUALIZAÇÃO v19.2")
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

        # Salva para acesso via API (v19.2 Resilience)
        os.makedirs("api", exist_ok=True)
        df.to_csv("api/dados_latest.csv", index=False)
        print(f"📊 Dados exportados para api/dados_latest.csv")

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
