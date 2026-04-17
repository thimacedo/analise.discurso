# database/repository.py
import os
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Importing models
from database.models import Base, Candidato, Comentario, Classificacao, ExecucaoPipeline

load_dotenv()

class DatabaseRepository:
    """
    Repositório de Banco de Dados via SQLAlchemy.
    Suporta PostgreSQL (Produção) ou SQLite (Desenvolvimento).
    """
    def __init__(self):
        # Default to SQLite if DATABASE_URL is not set
        db_url = os.getenv("DATABASE_URL", "sqlite:///./odio_politica.db")
        
        # SQLite specifics
        connect_args = {}
        if db_url.startswith("sqlite"):
            connect_args["check_same_thread"] = False
            
        self.engine = create_engine(db_url, connect_args=connect_args)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def criar_tabelas(self):
        """Cria as tabelas no banco de dados, se não existirem."""
        Base.metadata.create_all(bind=self.engine)
        
    def get_session(self):
        return self.SessionLocal()

    def iniciar_execucao(self):
        session = self.get_session()
        try:
            execucao = ExecucaoPipeline(status="EM_ANDAMENTO")
            session.add(execucao)
            session.commit()
            session.refresh(execucao)
            return execucao
        finally:
            session.close()

    def finalizar_execucao(self, exec_id, status, total_bruto, total_salvo, erro_mensagem=""):
        session = self.get_session()
        try:
            execucao = session.query(ExecucaoPipeline).filter(ExecucaoPipeline.id == exec_id).first()
            if execucao:
                execucao.fim = datetime.utcnow()
                execucao.status = status
                execucao.total_coletado = total_bruto
                execucao.total_classificado = total_salvo
                execucao.erro_mensagem = erro_mensagem
                session.commit()
        finally:
            session.close()

    def salvar_candidato(self, username, dados):
        session = self.get_session()
        try:
            candidato = session.query(Candidato).filter(Candidato.username == username).first()
            if not candidato:
                candidato = Candidato(username=username)
                session.add(candidato)
            
            candidato.nome_completo = dados.get('nome_completo', candidato.nome_completo)
            candidato.bio = dados.get('bio', candidato.bio)
            candidato.cargo = dados.get('cargo', candidato.cargo)
            candidato.sexo = dados.get('sexo', candidato.sexo)
            candidato.raca = dados.get('raca', candidato.raca)
            candidato.estado = dados.get('estado', candidato.estado)
            candidato.partido = dados.get('partido', candidato.partido)
            candidato.ideologia = dados.get('ideologia', candidato.ideologia)
            candidato.seguidores = dados.get('seguidores', candidato.seguidores)
            
            session.commit()
            session.refresh(candidato)
            return candidato
        finally:
            session.close()

    def salvar_comentario(self, candidato_id, dados):
        session = self.get_session()
        try:
            id_externo = dados.get('id_externo')
            post_id = dados.get('post_id')
            
            # Verifica se o comentário já existe para evitar duplicidade
            existente = session.query(Comentario).filter(
                Comentario.id_externo == id_externo,
                Comentario.post_id == post_id
            ).first()
            
            if existente:
                return existente
                
            comentario = Comentario(
                candidato_id=candidato_id,
                id_externo=id_externo,
                post_id=post_id,
                autor_username=dados.get('autor_username'),
                texto_bruto=dados.get('texto_bruto'),
                texto_limpo=dados.get('texto_limpo'),
                data_publicacao=dados.get('data_publicacao'),
                likes=dados.get('likes', 0)
            )
            session.add(comentario)
            session.commit()
            session.refresh(comentario)
            return comentario
        finally:
            session.close()

    def salvar_classificacao(self, comentario_id, dados):
        session = self.get_session()
        try:
            classificacao = session.query(Classificacao).filter(Classificacao.comentario_id == comentario_id).first()
            if not classificacao:
                classificacao = Classificacao(comentario_id=comentario_id)
                session.add(classificacao)
                
            classificacao.categoria_odio = dados.get('categoria_odio')
            classificacao.score = dados.get('score')
            classificacao.confianca = dados.get('confianca')
            classificacao.modelo_versao = dados.get('modelo_versao')
            
            session.commit()
            session.refresh(classificacao)
            return classificacao
        finally:
            session.close()
