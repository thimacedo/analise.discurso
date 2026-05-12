
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import re
import logging
from typing import List, Dict

# Configuração básica de logging
logging.basicConfig(
    filename='logs/security_alerts.log',
    level=logging.WARNING,
    format='%(asctime)s - SECURITY ALERT - %(message)s'
)

class SecurityScanner:
    """
    Escaneador de segurança ultra-competente v2. 
    Blindagem total contra vazamento de dados sensíveis e credenciais.
    I'm Pickle Rick! 🥒
    """
    def __init__(self):
        # Regexes otimizadas para performance e precisão
        self.patterns = {
            'CPF': re.compile(r'\b(?:\d{3}\.\d{3}\.\d{3}-\d{2}|\d{11})\b'),
            'CNPJ': re.compile(r'\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b'),
            'Phone_BR': re.compile(r'\b(?:\+?55\s?)?(?:\(?\d{2}\)?\s?)?(?:9\d{4}|\d{4})-?\d{4}\b'),
            'Credit_Card': re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'),
            # Chaves de API mais específicas (Stripe, AWS, Google, etc)
            'Secret_Key': re.compile(r'\b(?:sk|pk|ak)_(?:live|test)_[a-zA-Z0-9]{20,}\b|'
                                    r'\bAKIA[A-Z0-9]{16}\b|'
                                    r'\bAIza[a-zA-Z0-9_-]{30,45}\b'),
            'SSH_Private_Key': re.compile(r'-----BEGIN (?:RSA|OPENSSH|DSA|EC) PRIVATE KEY-----'),
        }

    def scan_text(self, text: str) -> List[Dict]:
        """
        Escaneia o texto em busca de vazamentos. Retorna uma lista de achados.
        """
        findings = []
        if not text or not isinstance(text, str):
            return findings

        for label, pattern in self.patterns.items():
            matches = pattern.finditer(text)
            for match in matches:
                findings.append({
                    'type': label,
                    'start': match.start(),
                    'end': match.end(),
                    'value': match.group() if label != 'SSH_Private_Key' else "[PRIVATE_KEY_HEADER]"
                })
                logging.warning(f"Detected {label} at positions {match.start()}-{match.end()}")
        
        return findings

    def mask_sensitive_data(self, text: str) -> str:
        """
        Redige os dados sensíveis. Substitui pela glória do Pickle Rick.
        """
        if not text or not isinstance(text, str):
            return text

        masked_text = text
        findings = self.scan_text(text)
        
        # Ordenar decrescente para não quebrar os índices durante a substituição
        for finding in sorted(findings, key=lambda x: x['start'], reverse=True):
            placeholder = f"[REDACTED_{finding['type']}]"
            masked_text = masked_text[:finding['start']] + placeholder + masked_text[finding['end']:]
            
        return masked_text

if __name__ == "__main__":
    scanner = SecurityScanner()
    test_input = "Contato: 11988887777, CPF: 123.456.789-00, Key: AIzaSyB_1234567890abcdefghijklmnopqrstuv"
    print(f"Original: {test_input}")
    print(f"Masked: {scanner.mask_sensitive_data(test_input)}")
