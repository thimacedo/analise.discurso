from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Candidato(Base):
    __tablename__ = "candidatos"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    nome_completo = Column(String)
    partido = Column(String)
    cargo = Column(String)
    estado = Column(String)
    status_monitoramento = Column(String, default="Ativo")

class Comentario(Base):
    __tablename__ = "comentarios"
    id = Column(Integer, primary_key=True, index=True)
    id_externo = Column(String, unique=True)
    candidato_id = Column(Integer, ForeignKey("candidatos.id"))
    autor_username = Column(String)
    texto_bruto = Column(String)
    texto_limpo = Column(String)
    data_publicacao = Column(DateTime)
    data_coleta = Column(DateTime, default=datetime.utcnow)
    post_id = Column(String)

class Classificacao(Base):
    __tablename__ = "classificacoes"
    id = Column(Integer, primary_key=True, index=True)
    comentario_id = Column(Integer, ForeignKey("comentarios.id"))
    is_hate = Column(Boolean, default=False)
    categoria_odio = Column(String)
    score = Column(Float)
    modelo_versao = Column(String)
    data_processamento = Column(DateTime, default=datetime.utcnow)
