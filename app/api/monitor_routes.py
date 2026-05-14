from fastapi import APIRouter, HTTPException
from app.database import supabase

router = APIRouter(prefix="/api/v1/monitor", tags=["Monitor"])

@router.post("/queue/unpause/{platform}")
def unpause_queue(platform: str):
    """
    Rota de emergência: Reativa a fila de uma plataforma após a atualização de cookies.
    Requer confirmação manual do operador.
    """
    if platform not in ["instagram", "twitter", "tiktok"]:
        raise HTTPException(status_code=400, detail="Plataforma inválida.")
    
    result = supabase.table('fila_coleta')\
        .update({'status': 'pending'})\
        .eq('plataforma', platform)\
        .eq('status', 'paused_auth_fail')\
        .execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Nenhuma fila pausada encontrada para esta plataforma.")
        
    return {"status": "success", "message": f"Fila de {platform} reativada com sucesso."}

@router.get("/status")
def get_system_status():
    """
    PASA v21: Painel de Bordo. Agrega métricas críticas em uma única chamada.
    """
    # 1. Saúde da Fila e Circuit Breaker
    queue_data = supabase.table('fila_coleta').select('status, plataforma').execute()
    
    paused_platforms = list(set(
        item['plataforma'] for item in queue_data.data 
        if item['status'] == 'paused_auth_fail'
    ))
    
    queue_summary = {
        "pending": sum(1 for item in queue_data.data if item['status'] == 'pending'),
        "processing": sum(1 for item in queue_data.data if item['status'] == 'processing'),
        "circuit_breaker_tripped": len(paused_platforms) > 0,
        "paused_platforms": paused_platforms
    }
    
    # 2. Ranking de Evolução (Top Workers)
    ledger_data = supabase.table('worker_ledger').select('worker_id, current_xp, current_level, total_runs').order('current_xp', desc=True).limit(5).execute()
    
    # 3. Últimas Falhas Críticas
    recent_failures = supabase.table('worker_runs').select('worker_id, error_message, created_at').eq('status', 'failed').order('created_at', desc=True).limit(3).execute()
    
    return {
        "pasa_version": 21,
        "autonomous_mode": True,
        "queue_health": queue_summary,
        "worker_evolution": ledger_data.data,
        "recent_critical_failures": recent_failures.data
    }
