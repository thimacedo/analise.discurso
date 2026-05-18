"""
PASA v31.1 - AI Classifier Engine v2.1: Mapeamento Real do Schema
"""
import os
import json
import google.generativeai as genai
from core.supabase_service import get_supabase_client

db = get_supabase_client()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

VALID_CATEGORIAS = [
    "Odio Identitario", 
    "Ameaca Politica", 
    "Discurso de Violencia", 
    "Ataque Pessoal", 
    "Apoio Politico", 
    "Neutro"
]

def get_gold_examples(limit=5):
    """Busca os exemplos do Padrão Ouro para Few-Shot Prompting."""
    try:
        response = db.table('audit_gold_standards')\
            .select('texto_original, rotulo_correto')\
            .order('created_at', desc=True)\
            .limit(limit)\
            .execute()
        return response.data if response.data else []
    except Exception:
        return []

def build_prompt(batch_comments):
    """Constrói o prompt exigindo mapeamento completo do schema real."""
    gold_examples = get_gold_examples()
    
    system_instruction = (
        "Você é um analista forense do Sentinela Democrática. "
        "Classifique os comentários a seguir e retorne um array JSON. Cada objeto deve conter:\n"
        "- 'id': o ID exato do comentário\n"
        "- 'rotulo': 'hate' ou 'not_hate'\n"
        "- 'categoria_ia': uma das categorias válidas\n"
        "- 'direcao_odio': se for 'hate', indique o grupo alvo (ex: 'Mulheres', 'Negros', 'LGBTQIA+', 'Opositores Politicos'). Se 'not_hate', retorne null.\n"
        "- 'confianca_ia': probabilidade de 0.0 a 1.0 da classificação estar correta.\n\n"
        f"Categorias válidas: {', '.join(VALID_CATEGORIAS)}.\n"
        "Responda APENAS com o array JSON puro, sem markdown.\n\n"
    )

    prompt = system_instruction + "Comentários para classificar:\n"
    for comment in batch_comments:
        txt = comment.get('texto') or ""
        prompt += f"ID: {comment['id']} | Texto: '{txt}'\n"
    
    return prompt

def classify_batch(batch_comments):
    """Envia um lote de comentários para a API do Gemini e retorna a classificação."""
    if not batch_comments:
        return []

    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = build_prompt(batch_comments)

    try:
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        if '```json' in raw_text:
            raw_text = raw_text.split('```json')[1].split('```')[0].strip()
        elif '```' in raw_text:
            raw_text = raw_text.split('```')[1].split('```')[0].strip()
            
        classifications = json.loads(raw_text)
        return classifications
    except Exception as e:
        print(f"[ClassifierEngine] Erro na API do Gemini: {e}")
        return []
