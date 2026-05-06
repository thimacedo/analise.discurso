import json
import logging
import time
import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger("sentinela-forensics")

# --- Matriz Taxonômica PASA v16.4 (Centralizada) ---
VALID_CATEGORIES = [
    "NEUTRO",
    "ODIO_IDENTITARIO",   # Xenofobia, racismo, regionalismo
    "VIOLENCIA_GENERO",   # Misoginia, ofensas à condição feminina
    "AMEACA",             # Incitação a dano físico ou morte
    "INSULTO_AD_HOMINEM", # Desumanização: lixo, rato, verme, escória
    "ATAQUE_INSTITUCIONAL",# Deslegitimação de órgãos como STF/TSE
    "RIGOR_CRIMINAL",     # Imputação de crime sem prova: ladrão, corrupto
    "XENOFOBIA_REGIONAL", # Específico para ataques a regiões (ex: Nordeste)
    "MILICIA_DIGITAL"     # Ataques coordenados e desinformação
]

class PasaForensicsService:
    """
    Serviço Centralizado de Peritagem Forense PASA v16.4.
    Gerencia prompts, parsing e auditoria de classificações de ódio.
    """
    
    VERSION = "16.4.1"

    def __init__(self):
        self.forbidden_terms = {
            re.compile(r'\bper[íi]cia(?:s)?\b', re.IGNORECASE): "análise / relatório",
            re.compile(r'\bper[íi]to(?:s|as|a)?\b', re.IGNORECASE): "analista",
            re.compile(r'\bpericial\b', re.IGNORECASE): "analítica",
            re.compile(r'\bforense(?:s)?\b', re.IGNORECASE): "estratégica",
            re.compile(r'\bprova(?:s)?\b', re.IGNORECASE): "evidências situacionais",
            re.compile(r'\blaudo(?:s)?\b', re.IGNORECASE): "dossiê"
        }

    def get_system_prompt(self) -> str:
        """Retorna o System Prompt padronizado para o Protocolo PASA."""
        return f"""
Você é um Perito em Linguística Forense do Sistema Sentinela Democrática.
Sua missão é classificar o texto segundo o Protocolo PASA v{self.VERSION}.

REGRAS DE OURO:
1. NEUTRO: Críticas administrativas, discordância política civilizada e debate de ideias NÃO são ódio.
2. PERFORMATIVIDADE: Analise se o discurso busca anular a cidadania ou desumanizar o alvo.
3. RIGOR: Imputação de crimes (ladrão, corrupto) sem contexto jornalístico é RIGOR_CRIMINAL e deve ser marcado como is_hate: true.
4. DESUMANIZAÇÃO: Termos como 'lixo', 'escória', 'rato' são INSULTO_AD_HOMINEM e SEMPRE são is_hate: true.

QUALQUER classificação em categorias PASA (exceto NEUTRO) deve, por padrão, resultar em "is_hate": true.

CATEGORIAS PERMITIDAS:
{", ".join(VALID_CATEGORIES)}

FORMATO DE SAÍDA (JSON ESTRITAMENTE):
{{
  "category": "CATEGORIA",
  "confidence": 0.95,
  "is_hate": true,
  "reason": "Explicação técnica curta",
  "evidence": ["termo1", "termo2"],
  "pasa_version": "{self.VERSION}"
}}
"""

    def parse_verdict(self, raw_text: str) -> Dict[str, Any]:
        """Parser resiliente para respostas de IA (Diamond Pattern)."""
        try:
            # Limpeza de markdown e ruídos
            clean = raw_text.strip()
            if "```json" in clean:
                clean = clean.split("```json")[1].split("```")[0]
            elif "```" in clean:
                clean = clean.split("```")[1].split("```")[0]
            
            clean = clean.strip()
            data = json.loads(clean)
            
            # Normalização da categoria
            cat = str(data.get("category", "NEUTRO")).upper().strip()
            if cat not in VALID_CATEGORIES:
                # Fallback inteligente
                if "XENOFOBIA" in cat: cat = "XENOFOBIA_REGIONAL"
                elif "GENERO" in cat or "MISOGINIA" in cat: cat = "VIOLENCIA_GENERO"
                elif "INSTITUCIONAL" in cat or "STF" in cat: cat = "ATAQUE_INSTITUCIONAL"
                else: cat = "NEUTRO"
            
            return {
                "category": cat,
                "confidence": float(data.get("confidence", 0.0)),
                "is_hate": bool(data.get("is_hate", False)),
                "reason": data.get("reason", "Análise automatizada PASA"),
                "evidence": data.get("evidence", []),
                "pasa_version": data.get("pasa_version", self.VERSION),
                "raw_forensic_trace": clean
            }
        except Exception as e:
            logger.error(f"[Forensics] Erro de parsing: {e} | Raw: {raw_text[:200]}")
            return {
                "category": "NEUTRO",
                "confidence": 0.0,
                "is_hate": False,
                "reason": f"Erro de parser forense: {str(e)}",
                "evidence": [],
                "pasa_version": self.VERSION,
                "raw_forensic_trace": raw_text
            }

    def audit_terms(self, text: str) -> Tuple[bool, List[Dict]]:
        """Auditoria terminológica para conformidade jurídica PASA."""
        violations = []
        for pattern, replacement in self.forbidden_terms.items():
            for match in pattern.finditer(text):
                violations.append({
                    'found_term': match.group(),
                    'replacement': replacement
                })
        return len(violations) == 0, violations

    def log_audit(self, text: str, verdict: Dict[str, Any], engine: str, latency: float):
        """Registra o evento de peritagem para auditoria futura."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "engine": engine,
            "latency": latency,
            "category": verdict["category"],
            "is_hate": verdict["is_hate"],
            "confidence": verdict["confidence"],
            "text_preview": text[:100] + "..." if len(text) > 100 else text,
            "reason": verdict["reason"],
            "pasa_version": verdict["pasa_version"]
        }
        logger.info(f"⚖️ [PASA AUDIT] {engine.upper()} | {verdict['category']} | {latency:.2f}s | {verdict['reason']}")
        return log_entry

# Singleton para acesso fácil
forensics_service = PasaForensicsService()
