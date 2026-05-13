# core/worker_auditor.py
import logging
from core.supabase_service import get_supabase_client

logger = logging.getLogger("WorkerAuditor")

# Constantes de Evolução (Sem pressão, custo de subida baixo)
XP_PER_SUCCESS = 10
XP_PER_CRITICAL_HIT = 25
XP_TO_LEVEL_UP = [50, 150, 300, 600, 1000] # XP necessário para ir do Nível 0->1, 1->2, etc.

# Limiar de Burla (Anti-Cheat)
# Se mais de 95% do que o worker traz é NEUTRO, e ele trouxe mais de 20 itens, ele está rasgando o processo.
SHORTCUT_NEUTRALITY_THRESHOLD = 0.95
SHORTCUT_VOLUME_THRESHOLD = 20

def audit_worker_result(worker_name: str, extracted_data: list):
    """
    Avalia o resultado de um worker, distribui recompensas ou aplica punições sistêmicas.
    A filosofia é: Falha é normal. Atalho é inaceitável.
    """
    supabase = get_supabase_client()
    
    # 1. Busca o estado atual do Worker no Ledger
    res = supabase.table('worker_ledger').select('*').eq('worker_name', worker_name).execute()
    if not res.data:
        # Primeira vez, registra como Novato (Nível 0)
        ledger = {"worker_name": worker_name, "level": 0, "xp": 0, "status": "ACTIVE"}
        supabase.table('worker_ledger').insert(ledger).execute()
    else:
        ledger = res.data[0]

    if ledger.get('status') == 'BANNED':
        logger.warning(f"⛔ Worker {worker_name} está BANIDO por violação sistêmica. Processo cancelado.")
        return False # Impede a execução

    total_items = len(extracted_data)
    if total_items == 0:
        # Falha em extrair dados não é punível, o ambiente é hostil.
        logger.info(f"📊 Auditoria: {worker_name} não rendeu dados. Sem punição, sem recompensa.")
        return True

    # 2. Cálculo de Métricas da Rodada
    critical_hits = sum(1 for item in extracted_data if item.get('is_critical'))
    neutral_hits = sum(1 for item in extracted_data if item.get('category') == 'NEUTRO')
    neutrality_rate = neutral_hits / total_items

    # 3. DETECÇÃO DE ATALHO (A Burla)
    # Se o worker trouxe um volume alto e quase tudo é lixo (NEUTRO), ele ignorou o processo de qualidade.
    if total_items >= SHORTCUT_VOLUME_THRESHOLD and neutrality_rate >= SHORTCUT_NEUTRALITY_THRESHOLD:
        logger.error(f"🚨 VIOLAÇÃO DE PROCESSO DETECTADA EM {worker_name}!")
        logger.error(f"🚨 Volume: {total_items}, Neutralidade: {neutrality_rate*100}%")
        logger.error(f"🚨 O processo foi burlado. O sistema será punido e o worker desativado.")
        
        # Punição Máxima: Desativação e Resete do Processo
        supabase.table('worker_ledger').update({
            "status": "BANNED",
            "level": 0,
            "xp": 0,
            "process_violations": ledger.get('process_violations', 0) + 1
        }).eq('worker_name', worker_name).execute()
        
        return False # Sinaliza para o Maestro parar o processo atual e reiniciar a fila

    # 4. DISTRIBUIÇÃO DE RECOMPENSAS (Evolução Gradual)
    xp_earned = (total_items * XP_PER_SUCCESS) + (critical_hits * XP_PER_CRITICAL_HIT)
    new_xp = ledger.get('xp', 0) + xp_earned
    current_level = ledger.get('level', 0)
    
    # Verifica se subiu de nível
    leveled_up = False
    if current_level < 5 and new_xp >= XP_TO_LEVEL_UP[current_level]:
        current_level += 1
        leveled_up = True
        logger.info(f"🎉 LEVEL UP! {worker_name} evoluiu para o Nível {current_level}!")

    # 5. Atualização do Ledger
    supabase.table('worker_ledger').update({
        "xp": new_xp,
        "level": current_level,
        "successful_extractions": ledger.get('successful_extractions', 0) + total_items,
        "critical_hits": ledger.get('critical_hits', 0) + critical_hits,
        "neutrality_rate": neutrality_rate, # Atualiza a taxa da última rodada
        "last_audit": "NOW()",
        "status": "ACTIVE"
    }).eq('worker_name', worker_name).execute()

    logger.info(f"📊 Auditoria: {worker_name} ganhou {xp_earned} XP. Total: {new_xp}. Nível: {current_level}")
    return True
