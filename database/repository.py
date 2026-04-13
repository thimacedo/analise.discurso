# database/repository.py
import sqlite3
import os
from datetime import datetime

class SimpleObject:
    """Classe auxiliar para simular objetos de banco com .id"""
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class DatabaseRepository:
    def __init__(self, db_path="analise_discurso.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def criar_tabelas(self):
        self.cursor.executescript("""
            CREATE TABLE IF NOT EXISTS execucoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_inicio TEXT,
                data_fim TEXT,
                status TEXT,
                total_bruto INTEGER,
                total_salvo INTEGER
            );
            CREATE TABLE IF NOT EXISTS candidatos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                cargo TEXT,
                sexo TEXT,
                raca TEXT,
                estado TEXT,
                partido TEXT,
                ideologia TEXT,
                data_atualizacao TEXT
            );
            CREATE TABLE IF NOT EXISTS comentarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                candidato_id INTEGER,
                id_externo TEXT,
                post_id TEXT,
                autor_username TEXT,
                texto_bruto TEXT,
                texto_limpo TEXT,
                data_publicacao TEXT,
                likes INTEGER,
                UNIQUE(id_externo, post_id),
                FOREIGN KEY(candidato_id) REFERENCES candidatos(id)
            );
            CREATE TABLE IF NOT EXISTS classificacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                comentario_id INTEGER,
                categoria_odio TEXT,
                score REAL,
                confianca REAL,
                modelo_versao TEXT,
                FOREIGN KEY(comentario_id) REFERENCES comentarios(id)
            );
        """)
        self.conn.commit()

    def iniciar_execucao(self):
        self.cursor.execute("INSERT INTO execucoes (data_inicio, status) VALUES (?, ?)", (datetime.now().isoformat(), "EM_ANDAMENTO"))
        self.conn.commit()
        return SimpleObject(id=self.cursor.lastrowid)

    def finalizar_execucao(self, exec_id, status, total_bruto, total_salvo):
        self.cursor.execute("UPDATE execucoes SET data_fim=?, status=?, total_bruto=?, total_salvo=? WHERE id=?",
                           (datetime.now().isoformat(), status, total_bruto, total_salvo, exec_id))
        self.conn.commit()

    def salvar_candidato(self, username, dados):
        self.cursor.execute("""
            INSERT INTO candidatos (username, cargo, sexo, raca, estado, partido, ideologia, data_atualizacao)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(username) DO UPDATE SET cargo=?, sexo=?, raca=?, estado=?, partido=?, ideologia=?, data_atualizacao=?
        """, (username, dados.get('cargo'), dados.get('sexo'), dados.get('raca'), 
              dados.get('estado'), dados.get('partido'), dados.get('ideologia'), datetime.now().isoformat(),
              dados.get('cargo'), dados.get('sexo'), dados.get('raca'), 
              dados.get('estado'), dados.get('partido'), dados.get('ideologia'), datetime.now().isoformat()))
        self.conn.commit()
        
        self.cursor.execute("SELECT id FROM candidatos WHERE username=?", (username,))
        row = self.cursor.fetchone()
        return SimpleObject(id=row['id'])

    def salvar_comentario(self, candidato_id, dados):
        try:
            self.cursor.execute("""
                INSERT INTO comentarios (candidato_id, id_externo, post_id, autor_username, texto_bruto, texto_limpo, data_publicacao, likes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (candidato_id, dados.get('id_externo'), dados.get('post_id'), 
                  dados.get('autor_username'), dados.get('texto_bruto'), dados.get('texto_limpo'),
                  dados.get('data_publicacao'), dados.get('likes', 0)))
            self.conn.commit()
            return SimpleObject(id=self.cursor.lastrowid)
        except sqlite3.IntegrityError:
            # Comentário já existe no banco, ignora
            return None

    def salvar_classificacao(self, comentario_id, dados):
        self.cursor.execute("""
            INSERT INTO classificacoes (comentario_id, categoria_odio, score, confianca, modelo_versao)
            VALUES (?, ?, ?, ?, ?)
        """, (comentario_id, dados.get('categoria_odio'), dados.get('score'), dados.get('confianca'), dados.get('modelo_versao')))
        self.conn.commit()

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()
