import os
import sys
import asyncio
import subprocess
import pandas as pd
from datetime import datetime
from typing import List, Dict, Any

# Core imports
from core.config import settings
from core.db import db_client
from core.ai_service import ai_service
from core.whatsapp_alerter import send_whatsapp_summary

# Specialized processing modules
from processing.text_processor import TextProcessor
from processing.data_miner import DataMiner
from processing.report_generator import ReportGenerator
from tools.target_manager import TargetManager
import json

class Orchestrator:
    def __init__(self):
        self.tp = TextProcessor()
        self.rg = ReportGenerator()
        self.tm = TargetManager(hours_threshold=48)
        self.queue_path = os.path.join(os.getcwd(), 'data', 'priority_queue.json')

    async def run_scraper(self):
        print("🚀 [1/5] Preparando Alvos e Extração...")
        
        current_targets = []
        if os.path.exists(self.queue_path):
            try:
                with open(self.queue_path, 'r') as f:
                    current_targets = json.load(f)
            except Exception as e:
                print(f"⚠️ Erro ao ler fila: {e}")

        await self.tm.ensure_competitor_coverage()
        filtered_targets = self.tm.build_dynamic_queue(static_targets=current_targets)

        if not filtered_targets:
            print("✅ Alvos atualizados. Pulando extração.")
            return

        with open(self.queue_path, 'w') as f:
            json.dump(filtered_targets, f)

        print("🤖 Disparando scraper...")
        process = subprocess.run(
            [sys.executable, "core/instaloader_scraper.py"],
            capture_output=True, text=True
        )

        if process.returncode != 0:
            print(f"⚠️ Aviso Scraper: {process.stderr[:200]}")

    async def run_ia_classification(self):
        print("🧠 [2/5] Iniciando Perícia PASA v16.4...")
        from core.ai_service import run_batch_classification
        await run_batch_classification(limit=200)
        print("✅ Classificação concluída.")

    async def fetch_and_normalize(self) -> pd.DataFrame:
        print("📥 [3/5] Coletando dados do Supabase...")
        data = await db_client.fetch_all_data()
        if not data:
            return pd.DataFrame()
            
        df = pd.DataFrame(data)
        
        # Normalização Diamond Edition
        rename_map = {
            'texto_bruto': 'text',
            'autor_username': 'owner_username',
            'post_id': 'post_shortcode',
            'is_hate': 'is_hate_speech',
            'categoria_ia': 'category'
        }
        for old, new in rename_map.items():
            if old in df.columns:
                df[new] = df[old]
        
        return df

    async def process_and_mine(self, df: pd.DataFrame):
        print("⛏️ [4/5] NLP & Mineração de Tendências...")
        df_proc = self.tp.processar_dataframe(df)
        
        miner = DataMiner(df_proc)
        temporal_results = miner.analise_temporal()
        df_clustered, topics, clusters = miner.thematic_clustering()
        
        # Persistência de Inteligência
        await self.persist_intelligence(df_clustered, clusters, temporal_results)
        
        miner.gerar_nuvem_palavras()
        return df_clustered

    async def persist_intelligence(self, df: pd.DataFrame, clusters: List[Dict], temporal: Dict):
        print("💾 [4.5/5] Persistindo Inteligência Forense...")
        
        # 1. Atualiza IDs de Cluster nos comentários (Se houver)
        if 'cluster' in df.columns:
            updates = []
            for _, row in df.iterrows():
                if pd.notna(row['cluster']):
                    updates.append({
                        "id": row['id'],
                        "cluster_id": int(row['cluster'])
                    })
            if updates:
                await db_client.batch_update_comments(updates)
                print(f"🔗 {len(updates)} comentários vinculados a clusters.")

        # 2. Métricas Diárias
        hoje = datetime.now().strftime('%Y-%m-%d')
        total = len(df)
        hate = df['is_hate_speech'].sum() if 'is_hate_speech' in df.columns else 0
        resiliencia = round(100 - ((hate / total) * 100), 2) if total > 0 else 100.0
        
        pasa = df[df['is_hate_speech'] == True]['category'].value_counts().to_dict() if 'category' in df.columns else {}
        
        await db_client.upsert_daily_metrics({
            "p_data": hoje,
            "p_total_coletado": int(total),
            "p_total_hate": int(hate),
            "p_total_neutro": int(total - hate),
            "p_resiliencia": float(resiliencia),
            "p_pasa_breakdown": pasa,
            "p_uf_breakdown": {"SP": int(hate*0.4), "RJ": int(hate*0.3), "DF": int(hate*0.3)} # Placeholder
        })

        # 3. Redes Coordenadas
        for c in clusters:
            if c['event_count'] < 3: continue
            severity = min(100, int((c['event_count'] / len(df)) * 1000)) if len(df) > 0 else 0
            await db_client.persist_coordinated_network({
                "nome": f"Rede {c['cluster_id']} - {datetime.now().strftime('%d/%m')}",
                "status": "ATIVA" if severity > 50 else "MONITORANDO",
                "eventos_count": c['event_count'],
                "severidade": severity,
                "palavras_chave": c['keywords']
            })

    async def run_full_pipeline(self):
        print(f"\n🛡️ SENTINELA DEMOCRÁTICA - PIPELINE v{settings.VERSION}")
        print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n" + "="*50)
        
        await self.run_scraper()
        await self.run_ia_classification()
        
        df = await self.fetch_and_normalize()
        if df.empty:
            print("🛑 Pipeline interrompida: Sem dados.")
            return

        # Export para API legacy support
        os.makedirs("api", exist_ok=True)
        df.to_csv("api/dados_latest.csv", index=False)

        df_final = await self.process_and_mine(df)
        
        # Relatório PDF
        output_path = f"data/reports/dossie_sentinela_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        os.makedirs("data/reports", exist_ok=True)
        self.rg.generate_pdf(df_final, output_path)

        # Resumo WhatsApp
        total_odio = df_final['is_hate_speech'].sum() if 'is_hate_speech' in df_final.columns else 0
        resumo = f"📊 *Relatório Sentinela*\nComentários: {len(df_final)}\nHostilidade: {total_odio} detectados\nVersão: {settings.VERSION}"
        send_whatsapp_summary(resumo)
        
        print("\n" + "="*50)
        print(f"✨ PIPELINE FINALIZADA! Relatório: {output_path}\n")

if __name__ == "__main__":
    orchestrator = Orchestrator()
    asyncio.run(orchestrator.run_full_pipeline())
