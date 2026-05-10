import re
from typing import Optional

def clean_comment(text: str, author_username: str) -> Optional[str]:
    """
    Limpa o texto do comentário e valida se ele não é apenas o nome do autor.
    Retorna None se o texto for inválido ou redundante.
    """
    if not text:
        return None
        
    text = text.strip()
    author_username = author_username.strip().replace('@', '')
    
    # Se o texto for idêntico ao username (com ou sem @), é lixo de seletor
    if text.lower() == author_username.lower() or text.lower() == f"@{author_username.lower()}":
        return None
        
    # Se o texto for muito curto (ex: apenas um emoji ou pontuação) e o seletor falhou
    if len(text) < 2:
        return None
        
    return text

class TextProcessor:
    """
    Processador de texto forense para análise de discurso.
    """
    def __init__(self):
        pass

    def clean_text(self, text: str, author: str = "") -> str:
        """Limpa o texto preservando a integridade para análise."""
        cleaned = clean_comment(text, author)
        return cleaned if cleaned else ""
