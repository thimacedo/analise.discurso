from fastapi import FastAPI, Query, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database.repository import DatabaseRepository
from typing import Optional
import os
import pyotp
import pandas as pd
import io
from datetime import datetime
from processing.dossie_service import DossieService
from pydantic import BaseModel

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

# --- AUTH MODELS & ENDPOINTS ---

class AuthRequest(BaseModel):
    code: str

@app.post("/api/v1/admin/auth/verify")
def verify_totp(request: AuthRequest):
    secret = os.getenv("SENTINELA_ADMIN_TOTP_SECRET")
    if not secret:
        raise HTTPException(status_code=500, detail="Segredo TOTP não configurado no servidor.")

    totp = pyotp.TOTP(secret)
    if totp.verify(request.code):
        return {"status": "success", "token": "temp-admin-session-token"}

    raise HTTPException(status_code=401, detail="Código inválido ou expirado.")

# --- GESTÃO DE ALVOS MODELS & ENDPOINTS ---

class TargetUpsertRequest(BaseModel):
    username: str
    nome_completo: Optional[str] = "Não informado"
    cargo: Optional[str] = "Monitorado"
    estado: Optional[str] = "BR"
    status: Optional[str] = "Ativo"

@app.get("/api/v1/admin/targets")
def list_admin_targets(search: Optional[str] = None):
    with db.get_session() as session:
        from database.models import Candidato
        query = session.query(Candidato)
        if search:
            query = query.filter(Candidato.username.ilike(f"%{search}%") | Candidato.nome_completo.ilike(f"%{search}%"))
        
        targets = query.order_by(Candidato.status_monitoramento.asc(), Candidato.username.asc()).all()
        return [
            {
                "username": t.username,
                "nome_completo": t.nome_completo,
                "cargo": t.cargo,
                "estado": t.estado,
                "status": t.status_monitoramento
            } for t in targets
        ]

@app.post("/api/v1/admin/targets/upsert")
def upsert_target(target: TargetUpsertRequest):
    with db.get_session() as session:
        from database.models import Candidato
        username_clean = target.username.strip().replace("@", "").lower()
        
        db_target = session.query(Candidato).filter(Candidato.username == username_clean).first()
        if db_target:
            db_target.nome_completo = target.nome_completo
            db_target.cargo = target.cargo
            db_target.estado = target.estado
            db_target.status_monitoramento = target.status
        else:
            new_target = Candidato(
                username=username_clean,
                nome_completo=target.nome_completo,
                cargo=target.cargo,
                estado=target.estado,
                status_monitoramento=target.status
            )
            session.add(new_target)
        
        session.commit()
        return {"status": "success", "message": f"@{username_clean} atualizado/adicionado."}

@app.patch("/api/v1/admin/targets/{username}/status")
def toggle_target_status(username: str, status: str):
    with db.get_session() as session:
        from database.models import Candidato
        db_target = session.query(Candidato).filter(Candidato.username == username.lower()).first()
        if not db_target:
            raise HTTPException(status_code=404, detail="Alvo não encontrado.")
        
        db_target.status_monitoramento = status
        session.commit()
        return {"status": "success", "new_status": status}

@app.post("/api/v1/admin/targets/import")
async def import_targets(file: UploadFile = File(...)):
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Apenas arquivos .csv são aceitos.")
    
    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents))
    
    required = ['username', 'full_name']
    if not all(col in df.columns for col in required):
        raise HTTPException(status_code=400, detail=f"CSV inválido. Colunas obrigatórias: {required}")
    
    success_count = 0
    with db.get_session() as session:
        from database.models import Candidato
        for _, row in df.iterrows():
            username = str(row['username']).strip().replace("@", "").lower()
            data = {
                "username": username,
                "nome_completo": row.get('full_name', "Não informado"),
                "cargo": row.get('cargo', "Monitorado"),
                "estado": row.get('estado', "BR"),
                "status_monitoramento": row.get('status', "Ativo")
            }
            
            target = session.query(Candidato).filter(Candidato.username == username).first()
            if target:
                target.nome_completo = data["nome_completo"]
                target.cargo = data["cargo"]
                target.estado = data["estado"]
                target.status_monitoramento = data["status_monitoramento"]
            else:
                session.add(Candidato(**data))
            success_count += 1
        
        session.commit()
    
    return {"status": "success", "message": f"{success_count} perfis processados com sucesso."}

@app.get("/api/v1/admin/targets/template")
def download_template():
    df = pd.DataFrame(columns=['username', 'full_name', 'cargo', 'estado', 'status'])
    df.loc[0] = ['lulaoficial', 'Luiz Inácio Lula da Silva', 'Presidente', 'BR', 'Ativo']
    
    stream = io.StringIO()
    df.to_csv(stream, index=False)
    
    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=modelo_importacao_sentinela.csv"
    return response

# --- PUBLIC ENDPOINTS ---

@app.get("/api/v1/exportar-dossie")
def exportar_dossie(candidate: Optional[str] = None):
    with db.get_session() as session:
        from database.models import Comentario, Classificacao, Candidato
        query = session.query(Comentario, Classificacao, Candidato)\
            .join(Classificacao, isouter=True)\
            .join(Candidato)
        
        if candidate:
            query = query.filter(Candidato.username == candidate)
            
        resultados = query.order_by(Comentario.data_publicacao.desc()).limit(50).all()
        
        if not resultados:
            raise HTTPException(status_code=404, detail="Nenhum dado encontrado para exportação.")
            
        dados_formatados = [
            {
                "candidatos": {"username": can.username},
                "texto_bruto": c.texto_bruto,
                "is_hate": cl.categoria_odio != 'neutro' if cl else False,
                "categoria_ia": cl.categoria_odio if cl else "Não Classificado"
            } for c, cl, can in resultados
        ]
        
        output_dir = os.path.join(os.getcwd(), "data", "reports")
        os.makedirs(output_dir, exist_ok=True)
        
        filename = f"dossie_inteligencia_{candidate if candidate else 'geral'}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(output_dir, filename)
        
        service = DossieService()
        service.generate_dossie(dados_formatados, filepath)
        
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type='application/pdf'
        )

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
        total_odio = session.query(Classificacao).filter(func.lower(Classificacao.categoria_odio) != 'neutro').count()
        
        categorias = session.query(
            Classificacao.categoria_odio, 
            func.count(Classificacao.id)
        ).filter(func.lower(Classificacao.categoria_odio) != 'neutro')\
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
        from sqlalchemy import func
        
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
