import re
from typing import List, Dict, Tuple

class PASAAuditor:
    """
    Auditor Linguístico PASA v16.4.
    Inspeciona textos gerados pela IA ou relatórios para garantir que a terminologia
    seja estritamente situacional e não-forense, evitando passivos legais.
    I'm Pickle Rick! 🥒
    """
    def __init__(self):
        # Mapeamento de termos proibidos (regex) para sugestões de uso.
        # \b garante word-boundaries, suportando acentuação básica via \w se bem configurado,
        # mas para PT-BR é melhor focar na string exata ou variações.
        self.forbidden_terms = {
            re.compile(r'\bper[íi]cia(?:s)?\b', re.IGNORECASE): "análise / relatório / levantamento",
            re.compile(r'\bper[íi]to(?:s|as|a)?\b', re.IGNORECASE): "analista / pesquisador",
            re.compile(r'\bpericial\b', re.IGNORECASE): "analítica / situacional",
            re.compile(r'\bforense(?:s)?\b', re.IGNORECASE): "estratégica / situacional",
            re.compile(r'\bprova(?:s)?\b', re.IGNORECASE): "dados / evidências situacionais / sinais",
            re.compile(r'\blaudo(?:s)?\b', re.IGNORECASE): "relatório / dossiê / painel"
        }

    def audit_text(self, text: str) -> Tuple[bool, List[Dict]]:
        """
        Escaneia um texto. Retorna (is_compliant, lista_de_violacoes).
        """
        violations = []
        if not text or not isinstance(text, str):
            return True, violations

        for pattern, suggestion in self.forbidden_terms.items():
            for match in pattern.finditer(text):
                # Extrair um pouco de contexto (20 chars antes e depois)
                start_context = max(0, match.start() - 20)
                end_context = min(len(text), match.end() + 20)
                context = text[start_context:end_context].replace('\n', ' ').strip()
                
                violations.append({
                    'found_term': match.group(),
                    'suggested_replacement': suggestion,
                    'start': match.start(),
                    'end': match.end(),
                    'context': f"...{context}..."
                })

        is_compliant = len(violations) == 0
        return is_compliant, violations

if __name__ == "__main__":
    auditor = PASAAuditor()
    test_str = "A perícia concluiu que a prova forense indica que o perito assinou o laudo."
    compliant, issues = auditor.audit_text(test_str)
    print(f"Compliant: {compliant}")
    for issue in issues:
        print(f" - Encontrou: '{issue['found_term']}' | Sugestão: {issue['suggested_replacement']}")
