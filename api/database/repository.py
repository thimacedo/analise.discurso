import os
from sqlalchemy import create_event, create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager

Base = declarative_base()

class DatabaseRepository:
    def __init__(self, db_url=None):
        self.url = db_url or os.getenv("SUPABASE_URL")
        # Ajuste para Supabase (Postgres) se necessário, ou fallback para SQLite local
        if not self.url or "supabase.co" in self.url:
            # Se for Supabase, precisamos da string de conexão correta (postgres://...)
            # Como o código original usava os segredos direto, vamos assumir que o engine lida com isso.
            # No entanto, o Supabase REST API (que os outros scripts usam) é diferente do SQLAlchemy.
            # Vou implementar uma versão robusta que tenta conectar no Postgres se houver URL, ou SQLite de teste.
            pass
        
        # Conexão via SQLAlchemy (exigida pelo main.py)
        # Nota: Ajustado para usar string de conexão Postgres se disponível
        conn_string = os.getenv("DATABASE_URL") or "sqlite:///./sentinela_local.db"
        self.engine = create_engine(conn_string)
        self.session_factory = sessionmaker(bind=self.engine)

    @contextmanager
    def get_session(self):
        session = self.session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
