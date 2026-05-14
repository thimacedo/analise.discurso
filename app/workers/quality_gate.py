"""
PASA v26 - Quality Gate: Filtro de sanidade na borda da coleta.
Evita que lixo textual chegue ao banco de dados e queime tokens da IA.
"""
import re

def is_valid_comment(text: str) -> bool:
    """Aplica regras rigorosas para determinar se um comentário tem valor analítico."""
    if not text or not isinstance(text, str):
        return False
    
    # Limpa espaços em branco excessivos e quebras de linha
    clean_text = re.sub(r'\s+', ' ', text).strip()
    
    # REGRA 1: Rejeita comentários curtos demais (Ex: "Ok", "👏", "13")
    if len(clean_text.split()) < 3:
        return False
        
    # REGRA 2: Rejeita artefatos de UI do Instagram (Ex: "lulaoficial Editado 4h")
    # Padrão comum em scrapers que pegam texto de botões ou timestamps
    if re.search(r'(editado\s*\d+\s*h|responder\s*\d+h|curtido por|ver tradução)', clean_text, re.IGNORECASE):
        return False
        
    # REGRA 3: Rejeita strings que são apenas menções (Ex: "@usuario @outro_usuario")
    if re.match(r'^(@[\w.]+\s*)+$', clean_text):
        return False
        
    # REGRA 4: Rejeita emojis soltos ou repetidos sem contexto (Ex: "❤️❤️❤️👏👏")
    # Se não houver caracteres alfanuméricos, rejeita
    if not re.search(r'[\w]', clean_text):
        return False
        
    return True
