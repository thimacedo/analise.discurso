import re
import logging
from typing import List, Dict

# Configuração básica de logging para o Rick não ficar cego
logging.basicConfig(
    filename='logs/security_alerts.log',
    level=logging.WARNING,
    format='%(asctime)s - SECURITY ALERT - %(message)s'
)

class SecurityScanner:
    """
    Escaneador de segurança ultra-competente. 
    Detecta PII e segredos antes que o Jerry poste no GitHub.
    """
    def __init__(self):
        # Compilando as regexes para nao ser um homem das cavernas
        self.patterns = {
            'CPF': re.compile(r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b'),
            'Phone_BR': re.compile(r'\b(?:\+?55\s?)?(?:\(?\d{2}\)?\s?)?\d{4,5}-?\d{4}\b'),
            'Credit_Card': re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'),
            'API_Key': re.compile(r'\b[a-zA-Z0-9]{32,}\b'),
            'SSH_Private_Key': re.compile(r'-----BEGIN (?:RSA|OPENSSH) PRIVATE KEY-----'),
        }

    def scan_text(self, text: str) -> List[Dict]:
        """
        Escaneia o texto em busca de vazamentos. Retorna uma lista de achados.
        """
        findings = []
        for label, pattern in self.patterns.items():
            matches = pattern.finditer(text)
            for match in matches:
                findings.append({
                    'type': label,
                    'start': match.start(),
                    'end': match.end(),
                    'value': match.group() if label != 'SSH_Private_Key' else "[SENSITIVE_KEY_HEADER]"
                })
                logging.warning(f"Detected {label} at positions {match.start()}-{match.end()}")
        
        return findings

    def mask_sensitive_data(self, text: str) -> str:
        """
        Redige os dados sensíveis. Substitui pela glória do Pickle Rick.
        """
        masked_text = text
        findings = self.scan_text(text)
        
        # Ordenar decrescente para não quebrar os índices durante a substituição
        for finding in sorted(findings, key=lambda x: x['start'], reverse=True):
            placeholder = f"[REDACTED_BY_PICKLE_RICK_{finding['type']}]"
            masked_text = masked_text[:finding['start']] + placeholder + masked_text[finding['end']:]
            
        return masked_text

if __name__ == "__main__":
    # Teste rápido de sanidade
    scanner = SecurityScanner()
    test_input = "Meu CPF é 123.456.789-00 e minha chave é abcdef1234567890abcdef1234567890"
    print(f"Original: {test_input}")
    print(f"Masked: {scanner.mask_sensitive_data(test_input)}")
