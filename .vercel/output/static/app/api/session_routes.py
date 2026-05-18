from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core.supabase_service import supabase

router = APIRouter(prefix="/api/v1/sessions", tags=["Sessions"])

class SessionPayload(BaseModel):
    cookies: str

@router.post("/instagram/cookies")
def update_instagram_cookies(payload: SessionPayload):
    """
    PASA v24: Injeta novos cookies do Instagram e despausa a fila automaticamente.
    Resolve o bloqueio do Circuit Breaker via Dashboard.
    """
    try:
        # 1. Atualiza os cookies na tabela de sessões
        supabase.table('worker_sessions').update({
            'cookies': payload.cookies,
            'status': 'active',
            'updated_at': 'now()'
        }).eq('plataforma', 'instagram').execute()
        
        # 2. Tenta despausar a fila_coleta se houver status de erro
        try:
            # Tenta resetar tentativas e status para itens que falharam por auth
            supabase.table('fila_coleta')\
                .update({'status': 'PENDENTE', 'tentativas': 0})\
                .eq('status', 'paused_auth_fail')\
                .execute()
        except Exception as e:
            print(f"⚠️ Erro ao resetar fila_coleta: {e}")
            
        return {"status": "success", "message": "Cookies atualizadas e Circuit Breaker despausado."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
