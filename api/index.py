from fastapi import FastAPI, Query, Depends, Body, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
from database.repository import DatabaseRepository
from typing import Optional, List, Dict
import os
import io
from datetime import datetime

app = FastAPI(title="ForenseNet API v2.7 - Ultra Resilient", version="2.7.0")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

db = DatabaseRepository()
try:
    db.criar_tabelas()
except Exception as e:
    print(f"Erro inicializacao: {e}")

DASHBOARD_PIN = os.getenv("DASHBOARD_PIN", "1234") 

def verify_pin(x_pin: Optional[str] = Header(None)):
    if x_pin != DASHBOARD_PIN:
        raise HTTPException(status_code=401, detail="PIN invalido")

@app.get("/api/v1/status")
def get_status():
    return {"status": "online", "environment": "serverless"}

@app.get("/api/v1/estatisticas/resumo")
def get_estatisticas_resumo():
    try:
        with db.get_session() as session:
            from database.models import Comentario, Classificacao
            from sqlalchemy import func
            total = session.query(Comentario).count()
            odio = session.query(Classificacao).filter(func.lower(Classificacao.categoria_odio) != 'neutro').count()
            categorias = session.query(Classificacao.categoria_odio, func.count(Classificacao.id)).filter(func.lower(Classificacao.categoria_odio) != 'neutro').group_by(Classificacao.categoria_odio).all()
            return {
                "total_comentarios": total or 0,
                "total_odio": odio or 0,
                "distribuicao_categorias": {str(k): v for k, v in categorias if k} if categorias else {}
            }
    except Exception as e:
        return {"error": str(e), "total_comentarios": 0, "total_odio": 0, "distribuicao_categorias": {}}

@app.get("/api/v1/comentarios")
def listar_comentarios(hate: Optional[bool] = None, limit: int = 50):
    try:
        with db.get_session() as session:
            from database.models import Comentario, Classificacao, Candidato
            query = session.query(Comentario, Classificacao, Candidato).join(Classificacao, isouter=True).join(Candidato)
            if hate: query = query.filter(Classificacao.categoria_odio != 'NEUTRO')
            res = query.order_by(Comentario.data_publicacao.desc()).limit(limit).all()
            return {
                "dados": [{
                    "id": c.id, "texto": c.texto_bruto, "autor": c.autor_username, "candidato": can.username,
                    "categoria": cl.categoria_odio if cl else "NEUTRO", "score": cl.score if cl else 0
                } for c, cl, can in res]
            }
    except Exception as e:
        return {"dados": [], "error": str(e)}

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
                
                id_ext = str(item.get('id_externo'))
                if not session.query(Comentario).filter(Comentario.id_externo == id_ext).first():
                    data_str = item.get('data')
                    data_obj = datetime.fromisoformat(data_str.replace('Z', '+00:00')) if data_str else datetime.utcnow()
                    com = Comentario(id_externo=id_ext, candidato_id=candidato.id, autor_username=item.get('autor'), texto_bruto=item.get('texto'), data_publicacao=data_obj)
                    session.add(com); session.flush()
                    cl = Classificacao(comentario_id=com.id, categoria_odio=item.get('categoria'), score=item.get('score'), modelo_versao='worker-sync')
                    session.add(cl); count += 1
            except: continue
        session.commit()
        return {"status": "success", "items_synced": count}

@app.get("/api/v1/export/laudo", dependencies=[Depends(verify_pin)])
def export_laudo():
    with db.get_session() as session:
        from database.models import Comentario, Classificacao, Candidato
        query = session.query(Comentario, Classificacao, Candidato).join(Classificacao).join(Candidato).limit(100)
        output = io.StringIO()
        output.write("DATA,AUTOR,ALVO,TEXTO,CATEGORIA,SCORE\n")
        for c, cl, can in query.all():
            txt = c.texto_bruto.replace('"', '""').replace('\n', ' ')
            output.write(f'"{c.data_publicacao}","{c.autor_username}","{can.username}","{txt}","{cl.categoria_odio}",{cl.score}\n')
        return StreamingResponse(io.BytesIO(output.getvalue().encode('utf-8-sig')), media_type="text/csv", headers={"Content-Disposition": "attachment; filename=laudo_forensenet.csv"})

@app.get("/api/v1/estatisticas/linha-do-tempo")
def get_timeline(): return []
@app.get("/api/v1/pipeline/status")
def get_pipe_status(): return {"status": "OPERACIONAL"}
@app.get("/api/v1/pipeline/history")
def get_pipe_history(): return []

@app.get("/api")
def read_root():
    return {"status": "ForenseNet API v2.7 Online"}
