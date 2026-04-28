import sqlite3
import httpx
import os
import asyncio
import json
import logging
from datetime import datetime
from dotenv import load_dotenv

# Configuração de Logs
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.FileHandler('logs/intelligence.log'), logging.StreamHandler()]
)

load_dotenv()

DB_PATH = "E:/projetos/sentinela-democratica/data/odio_politica.db"
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
MODEL_TRIAGE = "qwen2.5:3b"
MODEL_EXPERT = "gemma:2b"

class IntelligenceWorker:
    """
    Worker de Inteligência Forense v16.4.2
    Utiliza: MANUAL_TECNICO_PASA_v16_3.md e ADENDO_LINGUISTICA_PROFUNDA.md
    """
    def __init__(self):
        self.version = "16.4.2"

    async def call_ollama(self, model, prompt, system_rules):
        payload = {
            "model": model,
            "prompt": f"DIRETRIZES_SISTEMA: {system_rules}\n\nENTRADA_TEXTUAL: '{prompt}'",
            "stream": False,
            "format": "json"
        }
        async with httpx.AsyncClient(timeout=90.0) as client:
            try:
                res = await client.post(OLLAMA_URL, json=payload)
                if res.status_code == 200:
                    return json.loads(res.json().get("response", "{}"))
            except Exception as e:
                logging.error(f"Erro no modelo {model}: {e}")
        return None

    async def analyze(self, text):
        # CAMADA 1: TRIAGEM (Manual Técnico PASA v16.3)
        system_triage = (
            "Aja como Triador Forense. Use a Taxonomia MTAD v16.3: "
            "XENOFOBIA_REGIONAL, RACISMO_RELIGIOSO, VIOLÊNCIA_GÊNERO, MILICIA_DIGITAL, RACISMO_ESTRUTURAL. "
            "Identifique se 'is_hate' é true. Se houver dúvida ou agressão, 'needs_expert' deve ser true."
        )
        triage = await self.call_ollama(MODEL_TRIAGE, text, system_triage)

        if not triage or (not triage.get('is_hate') and not triage.get('needs_expert')):
            return triage or {"is_hate": False, "categoria": "NEUTRO"}

        # CAMADA 2: PERITAGEM (Adendo de Linguística Profunda v16.3.1)
        logging.info(f"🔍 [EXPERT] Ativando Gemma para Peritagem Profunda.")
        system_expert = (
            "Aja como Perito Sênior (Método Bakhtin/Othon Garcia). "
            "1. Analise a performatividade: o texto anula a cidadania do alvo? "
            "2. Identifique Falácias: Ad Hominem, Espantalho, Falsa Dicotomia. "
            "3. Avalie o Vetor de Fúria (BAIXO, MÉDIO, ALTO). "
            "Retorne JSON: {'is_hate': bool, 'categoria': 'string', 'risco': 'string', 'falacia': 'string', 'analise_pericial': 'string'}"
        )
        expert = await self.call_ollama(MODEL_EXPERT, text, system_expert)
        return expert if (expert and 'categoria' in expert) else triage

    async def run(self):
        logging.info(f"🚀 Sentinela Intelligence v{self.version} Ativa e Sincronizada com Base Documental.")
        while True:
            try:
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("SELECT id, texto_bruto FROM comentarios WHERE processado_ia = 0 LIMIT 10")
                rows = c.fetchall()
                if not rows:
                    conn.close()
                    await asyncio.sleep(10)
                    continue

                for rid, texto in rows:
                    res = await self.analyze(texto)
                    c.execute("""
                        UPDATE comentarios SET 
                        processado_ia = 1, is_hate = ?, categoria_ia = ?, 
                        analise_pericial = ?, data_processamento = ? 
                        WHERE id = ?
                    """, (
                        1 if res.get('is_hate') else 0, 
                        res.get('categoria', 'NEUTRO'), 
                        res.get('analise_pericial', res.get('falacia', 'N/A')), 
                        datetime.now().isoformat(), rid
                    ))
                conn.commit()
                conn.close()
                logging.info(f"✅ Lote de {len(rows)} vereditos processado.")
            except Exception as e:
                logging.error(f"Erro no ciclo: {e}")
                await asyncio.sleep(5)

if __name__ == '__main__':
    asyncio.run(IntelligenceWorker().run())
