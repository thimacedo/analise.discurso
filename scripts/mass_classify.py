import asyncio
import logging
from datetime import datetime, timezone
from core.supabase_service import supabase as db
from core.ai_service import AIService
from core.circuit_breaker import ai_circuit_breaker

logger = logging.getLogger("MassClassify")

async def process_mass_classification(limit: int = 50):
    logger.info(f"Iniciando lote de classificação (limite: {limit})...")

    # 1. Verifica saúde geral das IAs antes de começar
    can_proceed = any([
        ai_circuit_breaker.can_execute("groq"),
        ai_circuit_breaker.can_execute("mistral"),
        ai_circuit_breaker.can_execute("openrouter")
    ])
    if not can_proceed:
        logger.error("🛑 [IA] Todas as APIs estão com circuito aberto. Abortando lote.")
        return

    # 2. Busca pendentes
    res = db.table('comentarios') 
        .select('id, texto_bruto') 
        .eq('processado_ia', False) 
        .limit(limit) 
        .execute()

    if not res.data:
        logger.info("Nenhum comentário pendente para classificar.")
        return

    ai = AIService()
    success_count = 0
    fail_count = 0

    for comment in res.data:
        # Checagem de saúde durante o loop
        can_proceed_loop = any([
            ai_circuit_breaker.can_execute("groq"),
            ai_circuit_breaker.can_execute("mistral"),
            ai_circuit_breaker.can_execute("openrouter")
        ])
        if not can_proceed_loop:
            logger.error("🛑 [IA] APIs caíram durante o lote. Abortando para não sobrecarregar.")
            break

        try:
            result = await ai.classify_text(comment['texto_bruto'])
            
            # Atualiza Supabase
            db.table('comentarios').update({
                'processado_ia': True,
                'is_hate': result['is_hate'],
                'categoria_ia': result['categoria_ia'],
                'confianca_ia': result['confianca_ia'],
                'analise_pericial': result.get('analise_pericial', '')
            }).eq('id', comment['id']).execute()
            
            success_count += 1
            
        except RuntimeError:
            # Todas as IAs falharam neste item específico
            fail_count += 1
            if fail_count >= 3:
                logger.error("🛑 [IA] 3 falhas consecutivas sem fallback. Parando lote.")
                break
        except Exception as e:
            logger.error(f"Erro ao processar comentário {comment['id']}: {e}")
            fail_count += 1

        # Pausa humana entre chamadas (anti-rate limit)
        await asyncio.sleep(1.5)

    logger.info(f"Lote finalizado: {success_count} sucessos, {fail_count} falhas.")
