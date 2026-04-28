from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Candidato(Base):
    __tablename__ = "candidatos"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    nome = Column(String)
    estado = Column(String)
    partido = Column(String, nullable=True)
    status_monitoramento = Column(String, default="Ativo")
    comentarios_totais_count = Column(Integer, default=0)
    comentarios_odio_count = Column(Integer, default=0)

class Comentario(Base):
    __tablename__ = "comentarios"
    id = Column(Integer, primary_key=True, index=True)
    id_externo = Column(String, unique=True, index=True)
    candidato_id = Column(Integer, ForeignKey("candidatos.id"))
    autor_username = Column(String, nullable=True)
    texto_bruto = Column(Text)
    texto_limpo = Column(Text, nullable=True)
    data_publicacao = Column(DateTime, nullable=True)
    data_coleta = Column(DateTime, default=datetime.utcnow)
    post_id = Column(String, index=True, nullable=True)
    url_post = Column(String, nullable=True)
    tipo_midia = Column(String, nullable=True)
    fonte_coleta = Column(String, nullable=True)
    processado_ia = Column(Boolean, default=False, index=True) # Status de Processamento
    sentimento = Column(String, nullable=True) # POS, NEG, NEU

class Classificacao(Base):
    __tablename__ = "classificacoes"
    id = Column(Integer, primary_key=True, index=True)
    comentario_id = Column(Integer, ForeignKey("comentarios.id"), unique=True)
    is_hate = Column(Boolean, default=False)
    categoria_pasa = Column(String, nullable=True)
    score = Column(Float, default=0.0)
    modelo_versao = Column(String)
    data_processamento = Column(DateTime, default=datetime.utcnow)
