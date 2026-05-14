# core/schemas.py
from pydantic import BaseModel, field_validator
from typing import Literal, Optional
from datetime import datetime
import re

class CommentPayload(BaseModel):
    id_externo: str
    candidato_id: str
    post_id: str
    autor_username: str
    texto_bruto: str
    data_publicacao: str # Mantido como string para compatibilidade com o formato do IG, validado internamente
    categoria_ia: Literal["NEUTRO", "AMEACA", "ODIO_IDENTITARIO", "VIOLENCIA_GENERO", "RIGOR_CRIMINAL", "INSULTO_AD_HOMINEM", "ATAQUE_INSTITUCIONAL"]
    is_hate: bool
    plataforma: Literal["INSTAGRAM", "TWITTER", "YOUTUBE"]
    mined: Optional[bool] = True
    confianca_ia: Optional[float] = 0.60
    processado_ia: Optional[bool] = True

    @field_validator("texto_bruto")
    @classmethod
    def rejeitar_lixo_ui(cls, v):
        # Lista de ruídos baseada no Filtro Nível 3 e nas observações do usuário
        ruidos_estaticos = [
            "upload de contatos", 
            "não usuários", 
            "há 9 horas", 
            "e outros", 
            "ver tradução", 
            "ver comentários", 
            "responder",
            "página inicial",
            "notificações"
        ]
        
        v_lower = v.lower().strip()
        
        # 1. Check substrings estáticas
        if any(r in v_lower for r in ruidos_estaticos):
            raise ValueError(f"Texto de UI estático detectado: {v[:50]}")
            
        # 2. Check Padrões Dinâmicos (Regex)
        dynamic_patterns = [
            r'^há \d+ (hora|min|dia)',
            r'^e outros \d+$',
            r'^upload de contatos',
            r'^\d+ ponto(s)? de coleta',
            r'^\d+(\.\d+)? visualizaç(ão|ões)$'
        ]
        
        if any(re.match(p, v_lower) for p in dynamic_patterns):
            raise ValueError(f"Padrão dinâmico de UI detectado: {v[:50]}")

        # 3. Validação de tamanho mínimo
        if len(v.strip()) < 2:
            raise ValueError("Texto excessivamente curto (ruído ou emoji isolado)")

        return v.strip()

    @field_validator("autor_username")
    @classmethod
    def validar_username(cls, v):
        # Usernames do IG não têm espaços e geralmente são menores que 30 chars
        if " " in v or len(v) > 30:
            return "public_user"
        return v
