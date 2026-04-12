# memoria.py
import json
import os
from datetime import datetime
from typing import Optional, List

class MemoriaExecucao:
    def __init__(self, arquivo="execucao_memoria.json"):
        self.arquivo = arquivo
        self.dados = self._carregar()

    def _carregar(self):
        if os.path.exists(self.arquivo):
            try:
                with open(self.arquivo, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return self._criar_padrao()
        return self._criar_padrao()

    def _criar_padrao(self):
        return {
            "versao": 1,
            "ultima_execucao": None,
            "perfis": {}
        }

    def salvar(self):
        with open(self.arquivo, 'w', encoding='utf-8') as f:
            json.dump(self.dados, f, ensure_ascii=False, indent=2)

    def registrar_execucao(self):
        self.dados["ultima_execucao"] = datetime.now().isoformat()
        self.salvar()

    def get_perfil_memoria(self, perfil: str) -> dict:
        """Retorna os dados salvos para um perfil, ou um dicionário vazio"""
        return self.dados["perfis"].get(perfil, {})

    def get_ultimo_post_id(self, perfil: str) -> Optional[str]:
        return self.get_perfil_memoria(perfil).get("ultimo_post_id")

    def get_ultimo_timestamp(self, perfil: str) -> Optional[datetime]:
        ts = self.get_perfil_memoria(perfil).get("ultimo_comentario_timestamp")
        if ts:
            return datetime.fromisoformat(ts)
        return None

    def get_posts_coletados(self, perfil: str) -> List[str]:
        return self.get_perfil_memoria(perfil).get("posts_coletados", [])

    def atualizar_perfil(self, perfil: str, ultimo_post_id: str = None,
                         ultimo_timestamp: datetime = None, post_coletado: str = None):
        if perfil not in self.dados["perfis"]:
            self.dados["perfis"][perfil] = {
                "ultimo_post_id": None,
                "ultimo_comentario_timestamp": None,
                "posts_coletados": [],
                "total_comentarios_coletados": 0
            }
        p = self.dados["perfis"][perfil]
        if ultimo_post_id:
            p["ultimo_post_id"] = ultimo_post_id
        if ultimo_timestamp:
            p["ultimo_comentario_timestamp"] = ultimo_timestamp.isoformat()
        if post_coletado and post_coletado not in p["posts_coletados"]:
            p["posts_coletados"].append(post_coletado)
        self.salvar()

    def incrementar_total_comentarios(self, perfil: str, quantidade: int):
        if perfil not in self.dados["perfis"]:
            self.dados["perfis"][perfil] = {
                "ultimo_post_id": None,
                "ultimo_comentario_timestamp": None,
                "posts_coletados": [],
                "total_comentarios_coletados": 0
            }
        self.dados["perfis"][perfil]["total_comentarios_coletados"] += quantidade
        self.salvar()