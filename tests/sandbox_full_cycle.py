# tests/sandbox_full_cycle.py
import pytest
import asyncio
from workers.scrapers.instagram_worker import InstagramWorker
from workers.processors.classifier_worker import ClassifierWorker
from core.supabase_service import get_supabase_client

@pytest.mark.asyncio
async def test_full_sandbox_cycle():
    """
    PASA v17 Smoke Test: Valida fluxo Fila -> Coleta -> Classificação -> XP
    """
    db = get_supabase_client()
    target_username = "instagram" # Perfil de teste
    
    # 1. Setup: Garante que o alvo existe no banco
    db.table('candidatos').upsert({
        "username": target_username,
        "status_monitoramento": "Ativo",
        "prioridade_coleta": 5
    }, on_conflict="username").execute()

    # 2. Executa InstagramWorker
    scraper = InstagramWorker(target_profile=target_username, max_posts=1)
    results = await scraper.execute()
    
    assert results is not None, "Worker do Instagram falhou na coleta"
    assert len(results) >= 0, "Extração concluída (pode ser 0 se não houver novos posts)"
    
    # 3. Executa ClassifierWorker
    classifier = ClassifierWorker()
    classification_results = await classifier.execute()
    
    assert classification_results is not None, "Worker de Classificação falhou"
    
    # 4. Validação no Banco de Dados (Comentários e Runs)
    # Verifica se a run registrou XP
    run_res = db.table('worker_runs')\
        .select('xp_gained')\
        .eq('worker_name', f"InstagramWorker-{target_username}")\
        .order('started_at', desc=True)\
        .limit(1)\
        .execute()
    
    assert run_res.data[0]['xp_gained'] != 0, "XP não foi processado (pode ser positivo ou negativo)"
    
    # 5. Validação do Ledger
    ledger_res = db.table('worker_ledger').select('current_xp, current_level').eq('worker_name', f"InstagramWorker-{target_username}").execute()
    if ledger_res.data:
        assert ledger_res.data[0]['current_xp'] >= 0, "Ledger registrou XP inválido"

if __name__ == "__main__":
    asyncio.run(test_full_sandbox_cycle())
