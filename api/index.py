from fastapi import FastAPI, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database.repository import DatabaseRepository
from typing import Optional

app = FastAPI(
    title="API Análise Ódio Político",
    description="API para monitoramento e análise de discurso de ódio em redes sociais",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = DatabaseRepository()

def get_db():
    session = db.get_session()
    try:
        yield session
    finally:
        session.close()

@app.get("/api/v1/status")
def get_status():
    return {
        "status": "online",
        "version": "1.0.0",
        "database": "connected"
    }

@app.get("/api/v1/estatisticas/resumo")
def get_estatisticas_resumo():
    with db.get_session() as session:
        from database.models import Comentario, Classificacao
        from sqlalchemy import func
        
        total_comentarios = session.query(Comentario).count()
        total_odio = session.query(Classificacao).filter(Classificacao.categoria_odio != 'neutro').count()
        
        # Categorias de ódio
        categorias = session.query(
            Classificacao.categoria_odio, 
            func.count(Classificacao.id)
        ).filter(Classificacao.categoria_odio != 'neutro')\
         .group_by(Classificacao.categoria_odio).all()
         
        return {
            "total_comentarios": total_comentarios,
            "total_odio": total_odio,
            "taxa_odio": round((total_odio / total_comentarios * 100), 2) if total_comentarios > 0 else 0,
            "distribuicao_categorias": {k: v for k, v in categorias}
        }

@app.get("/api/v1/estatisticas/linha-do-tempo")
def get_linha_do_tempo():
    with db.get_session() as session:
        from database.models import Comentario, Classificacao
        from sqlalchemy import func, String, cast
        
        resultados = session.query(
            func.date(Comentario.data_publicacao).label('dia'),
            func.count(Comentario.id).label('total'),
            func.sum(func.case((Classificacao.categoria_odio != 'neutro', 1), else_=0)).label('odio')
        ).join(Classificacao, isouter=True)\
         .group_by(func.date(Comentario.data_publicacao))\
         .order_by(func.date(Comentario.data_publicacao))\
         .all()
         
        return [
            {
                "data": str(r.dia),
                "total": r.total,
                "odio": r.odio
            } for r in resultados if r.dia
        ]

@app.get("/api/v1/candidatos")
def listar_candidatos():
    with db.get_session() as session:
        from database.models import Candidato
        candidatos = session.query(Candidato).all()
        return [
            {
                "id": c.id,
                "username": c.username,
                "nome_completo": c.nome_completo,
                "partido": c.partido,
                "cargo": c.cargo,
                "estado": c.estado
            } for c in candidatos
        ]

@app.get("/api/v1/comentarios")
def listar_comentarios(
    hate: Optional[bool] = None,
    party: Optional[str] = None,
    candidate: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    with db.get_session() as session:
        from database.models import Comentario, Classificacao, Candidato
        query = session.query(Comentario, Classificacao, Candidato)\
            .join(Classificacao, isouter=True)\
            .join(Candidato)
        
        if hate is not None:
            if hate:
                query = query.filter(Classificacao.categoria_odio != 'neutro')
            else:
                query = query.filter(Classificacao.categoria_odio == 'neutro')
        
        if party:
            query = query.filter(Candidato.partido == party)
        
        if candidate:
            query = query.filter(Candidato.username == candidate)
        
        total = query.count()
        resultados = query.offset(offset).limit(limit).all()
        
        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "dados": [
                {
                    "id": c.id,
                    "texto": c.texto_bruto,
                    "data": c.data_publicacao,
                    "autor": c.autor_username,
                    "candidato": can.username,
                    "partido": can.partido,
                    "categoria": cl.categoria_odio if cl else None,
                    "score": cl.score if cl else None
                } for c, cl, can in resultados
            ]
        }

@app.get("/api/v1/estatisticas/por-partido")
def estatisticas_por_partido():
    with db.get_session() as session:
        from sqlalchemy import func
        from database.models import Candidato, Comentario, Classificacao
        
        resultados = session.query(
            Candidato.partido,
            func.count(Comentario.id).label('total_comentarios'),
            func.sum(func.case((Classificacao.categoria_odio != 'neutro', 1), else_=0)).label('total_odio')
        ).join(Comentario).join(Classificacao, isouter=True)\
         .group_by(Candidato.partido)\
         .order_by(func.count(Comentario.id).desc())\
         .all()
        
        return [
            {
                "partido": r.partido,
                "total_comentarios": r.total_comentarios,
                "total_odio": r.total_odio,
                "taxa_odio": round((r.total_odio / r.total_comentarios * 100), 2) if r.total_comentarios > 0 else 0
            } for r in resultados
        ]

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API ForenseNet v2.0 (FastAPI em Vercel)"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
