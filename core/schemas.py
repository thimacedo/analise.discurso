# core/schemas.py
from __future__ import annotations
from pydantic import BaseModel, field_validator, model_validator
from typing import Literal, Optional
from datetime import datetime
import re

# Categorias válidas do PASA — fonte única de verdade
CATEGORIAS_PASA = Literal[
    "NEUTRO",
    "AMEACA",
    "ODIO_IDENTITARIO",
    "VIOLENCIA_GENERO",
    "RIGOR_CRIMINAL",
    "INSULTO_AD_HOMINEM",
    "ATAQUE_INSTITUCIONAL",
]

# Ruídos de UI do Instagram conhecidos
_UI_NOISE = [
    "upload de contatos",
    "não usuários",
    "ver tradução",
    "ver comentários",
    "ver menos",
    "responder",
    "curtidas",
    "também da meta",
    "explorar",
    "notificações",
    "página inicial",
]

# Padrões temporais que o Instagram injeta como texto
_NOISE_PATTERNS = [
    re.compile(r"^há \d+ (hora|horas|min|mins|dia|dias|semana|semanas)$"),
    re.compile(r"^e outros \d+$"),
    re.compile(r"^\d+(\.\d+)? visualizaç(ão|ões)$"),
    re.compile(r"^\d+ de \w+ de \d{4}$"),  # "7 de setembro de 2025"
]

class CommentPayload(BaseModel):
    id_externo:     str
    candidato_id:   str
    post_id:        str
    autor_username: str
    texto_bruto:    str
    data_publicacao: Optional[str] = None # Mantido como str para compatibilidade com o formato do IG nos workers
    categoria_ia:   CATEGORIAS_PASA = "NEUTRO"
    is_hate:        bool = False
    confianca_ia:   float = 0.0
    processado_ia:  bool = True
    plataforma:     Literal["INSTAGRAM", "TWITTER", "YOUTUBE"] = "INSTAGRAM"
    mined:          bool = True
    worker_name:    str

    @field_validator("texto_bruto")
    @classmethod
    def rejeitar_lixo(cls, v: str) -> str:
        limpo = v.strip()

        if len(limpo) < 3:
            raise ValueError(f"Texto muito curto: '{limpo}'")

        lower = limpo.lower()
        if any(ruido in lower for ruido in _UI_NOISE):
            raise ValueError(f"Ruído de UI detectado: '{limpo[:60]}'")

        if any(p.match(lower) for p in _NOISE_PATTERNS):
            raise ValueError(f"Padrão temporal de UI detectado: '{limpo[:60]}'")

        return limpo

    @field_validator("confianca_ia")
    @classmethod
    def confianca_no_range(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"confianca_ia deve estar entre 0 e 1, recebido: {v}")
        return v

    @model_validator(mode="after")
    def is_hate_coerente(self) -> CommentPayload:
        # Se categoria é NEUTRO, is_hate não pode ser True
        if self.categoria_ia == "NEUTRO" and self.is_hate:
            self.is_hate = False
        # Se categoria é crítica, is_hate deve ser True
        criticas = {"AMEACA", "ODIO_IDENTITARIO", "VIOLENCIA_GENERO"}
        if self.categoria_ia in criticas and not self.is_hate:
            self.is_hate = True
        return self

class WorkerRunPayload(BaseModel):
    """Representa uma execução registrada no worker_runs."""
    worker_name:      str
    status:           Literal["running", "success", "failure"]
    items_processed:  int = 0
    items_rejected:   int = 0
    duration_ms:      Optional[int] = None
    error_message:    Optional[str] = None
    payload_snapshot: Optional[dict] = None
