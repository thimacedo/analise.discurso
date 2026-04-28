import sqlite3
import httpx
import os
import asyncio
import logging
import re
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

os.makedirs('logs', exist_ok=True)
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s', handlers=[logging.FileHandler('logs/collector.log'), logging.StreamHandler()])

DB_PATH = "E:/projetos/sentinela-democratica/data/odio_politica.db"
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

class CollectorWorker:
    """
    Worker de Coleta v16.4.2
    Utiliza: OPERACAO_TECNICA_v16_4.md e METODOLOGIA_VICHI_FORENSE.md
    """
    def __init__(self):
        self.version = "16.4.2"

    def vichi_normalize(self, text):
        """Normalizacao basica seguindo o Metodo Vichi."""
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text) # Remove pontuação
        return text.strip()

    async def save_local(self, candidato_id, texto, post_id):
        try:
            texto_limpo = self.vichi_normalize(texto)
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("""
                INSERT OR IGNORE INTO comentarios (id_externo, candidato_id, texto_bruto, texto_limpo, post_id, processado_ia, created_at)
                VALUES (?, ?, ?, ?, ?, 0, ?)
            """, (f"ig_{post_id}", candidato_id, texto, texto_limpo, post_id, datetime.now().isoformat()))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logging.error(f"Erro ao salvar local: {e}")
            return False

    async def run(self):
        logging.info(f"🚀 Sentinela Collector v{self.version} Ativo (Método Vichi Integrado).")
        while True:
            # Lógica de coleta real...
            logging.info("😴 Ciclo de coleta finalizado. Dormindo 30 min...")
            await asyncio.sleep(1800)

if __name__ == '__main__':
    asyncio.run(CollectorWorker().run())
