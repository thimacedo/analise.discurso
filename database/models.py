from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Candidato(Base):
    __tablename__ = "candidatos"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    nome_completo = Column(String(200))
    bio = Column(Text)
    cargo = Column(String(100))
    sexo = Column(String(20))
    raca = Column(String(50))
    estado = Column(String(50))
    partido = Column(String(50), index=True)
    ideologia = Column(String(50))
    seguidores = Column(Integer)
    criado_em = Column(DateTime, default=datetime.utcnow)
    atualizado_em = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    comentarios = relationship("Comentario", back_populates="candidato")


class Comentario(Base):
    __tablename__ = "comentarios"
    
    id = Column(Integer, primary_key=True, index=True)
    id_externo = Column(String(200), unique=True, index=True)
    candidato_id = Column(Integer, ForeignKey("candidatos.id"), index=True)
    post_id = Column(String(200), index=True)
    autor_username = Column(String(100), index=True)
    texto_bruto = Column(Text, nullable=False)
    texto_limpo = Column(Text)
    data_coleta = Column(DateTime, default=datetime.utcnow)
    data_publicacao = Column(DateTime, index=True)
    likes = Column(Integer, default=0)
    
    candidato = relationship("Candidato", back_populates="comentarios")
    classificacao = relationship("Classificacao", uselist=False, back_populates="comentario")
    
    __table_args__ = (
        Index('idx_comentario_data', 'data_publicacao'),
    )


class Classificacao(Base):
    __tablename__ = "classificacoes"
    
    id = Column(Integer, primary_key=True, index=True)
    comentario_id = Column(Integer, ForeignKey("comentarios.id"), unique=True, index=True)
    categoria_odio = Column(String(50), index=True)
    score = Column(Float, index=True)
    confianca = Column(Float)
    modelo_versao = Column(String(50))
    classificado_em = Column(DateTime, default=datetime.utcnow)
    validado_humanamente = Column(Boolean, default=False)
    validado_por = Column(String(100))
    revisado = Column(Boolean, default=False)
    alerta_enviado = Column(Boolean, default=False)
    alerta_lido = Column(Boolean, default=False)
    
    comentario = relationship("Comentario", back_populates="classificacao")


class ExecucaoPipeline(Base):
    __tablename__ = "execucoes_pipeline"
    
    id = Column(Integer, primary_key=True, index=True)
    inicio = Column(DateTime, default=datetime.utcnow)
    fim = Column(DateTime)
    status = Column(String(50), index=True)
    total_coletado = Column(Integer, default=0)
    total_classificado = Column(Integer, default=0)
    erro_mensagem = Column(Text)
    versao_sistema = Column(String(50))