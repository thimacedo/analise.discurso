import re
from typing import Dict, List

class PASAAuditor:
    """
    Auditor to ensure compliance with PASA v16.4 terminology constraints.
    Replaces forbidden terms with approved alternatives.
    """
    
    FORBIDDEN_MAPPING = {
        r'\bper[íi]cia(s)?\b': 'Análise',
        r'\bpericiar\b': 'Analisar',
        r'\bperito(s)?\b': 'Analista',
        r'\bpericial\b': 'Analítica',
        r'\bpericiais\b': 'Analíticas',
        r'\bforense(s)?\b': 'Estratégica / Situacional',
        r'\bprova(s)?\b': 'Dados / Sinais'
    }

    def __init__(self):
        # Pre-compile regexes for performance
        self._compiled_rules = [
            (re.compile(pattern, re.IGNORECASE), replacement)
            for pattern, replacement in self.FORBIDDEN_MAPPING.items()
        ]

    def audit_text(self, text: str) -> Dict:
        """
        Scans text for forbidden terms and returns an audit report.
        """
        if not text:
            return {"is_compliant": True, "violations": []}

        violations = []
        is_compliant = True

        for pattern, replacement in self._compiled_rules:
            for match in pattern.finditer(text):
                is_compliant = False
                found_term = match.group(0)
                
                # Get a snippet of context (up to 30 chars around the match)
                start_idx = max(0, match.start() - 30)
                end_idx = min(len(text), match.end() + 30)
                context = text[start_idx:end_idx].strip()

                violations.append({
                    "found_term": found_term,
                    "suggested_replacement": replacement,
                    "context": f"...{context}..."
                })

        return {
            "is_compliant": is_compliant,
            "violations": violations
        }
