import json
import logging
import time
import re
import os
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger("sentinela-forensics")

# --- Matriz TaxonÃ´mica PASA v42 (MTAD) ---
VALID_CATEGORIES = [
    "ODIO_IDENTITARIO",
    "VIOLENCIA_GENERO",
    "AMEACA",
    "ATAQUE_INSTITUCIONAL",
    "RIGOR_CRIMINAL",
    "INSULTO_AD_HOMINEM",
    "NEUTRO"
]

class PasaForensicsService:
    """
    ServiÃ§o Centralizado de Peritagem Forense PASA v42.
    Gerencia prompts baseados no MCF v2.0, parsing e auditoria CCF.
    """

    VERSION = "42.1.0"

    def __init__(self):
        self.manual_path = "docs/forensics/MANUAL_CLASSIFICACAO_FORENSE_v2.md"
        self.forbidden_terms = {
            re.compile(r'\bper[Ã­i]cia(?:s)?\b', re.IGNORECASE): "anÃ¡lise / relatÃ³rio",
            re.compile(r'\bper[Ã­i]to(?:s|as|a)?\b', re.IGNORECASE): "analista",
            re.compile(r'\bpericial\b', re.IGNORECASE): "analÃ­tica",
            re.compile(r'\bforense(?:s)?\b', re.IGNORECASE): "estratÃ©gica",
            re.compile(r'\bprova(?:s)?\b', re.IGNORECASE): "evidÃªncias situacionais",
            re.compile(r'\blaudo(?:s)?\b', re.IGNORECASE): "dossiÃª"
        }

    def _load_manual(self) -> str:
        """Carrega o manual MCF v2.0 do disco."""
        try:
            # Tenta caminhos relativos diferentes dependendo de onde o processo Ã© iniciado
            paths = [self.manual_path, f"../{self.manual_path}", f"E:/Projetos/sentinela-democratica/{self.manual_path}"]
            for p in paths:
                if os.path.exists(p):
                    with open(p, 'r', encoding='utf-8') as f:
                        return f.read()
            return "AVISO: Manual MCF v2.0 nÃ£o encontrado. Use a taxonomia MTAD e o CCF Framework."
        except Exception as e:
            logger.error(f"Erro ao carregar manual: {e}")
            return "ERRO ao carregar Manual MCF v2.0."

    def get_system_prompt(self) -> str:
        """Retorna o System Prompt baseado no MCF v2.0 definitivo."""
        manual = self._load_manual()
        return f"""
VocÃª Ã© um Analista Forense LinguÃ­stico do Sistema Sentinela DemocrÃ¡tica.
Siga RIGOROSAMENTE o manual abaixo para classificar os comentÃ¡rios.

{manual}

IMPORTANTE: Toda resposta DEVE ser um JSON vÃ¡lido seguindo o Contrato de Dados (SeÃ§Ã£o 7 do Manual).
"""

    def parse_verdict(self, raw_text: str) -> Dict[str, Any]:
        """Parser resiliente para respostas de IA (MCF v2.0 Pattern)."""
        try:
            # Limpeza de markdown
            clean = raw_text.strip()
            if "```json" in clean:
                clean = clean.split("```json")[1].split("```")[0]
            elif "```" in clean:
                clean = clean.split("```")[1].split("```")[0]

            clean = clean.strip()
            data = json.loads(clean)

            # Mapeamento do JSON da IA para o Schema do Supabase
            cat = str(data.get("categoria_ia", data.get("category", "NEUTRO"))).upper().strip()
            if cat not in VALID_CATEGORIES:
                cat = "NEUTRO"

            # Determina o rotulo (is_hate)
            rotulo = data.get("rotulo", "not_hate")
            is_hate = True if rotulo == "hate" else False
            if cat != "NEUTRO": is_hate = True # Garantia forense

            return {
                "id": data.get("id"),
                "category": cat,
                "categoria_ia": cat,
                "is_hate": is_hate,
                "rotulo": "hate" if is_hate else "not_hate",
                "direcao_odio": data.get("direcao_odio"),
                "ccf_density": float(data.get("ccf_density", 0.0)),
                "ccf_sync": float(data.get("ccf_sync", 0.0)),
                "ccf_performativity": float(data.get("ccf_performativity", 0.0)),
                "confidence": float(data.get("confianca_ia", data.get("confidence", 0.0))),
                "confianca_ia": float(data.get("confianca_ia", data.get("confidence", 0.0))),
                "reason": data.get("reason", "AnÃ¡lise PASA v42"),
                "pasa_version": self.VERSION
            }
        except Exception as e:
            logger.error(f"[Forensics] Erro de parsing MCF v2.0: {e}")
            return {
                "categoria_ia": "NEUTRO",
                "is_hate": False,
                "rotulo": "not_hate",
                "confianca_ia": 0.0,
                "reason": f"Erro de parser: {str(e)}"
            }

    def audit_terms(self, text: str) -> Tuple[bool, List[Dict]]:
        """Auditoria terminolÃ³gica para conformidade jurÃ­dica PASA."""
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
            "category": verdict.get("categoria_ia", "NEUTRO"),
            "is_hate": verdict.get("is_hate", False),
            "confidence": verdict.get("confianca_ia", 0.0),
            "text_preview": text[:100] + "..." if len(text) > 100 else text,
            "reason": verdict.get("reason", ""),
            "pasa_version": verdict.get("pasa_version", self.VERSION)
        }
        logger.info(f"âš–ï¸ [PASA AUDIT] {engine.upper()} | {verdict.get('categoria_ia', 'NEUTRO')} | {latency:.2f}s | {verdict.get('reason', '')}")
        return log_entry

# Singleton para acesso fÃ¡cil
forensics_service = PasaForensicsService()
