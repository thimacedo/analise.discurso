"""
PASA v30 - Quality Gate v2: Filtro pesado contra artefatos de UI e lixo do scraper
"""
import re

def is_valid_comment(text: str, author: str = "") -> bool:
    if not text or not isinstance(text, str):
        return False
    
    clean_text = re.sub(r'\s+', ' ', text).strip()
    
    # REGRA 1: Rejeita autores hasheados ou IDs puros (Ex: @261704639352628, @DX0c7G3jmWf)
    if author and re.match(r'^[0-9]+$', author):
        return False
    if author and re.match(r'^[A-Za-z0-9]{10,}$', author) and not re.search(r'[aeiou]', author.lower()):
        return False
        
    # REGRA 2: Rejeita artefatos de UI do Instagram
    if re.search(r'(editado\s*•?\s*\d+\s*h|responder\s*\d+h|curtido por)', clean_text, re.IGNORECASE):
        return False
    if re.search(r'(e outros \d+|e mais \d+)', clean_text, re.IGNORECASE):
        return False
        
    # REGRA 3: Rejeita strings de sujeira de contatos/URI
    if re.search(r'(upload de contatos|não usuários|contatos e não)', clean_text, re.IGNORECASE):
        return False
        
    # REGRA 4: Rejeita menções soltas ou texto curto demais
    if len(clean_text.split()) < 3:
        return False
    if re.match(r'^(@[\w.]+\s*)+$', clean_text):
        return False
        
    # REGRA 5: Rejeita emojis soltos
    if re.match(r'^([\W_]\s*)+$', clean_text):
        return False
        
    return True
