from fastapi import APIRouter, HTTPException
from app.database import supabase

router = APIRouter(prefix="/api/v1/monitor", tags=["Monitor"])

# ... (rotas existentes) ...

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
