import os
import sys
import asyncio
import json
import pandas as pd
from datetime import datetime, UTC
from typing import List, Dict, Any

from core.config import settings
from core.db import db_client
from core.ai_service import ai_service
from core.predictive_service import predictive_service
from core.firebase_alerter import send_alert_summary
from core.instagram_headless import InstagramHeadlessScraper
from core.meta_ad_service import meta_ad_service
from processing.text_processor import clean_comment
from processing.data_miner import data_miner
from processing.report_generator import ReportGenerator
from processing.ad_processor import ad_processor
from tools.target_manager import TargetManager
from workers.processors.queue_manager import QueueManagerWorker

class Orchestrator:
    def __init__(self):
        self.rg = ReportGenerator()
        self.tm = TargetManager(hours_threshold=48)
        self.batch_size = 200
        self.error_counts = {} # Rastreia erros repetidos para evitar loops infinitos

    async def run_scraper(self, limit=200, cooldown=300):
        print(f"🚀 [1/5] Preparando Extração - Limite: {limit}...")
        
        qm = QueueManagerWorker()
        qm.batch_size = limit 
        await qm.execute()

        today = datetime.now(UTC).date().isoformat()
        res = db_client.client.table('fila_coleta')\
            .select('candidato_id')\
            .eq('data_agendada', today)\
            .eq('status', 'PENDENTE')\
            .order('prioridade', desc=True)\
            .limit(limit)\
            .execute()
        
        targets = [item['candidato_id'] for item in res.data]
        if not targets:
            print("✅ Fila central de hoje já processada.")
            return

        print(f"🤖 Iniciando Coleta para {len(targets)} alvos...")
        scraper = InstagramHeadlessScraper()
        
        for i, target in enumerate(targets):
            print(f"\n🎯 [{i+1}/{len(targets)}] @{target}...")
            try:
                await scraper.run(targets=[target])
                if i < len(targets) - 1:
                    await ai_service.run_batch_classification(limit=50, force_retry_failures=True)
                    await ai_service.run_batch_classification(limit=100)
                    await asyncio.sleep(max(0, cooldown - 60))
            except Exception as e:
                print(f"❌ Erro @{target}: {e}")

    async def run_ia_classification(self):
        print("🧠 [2/5] Perícia PASA v16.4...")
        await ai_service.run_batch_classification(limit=200)

    async def run_repericia_cycle(self):
        targets = await db_client.fetch_targets_needing_repericia()
        if not targets: return
        print(f"🕵️‍♂️ Re-perícia: {', '.join(targets)}")
        for username in targets:
            await db_client.reset_target_comments(username)
            await db_client.mark_repericia_complete(username)

    async def run_meta_ads_cycle(self):
        print("📢 [1.7/5] META AD LIBRARY...")
        try:
            with open("data/priority_queue.json", "r") as f:
                targets = json.load(f)
        except:
            targets = []

        if not targets: return
        for target in targets[:5]:
            ads = await meta_ad_service.search_ads(target)
            if ads: await db_client.persist_ads_batch(ads)
        
        await ad_processor.run_once(limit=10)

    async def fetch_and_normalize(self) -> pd.DataFrame:
        data = await db_client.fetch_all_data()
        if not data: return pd.DataFrame()
            
        df = pd.DataFrame(data)
        rename_map = {
            'texto_bruto': 'text',
            'autor_username': 'owner_username',
            'post_id': 'post_shortcode',
            'is_hate': 'is_hate_speech',
            'categoria_ia': 'category'
        }
        for old, new in rename_map.items():
            if old in df.columns: df[new] = df[old]
        return df

    async def process_and_mine(self, df: pd.DataFrame):
        print("⛏️ [4/5] NLP & Mineração...")
        await data_miner.run_once(limit=self.batch_size)
        df['text'] = df.apply(lambda row: clean_comment(row['text'], row['owner_username']), axis=1)
        df.dropna(subset=['text'], inplace=True)
        return df

    async def persist_intelligence(self, df: pd.DataFrame, clusters: List[Dict]):
        if 'cluster' in df.columns:
            updates = [{"id": row['id'], "cluster_id": int(row['cluster'])} 
                       for _, row in df.iterrows() if pd.notna(row['cluster'])]
            if updates: await db_client.batch_update_comments(updates)

        hoje, total = datetime.now().strftime('%Y-%m-%d'), len(df)
        hate = df['is_hate_speech'].sum() if 'is_hate_speech' in df.columns else 0
        critical = df[df['is_hate_speech'] == True]['category'].isin(['CRITICAL', 'SEVERE']).sum() if 'category' in df.columns else 0
        res = round(100 - ((hate / total) * 100), 2) if total > 0 else 100.0
        pasa = df[df['is_hate_speech'] == True]['category'].value_counts().to_dict() if 'category' in df.columns else {}
        
        print(f"🏆 [PSR-1] { (total * 1) + (critical * 5) } pts.")
        await db_client.upsert_daily_metrics({"p_data": hoje, "p_total_coletado": int(total), "p_total_hate": int(hate), "p_total_neutro": int(total - hate), "p_resiliencia": float(res), "p_pasa_breakdown": pasa})

        for c in clusters:
            if c['event_count'] < 3: continue
            severity = min(100, int((c['event_count'] / len(df)) * 1000)) if len(df) > 0 else 0
            await db_client.persist_coordinated_network({"nome": f"Rede {c['cluster_id']} - {datetime.now().strftime('%d/%m')}", "status": "ATIVA" if severity > 50 else "MONITORANDO", "eventos_count": c['event_count'], "severidade": severity, "palavras_chave": c['keywords']})

    async def run_predictive_cycle(self):
        try:
            status = await predictive_service.analyze_trends(days=7)
            if status.get('is_anomaly'): print(f"⚠️ ANOMALIA: {status['trend']}")
        except Exception as e: print(f"⚠️ Erro Preditivo: {e}")

    async def run_full_pipeline(self):
        print(f"🛡️ SENTINELA v{settings.VERSION} | AI: {settings.IA_PROVIDER}")
        
        stages = [
            ("Scraper", self.run_scraper),
            ("Repericia Cycle", self.run_repericia_cycle),
            ("Meta Ads Cycle", self.run_meta_ads_cycle),
            ("IA Classification", self.run_ia_classification),
            ("Predictive Cycle", self.run_predictive_cycle),
        ]
        
        for stage_name, stage_func in stages:
            try:
                print(f"🚀 Iniciando estágio: {stage_name}...")
                await stage_func()
            except Exception as e:
                error_type = type(e).__name__
                self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
                
                print(f"❌ ERRO REPETIDO ({self.error_counts[error_type]}/3) no estágio '{stage_name}': {error_type} - {e}")
                
                if self.error_counts[error_type] >= 3:
                    print(f"💥 ERRO CRÍTICO: O erro '{error_type}' ocorreu 3 vezes. Finalizando o processo.")
                    sys.exit(1) # Termina o script
                else:
                    print(f"⚠️ Continuando após erro em '{stage_name}'.") # Informa que continuará

        
        df = await self.fetch_and_normalize()
        if df.empty: return

        os.makedirs("api", exist_ok=True)
        df.to_csv("api/dados_latest.csv", index=False)
        df_final = await self.process_and_mine(df)
        
        path = f"data/reports/dossie_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        os.makedirs("data/reports", exist_ok=True)
        self.rg.generate_pdf(df_final, path)

        total_odio = df_final['is_hate_speech'].sum() if 'is_hate_speech' in df_final.columns else 0
        send_alert_summary(f"📊 Alertas: {total_odio} | v{settings.VERSION}")
        print(f"✨ FINALIZADA: {path}")

if __name__ == "__main__":
    asyncio.run(Orchestrator().run_full_pipeline())
