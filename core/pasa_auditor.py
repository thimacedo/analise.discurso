import re
import asyncio
from typing import List, Dict, Tuple, Any
from core.ai_service import AIService 

class PASAAuditor:
    """
    Auditor Linguístico e Forense PASA v16.4.
    Realiza classificação de risco (IA) seguida de auditoria terminológica.
    """
    def __init__(self, ai_service_instance=None):
        if ai_service_instance is None:
            from core.ai_service import ai_service
            self.ai_service = ai_service
        else:
            self.ai_service = ai_service_instance
        self.forbidden_terms = {
            re.compile(r'\bper[íi]cia(?:s)?\b', re.IGNORECASE): "análise / relatório",
            re.compile(r'\bper[íi]to(?:s|as|a)?\b', re.IGNORECASE): "analista",
            re.compile(r'\bpericial\b', re.IGNORECASE): "analítica",
            re.compile(r'\bforense(?:s)?\b', re.IGNORECASE): "estratégica",
            re.compile(r'\bprova(?:s)?\b', re.IGNORECASE): "evidências situacionais",
            re.compile(r'\blaudo(?:s)?\b', re.IGNORECASE): "dossiê"
        }

    async def process(self, text: str) -> Dict[str, Any]:
        """Pipeline completo: Classifica (IA) e Audita (PASA v16.4)."""
        # 1. Classificação via IA
        classification = await self.ai_service.classify(text)
        
        # 2. Auditoria terminológica PASA
        is_compliant, violations = self.audit_text(text)
        
        return {
            "text": text,
            "category": classification.get("category"),
            "is_hate": classification.get("is_hate"),
            "classification": classification,
            "is_compliant": is_compliant,
            "violations": violations
        }

    def audit_text(self, text: str) -> Tuple[bool, List[Dict]]:
        violations = []
        for pattern, replacement in self.forbidden_terms.items():
            for match in pattern.finditer(text):
                violations.append({
                    'found_term': match.group(),
                    'replacement': replacement
                })
        return len(violations) == 0, violations
