import os
import re
import asyncio
from datetime import datetime
from supabase import create_client, Client
from pysentimiento import create_analyzer
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Sentinela-Intelligence")

# --- CONFIGURAÇÕES ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
BATCH_SIZE = 50 # Reduzido para estabilidade em 2GB RAM

if not all([SUPABASE_URL, SUPABASE_KEY]):
    logger.error("Variaveis de ambiente nao configuradas.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- MODELOS NLP ---
logger.info("Carregando modelos PASA (BERTimbau)...")
try:
    hate_analyzer = create_analyzer(task="hate_speech", lang="pt")
    sentiment_analyzer = create_analyzer(task="sentiment", lang="pt")
    MODELO_VERSAO = "pysentimiento_v0.3_diamond"
except Exception as e:
    logger.error(f"Falha ao carregar modelos: {e}")
    exit(1)

def limpar_texto(texto: str) -> str:
    if not texto: return ""
    texto = re.sub(r'http\S+|www\S+|https\S+', '', texto, flags=re.MULTILINE)
    texto = re.sub(r'@\w+', '', texto)
    texto = re.sub(r'[^\w\s]', '', texto)
    return texto.strip()

def classificar_comentario(texto_bruto: str) -> dict:
    texto_limpo = limpar_texto(texto_bruto)
    
    if not texto_limpo or len(texto_limpo.split()) < 3:
        return {"texto_limpo": texto_limpo, "is_hate": False, "categoria": "NEUTRO", "score": 0.0, "sent": "NEU"}

    # Analise de Hostilidade PASA
    hate_result = hate_analyzer.predict(texto_limpo)
    is_hate = hate_result.output == "HATE"
    
    # Mapeamento de categorias PASA (Simplificado via Probas)
    categorias = [k for k, v in hate_result.probas.items() if v > 0.3 and k != "hate"]
    categoria_pasa = categorias[0].upper() if categorias else "GENERAL_HATE"
    score_hate = hate_result.probas.get("HATE", 0.0)

    # Analise de Sentimento
    sent_result = sentiment_analyzer.predict(texto_limpo)
    
    return {
        "texto_limpo": texto_limpo,
        "is_hate": is_hate,
        "categoria": categoria_pasa if is_hate else "NEUTRO",
        "score": round(score_hate, 4),
        "sent": sent_result.output.upper()
    }

async def process_batch():
    logger.info("Buscando backlog para classificacao...")
    
    res = supabase.table('comentarios') \
        .select('id, texto_bruto') \
        .eq('processado_ia', False) \
        .limit(BATCH_SIZE) \
        .execute()
    
    comments = res.data
    if not comments:
        logger.info("Backlog limpo. Aguardando novos dados.")
        return False

    update_payload = []
    class_payload = []

    for c in comments:
        result = classificar_comentario(c['texto_bruto'])
        
        update_payload.append({
            "id": c['id'],
            "texto_limpo": result["texto_limpo"],
            "processado_ia": True,
            "sentimento": result["sent"]
        })
        
        class_payload.append({
            "comentario_id": c['id'],
            "is_hate": result["is_hate"],
            "categoria_pasa": result["categoria"],
            "score": result["score"],
            "modelo_versao": MODELO_VERSAO
        })

    try:
        # Bulk Upsert
        supabase.table('comentarios').upsert(update_payload, on_conflict="id").execute()
        supabase.table('classificacoes').upsert(class_payload, on_conflict="comentario_id").execute()
        logger.info(f"[✓] Lote de {len(comments)} registros processado via PASA v15.19.")
        return True
    except Exception as e:
        logger.error(f"Erro ao salvar lote: {e}")
        return False

async def main():
    logger.info("Iniciando Intelligence Worker Diamond v15.19")
    while True:
        has_more = await process_batch()
        if not has_more:
            await asyncio.sleep(60) # Espera 1 min se o banco estiver vazio
        else:
            await asyncio.sleep(2) # Pausa leve entre lotes

if __name__ == "__main__":
    asyncio.run(main())
