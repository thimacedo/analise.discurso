"""
PASA v44 - Audit Worker: Verificação Cruzada Anti-Alucinação
Reclassifica amostras de alta confiança usando Groq (Llama 3) para detectar divergências.
"""
import os
import random
import logging
import json
import httpx
import asyncio
from typing import List, Dict, Any
from core.db import db_client as db

logger = logging.getLogger("AuditWorker")

async def run_audit(sample_size=10):
    """
    Busca amostras de alta confiança e cruza com Groq (Llama 3).
    """
    logger.info(f"Iniciando auditoria cruzada (n={sample_size})...")
    
    # 1. Busca comentários de alta confiança para auditar
    # Nota: Usamos 'confianca_ia' ou 'confianza_ia' conforme o schema detectado
    try:
        res = db.client.table('comentarios').select('id, texto_limpo, categoria_ia, is_hate').gte('confianca_ia', 0.85).eq('processado_ia', True).limit(100).execute()
    except Exception:
        res = db.client.table('comentarios').select('id, texto_limpo, categoria_ia, is_hate').gte('confianza_ia', 0.85).eq('processado_ia', True).limit(100).execute()
    
    if not res.data or len(res.data) < sample_size:
        logger.info("Dados insuficientes para auditoria.")
        return

    sample = random.sample(res.data, sample_size)
    discrepancies = 0
    groq_api_key = os.getenv("GROQ_API_KEY")

    if not groq_api_key:
        logger.error("GROQ_API_KEY não configurada. Abortando auditoria.")
        return

    async with httpx.AsyncClient() as client:
        for comment in sample:
            prompt = f"""
            Você é um auditor de inteligência artificial. Classifique o texto a seguir seguindo a Taxonomia MTAD.
            Taxonomia: ODIO_IDENTITARIO, VIOLENCIA_GENERO, AMEACA, ATAQUE_INSTITUCIONAL, RIGOR_CRIMINAL, INSULTO_AD_HOMINEM, NEUTRO.
            Responda APENAS com um JSON válido: {{"rotulo": "hate" ou "not_hate", "categoria_ia": "CATEGORIA"}}
            Texto: "{comment['texto_limpo']}"
            """
            try:
                resp = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {groq_api_key}"},
                    json={
                        "model": "llama-3.3-70b-versatile",
                        "messages": [{"role": "user", "content": prompt}],
                        "response_format": {"type": "json_object"}
                    },
                    timeout=10.0
                )
                
                if resp.status_code == 200:
                    result = resp.json()['choices'][0]['message']['content']
                    data = json.loads(result)
                    
                    # 2. Compara com a classificação original
                    orig_hate = "hate" if comment['is_hate'] else "not_hate"
                    if data.get('categoria_ia') != comment['categoria_ia'] or data.get('rotulo') != orig_hate:
                        discrepancies += 1
                        # Marca no banco para revisão humana
                        # Tentamos atualizar, mesmo que as colunas sejam novas
                        try:
                            db.client.table('comentarios').update({
                                'needs_review': True, 
                                'audit_discrepancy': True,
                                'audit_data': data
                            }).eq('id', comment['id']).execute()
                        except Exception:
                            logger.warning(f"Falha ao marcar discrepância no DB para ID {comment['id']}")
                
            except Exception as e:
                logger.error(f"Erro na auditoria do ID {comment['id']}: {e}")

    drift_rate = (discrepancies / sample_size) * 100
    logger.info(f"Auditoria concluída. Taxa de divergência: {drift_rate}%")
    if drift_rate > 20:
        logger.warning("🚨 ALERTA: Alta taxa de divergência detectada!")
