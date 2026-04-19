from fastapi import FastAPI, Query, Depends, Body, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from typing import Optional, List, Dict
from datetime import datetime

# Imports Modulares
from api.templates import DASHBOARD_HTML
from api.config import DASHBOARD_PIN
from database.repository import DatabaseRepository

app = FastAPI(title="ForenseNet API v5.5 - Modular Architecture", version="5.5.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

db = DatabaseRepository()

# --- SEGURANÇA ---
def verify_pin(x_pin: Optional[str] = Header(None)):
    if x_pin != DASHBOARD_PIN:
        raise HTTPException(status_code=401, detail="PIN invalido")

# --- ROTAS DE INTERFACE ---
@app.get("/", response_class=HTMLResponse)
def read_root():
    return HTMLResponse(content=DASHBOARD_HTML)

@app.get("/api")
def read_api_root():
    return {"status": "ForenseNet API v5.5 Modular Online"}

# --- ROTAS DE DADOS ---
@app.get("/api/v1/status")
def get_status():
    return {"status": "online", "version": "5.5.0"}

@app.get("/api/v1/comentarios")
def listar_comentarios(hate: Optional[bool] = None, limit: int = 100):
    try:
        with db.get_session() as session:
            from database.models import Comentario, Classificacao, Candidato
            query = session.query(Comentario, Classificacao, Candidato).join(Classificacao, isouter=True).join(Candidato)
            if hate: query = query.filter(Classificacao.is_hate == True)
            res = query.order_by(Comentario.data_coleta.desc()).limit(limit).all()
            return [{
                "id": str(c.id), "texto_bruto": c.texto_bruto, "autor": c.autor_username, 
                "candidato_id": can.username, "is_hate": cl.is_hate if cl else False,
                "categoria_ia": cl.categoria_odio if cl else "NEUTRO", "data_coleta": c.data_coleta.isoformat(),
                "post_url": c.post_id,
                "post_image": c.id_externo.split('_')[0] if "_" in str(c.id_externo) else None,
                "post_caption": c.texto_limpo
            } for c, cl, can in res]
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/v1/sync", dependencies=[Depends(verify_pin)])
def sync_data(payload: List[Dict] = Body(...)):
    with db.get_session() as session:
        from database.models import Comentario, Classificacao, Candidato
        count = 0
        for item in payload:
            try:
                can_name = item.get('candidato', 'desconhecido')
                candidato = session.query(Candidato).filter(Candidato.username == can_name).first()
                if not candidato:
                    candidato = Candidato(username=can_name); session.add(candidato); session.flush()
                
                id_ext = str(item.get('id_external') or item.get('id_externo'))
                if not session.query(Comentario).filter(Comentario.id_externo == id_ext).first():
                    data_str = item.get('data')
                    data_obj = datetime.fromisoformat(data_str.replace('Z', '+00:00')) if data_str else datetime.utcnow()
                    com = Comentario(
                        id_externo=id_ext, candidato_id=candidato.id, autor_username=item.get('autor'), 
                        texto_bruto=item.get('texto'), data_publicacao=data_obj, post_id=item.get('post_url'),
                        texto_limpo=item.get('post_caption')
                    )
                    session.add(com); session.flush()
                    is_h = item.get('categoria', 'NEUTRO') != 'NEUTRO'
                    cl = Classificacao(comentario_id=com.id, is_hate=is_h, categoria_odio=item.get('categoria'), score=item.get('score'), modelo_versao='qwen-v5.5-modular')
                    session.add(cl); count += 1
            except: continue
        session.commit()
        return {"status": "success", "items_synced": count}
