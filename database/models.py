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
    autor_username = Column(String)
    texto_bruto = Column(Text)
    texto_limpo = Column(Text, nullable=True)
    data_publicacao = Column(DateTime)
    data_coleta = Column(DateTime, default=datetime.utcnow)
    post_id = Column(String, index=True)
    url_post = Column(String, nullable=True)
    tipo_midia = Column(String, nullable=True)
    fonte_coleta = Column(String, nullable=True) # PASA: Rastreabilidade
    is_hate = Column(Boolean, default=False)
    classificacao_pasa = Column(String, nullable=True)
    raw_metadata = Column(JSON, nullable=True)
