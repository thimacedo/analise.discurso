from datetime import datetime
from typing import List, Optional, Dict
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from .models import Base, Candidato, Comentario, Classificacao, ExecucaoPipeline
import os
from dotenv import load_dotenv

load_dotenv()

class DatabaseRepository:
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/odio_politica')
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def criar_tabelas(self):
        Base.metadata.create_all(bind=self.engine)
        
    def get_session(self):
        return self.SessionLocal()
    
    def salvar_candidato(self, username: str, dados: Dict) -> Candidato:
        with self.get_session() as session:
            candidato = session.query(Candidato).filter(Candidato.username == username).first()
            
            if not candidato:
                candidato = Candidato(username=username)
            
            for chave, valor in dados.items():
                if hasattr(candidato, chave):
                    setattr(candidato, chave, valor)
            
            session.add(candidato)
            session.commit()
            session.refresh(candidato)
            return candidato
    
    def salvar_comentario(self, candidato_id: int, dados: Dict) -> Optional[Comentario]:
        with self.get_session() as session:
            try:
                comentario = Comentario(
                    candidato_id=candidato_id,
                    id_externo=dados.get('id_externo'),
                    post_id=dados.get('post_id'),
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
            except IntegrityError:
                session.rollback()
                return None
    
    def salvar_classificacao(self, comentario_id: int, dados: Dict) -> Classificacao:
        with self.get_session() as session:
            classificacao = session.query(Classificacao).filter(Classificacao.comentario_id == comentario_id).first()
            
            if not classificacao:
                classificacao = Classificacao(comentario_id=comentario_id)
            
            classificacao.categoria_odio = dados.get('categoria_odio')
            classificacao.score = dados.get('score')
            classificacao.confianca = dados.get('confianca')
            classificacao.modelo_versao = dados.get('modelo_versao', 'v1.0')
            
            session.add(classificacao)
            session.commit()
            session.refresh(classificacao)
            return classificacao
    
    def iniciar_execucao(self) -> ExecucaoPipeline:
        with self.get_session() as session:
            execucao = ExecucaoPipeline(status='INICIADO')
            session.add(execucao)
            session.commit()
            session.refresh(execucao)
            return execucao
    
    def finalizar_execucao(self, execucao_id: int, status: str, total_coletado: int, total_classificado: int, erro: str = None):
        with self.get_session() as session:
            execucao = session.query(ExecucaoPipeline).get(execucao_id)
            execucao.fim = datetime.utcnow()
            execucao.status = status
            execucao.total_coletado = total_coletado
            execucao.total_classificado = total_classificado
            execucao.erro_mensagem = erro
            session.commit()
    
    def estatisticas_resumo(self) -> Dict:
        with self.get_session() as session:
            total_comentarios = session.query(func.count(Comentario.id)).scalar()
            total_odio = session.query(func.count(Classificacao.id)).filter(Classificacao.categoria_odio != 'neutro').scalar()
            taxa_odio = round((total_odio / total_comentarios * 100), 1) if total_comentarios > 0 else 0
            
            # Métricas exatas do dashboard ForenseNet
            total_candidatos = session.query(func.count(Candidato.id)).scalar()
            revisao_pendente = session.query(func.count(Classificacao.id)).filter(Classificacao.revisado == False).scalar()
            alertas_nao_lidos = session.query(func.count(Classificacao.id)).filter(Classificacao.alerta_enviado == True, Classificacao.alerta_lido == False).scalar()
            jobs_recentes = session.query(func.count(ExecucaoPipeline.id)).filter(ExecucaoPipeline.inicio >= datetime.utcnow().replace(hour=0, minute=0, second=0)).scalar()
            confianca_media = session.query(func.avg(Classificacao.confianca)).scalar() or 0
            severidade_alta = session.query(func.count(Classificacao.id)).filter(Classificacao.score >= 0.7).scalar()
            
            return {
                'total_comentarios': total_comentarios,
                'total_discurso_odio': total_odio,
                'percentual_odio': taxa_odio,
                'candidatos_ativos': total_candidatos,
                'revisao_pendente': revisao_pendente,
                'alertas_nao_lidos': alertas_nao_lidos,
                'jobs_recentes_24h': jobs_recentes,
                'confianca_media': round(confianca_media * 100, 1),
                'severidade_alta': severidade_alta
            }
