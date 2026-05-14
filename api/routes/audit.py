# api/routes/audit.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from core.supabase_service import get_supabase_client
from datetime import datetime, UTC

router = APIRouter(prefix="/api/v1/audit", tags=["Audit"])

class AuditValidation(BaseModel):
    comment_id: str
    rotulo_correto: str
    validado_por: str

@router.post("/validate")
async def validate_comment(payload: AuditValidation):
    """
    Marca um comentário como Padrão Ouro (Falso Positivo ou Validado).
    Acesso restrito a admin (configurado via frontend/middleware).
    """
    db = get_supabase_client()
    
    # Busca o comentário original para garantir que existe
    comment = db.table('comentarios').select('texto_bruto').eq('id', payload.comment_id).single().execute()
    if not comment.data:
        raise HTTPException(status_code=404, detail="Comentário não encontrado.")
    
    try:
        # Insere na tabela de Gold Standard
        audit_data = {
            "original_comment_id": payload.comment_id,
            "texto_original": comment.data['texto_bruto'],
            "rotulo_correto": payload.rotulo_correto,
            "validado_por": payload.validado_por,
            "created_at": datetime.now(UTC).isoformat()
        }
        
        result = db.table('audit_gold_standards').insert(audit_data).execute()
        return {"status": "success", "audit_id": result.data[0]['id']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
