# api/routes/sessions.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Optional
from core.supabase_service import get_supabase_client
from datetime import datetime, UTC

router = APIRouter(prefix="/api/v1/sessions")

class InstagramSessionUpdate(BaseModel):
    session_id: str
    ds_user_id: str
    csrf_token: str
    profile_name: Optional[str] = "default"

@router.get("/instagram/status")
async def get_instagram_session_status():
    """Verifica se há uma sessão ativa e sua validade (simulado via DB)."""
    db = get_supabase_client()
    try:
        res = db.table("system_configs").select("*").eq("key", "instagram_session").single().execute()
        if not res.data:
            return {"status": "missing", "message": "Nenhuma sessão configurada"}
        
        config = res.data.get("value", {})
        last_updated = res.data.get("updated_at")
        
        return {
            "status": "active",
            "profile_name": config.get("profile_name", "unknown"),
            "last_updated": last_updated,
            "is_valid": True # Futuramente integrar com check real do Instagram
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@router.post("/instagram/update")
async def update_instagram_session(data: InstagramSessionUpdate):
    """Atualiza os tokens de sessão do Instagram no banco de dados."""
    db = get_supabase_client()
    try:
        session_data = {
            "session_id": data.session_id,
            "ds_user_id": data.ds_user_id,
            "csrf_token": data.csrf_token,
            "profile_name": data.profile_name
        }
        
        db.table("system_configs").upsert({
            "key": "instagram_session",
            "value": session_data,
            "updated_at": datetime.now(UTC).isoformat()
        }, on_conflict="key").execute()
        
        return {"status": "success", "message": "Sessão atualizada com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
