import re
from typing import List, Dict, Tuple, Any
from core.ai_service import AIService 

class PASAAuditor:
    """
    Auditor Linguístico e Forense PASA v16.4.
    Realiza classificação de risco (IA) seguida de auditoria terminológica.
    """
    def __init__(self):
        self.ai_service = AIService()
        self.forbidden_terms = {
            re.compile(r'\bper[íi]cia(?:s)?\b', re.IGNORECASE): "análise / relatório",
            re.compile(r'\bper[íi]to(?:s|as|a)?\b', re.IGNORECASE): "analista",
            re.compile(r'\bpericial\b', re.IGNORECASE): "analítica",
            re.compile(r'\bforense(?:s)?\b', re.IGNORECASE): "estratégica",
            re.compile(r'\bprova(?:s)?\b', re.IGNORECASE): "evidências situacionais",
            re.compile(r'\blaudo(?:s)?\b', re.IGNORECASE): "dossiê"
        }

    def process(self, text: str) -> Dict[str, Any]:
        """Pipeline completo: Classifica (IA) e Audita (PASA v16.4)."""
        # 1. Classificação via IA
        classification = self.ai_service.classify_discourse(text)
        
        # 2. Auditoria terminológica PASA
        is_compliant, violations = self.audit_terms(text)
        
        return {
            "text": text,
            "classification": classification,
            "is_compliant": is_compliant,
            "violations": violations
        }

    def audit_terms(self, text: str) -> Tuple[bool, List[Dict]]:
        violations = []
        for pattern, replacement in self.forbidden_terms.items():
            for match in pattern.finditer(text):
                violations.append({
                    'found': match.group(),
                    'replacement': replacement
                })
        return len(violations) == 0, violations
