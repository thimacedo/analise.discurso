from fastapi import FastAPI, Query, Depends, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from database.repository import DatabaseRepository
from local_qwen_classifier import QwenLocalClassifier
from typing import Optional, List, Dict
import os

app = FastAPI(
    title="ForenseNet API v2.1",
    description="Backend para monitoramento pericial de discurso de ódio",
    version="2.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = DatabaseRepository()
qwen = QwenLocalClassifier()

# --- ENDPOINTS DE DADOS ---

@app.get("/api/v1/status")
def get_status():
    is_vercel = os.getenv("VERCEL") or os.getenv("VERCEL_ENV")
    return {
        "status": "online",
        "environment": "serverless" if is_vercel else "local",
        "database": "sqlite_memory" if is_vercel and not os.getenv("DATABASE_URL") else "connected"
    }

@app.get("/api/v1/estatisticas/resumo")
def get_estatisticas_resumo():
    with db.get_session() as session:
        from database.models import Comentario, Classificacao
        from sqlalchemy import func
        
        total_comentarios = session.query(Comentario).count()
        # Filtra categorias que não sejam NEUTRO (case insensitive)
        total_odio = session.query(Classificacao).filter(func.lower(Classificacao.categoria_odio) != 'neutro').count()
        
        categorias = session.query(
            Classificacao.categoria_odio, 
            func.count(Classificacao.id)
        ).filter(func.lower(Classificacao.categoria_odio) != 'neutro')\
         .group_by(Classificacao.categoria_odio).all()
         
        avg_confidence = session.query(func.avg(Classificacao.confianca)).scalar() or 0
         
        return {
            "total_comentarios": total_comentarios,
            "total_odio": total_odio,
            "taxa_odio": round((total_odio / total_comentarios * 100), 2) if total_comentarios > 0 else 0,
            "avg_confidence": round(float(avg_confidence) * 100, 1),
            "distribuicao_categorias": {k: v for k, v in categorias}
        }

@app.get("/api/v1/estatisticas/linha-do-tempo")
def get_linha_do_tempo():
    with db.get_session() as session:
        from database.models import Comentario, Classificacao
        from sqlalchemy import func
        
        resultados = session.query(
            func.date(Comentario.data_publicacao).label('dia'),
            func.count(Comentario.id).label('total'),
            func.sum(func.case((func.lower(Classificacao.categoria_odio) != 'neutro', 1), else_=0)).label('odio')
        ).join(Classificacao, isouter=True)\
         .group_by(func.date(Comentario.data_publicacao))\
         .order_by(func.date(Comentario.data_publicacao))\
         .all()
         
        return [
            {"data": str(r.dia), "total": r.total, "odio": r.odio or 0} 
            for r in resultados if r.dia
        ]

@app.get("/api/v1/comentarios")
def listar_comentarios(
    hate: Optional[bool] = None,
    limit: int = Query(50, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    with db.get_session() as session:
        from database.models import Comentario, Classificacao, Candidato
        query = session.query(Comentario, Classificacao, Candidato)\
            .join(Classificacao, isouter=True)\
            .join(Candidato)
        
        if hate is True:
            query = query.filter(func.lower(Classificacao.categoria_odio) != 'neutro')
        elif hate is False:
            query = query.filter(func.lower(Classificacao.categoria_odio) == 'neutro')
        
        total = query.count()
        resultados = query.order_by(Comentario.data_publicacao.desc()).offset(offset).limit(limit).all()
        
        return {
            "total": total,
            "dados": [
                {
                    "id": c.id,
                    "texto": c.texto_bruto,
                    "data": c.data_publicacao.isoformat() if c.data_publicacao else None,
                    "autor": c.autor_username,
                    "candidato": can.username,
                    "categoria": cl.categoria_odio if cl else "N/A",
                    "score": cl.score if cl else 0,
                    "confianca": cl.confianca if cl else 0
                } for c, cl, can in resultados
            ]
        }

# --- ENDPOINT DE ANÁLISE EM TEMPO REAL ---

@app.post("/api/v1/analyze")
def analyze_text(payload: Dict = Body(...)):
    text = payload.get("text")
    if not text:
        return {"error": "Texto é obrigatório"}, 400
    
    # Usa o classificador Qwen Local que configuramos
    result = qwen.classify_comment(text)
    return result

# --- SERVIR DASHBOARD ---

@app.get("/", response_class=HTMLResponse)
def read_root():
    try:
        path = os.path.join(os.getcwd(), "dashboard.html")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        return "<h1>Dashboard não encontrado na raiz</h1>"
    except Exception as e:
        return f"<h1>Erro ao carregar dashboard: {str(e)}</h1>"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
