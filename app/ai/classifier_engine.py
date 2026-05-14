"""
PASA v25 - AI Classifier Engine: Processamento em Lote com Few-Shot Dinâmico
"""
import os
import json
import google.generativeai as genai
from core.supabase_service import supabase

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_gold_examples(limit=5):
    """Busca os exemplos do Padrão Ouro para Few-Shot Prompting."""
    try:
        # Tenta buscar da tabela sugerida no PASA v25
        response = supabase.table('audit_gold_standards')\
            .select('texto_original, rotulo_correto')\
            .order('created_at', desc=True)\
            .limit(limit)\
            .execute()
        return response.data if response.data else []
    except Exception:
        # Fallback: Se a tabela não existir, tentamos o arquivo JSON do Padrão Ouro original
        try:
            gold_path = os.path.join(os.getcwd(), 'data', 'classifier_gold_dataset.json')
            if os.path.exists(gold_path):
                with open(gold_path, 'r', encoding='utf-8') as f:
                    gold_data = json.load(f)
                    # Converte para o formato esperado: {'texto_original': ..., 'rotulo_correto': ...}
                    return [{"texto_original": item['text'], "rotulo_correto": item['label']} for item in gold_data[-limit:]]
        except Exception:
            pass
        return []

def build_prompt(batch_comments):
    """Constrói o prompt com Few-Shot e o lote de comentários."""
    gold_examples = get_gold_examples()
    
    system_instruction = (
        "Você é um analista forense do Sentinela Democrática. "
        "Classifique os comentários a seguir como 'hate' ou 'not_hate'. "
        "Responda APENAS com um array JSON de objetos contendo 'id' e 'rotulo'.\n\n"
    )

    if gold_examples:
        system_instruction += "Exemplos de classificação correta (Padrão Ouro):\n"
        for ex in gold_examples:
            system_instruction += f"Texto: '{ex['texto_original']}' -> Rotulo: '{ex['rotulo_correto']}'\n"
        system_instruction += "\n"

    prompt = system_instruction + "Comentários para classificar:\n"
    for comment in batch_comments:
        # Usa texto_bruto se 'texto' não estiver presente
        txt = comment.get('texto') or comment.get('texto_bruto') or ""
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
        # Limpeza defensiva do texto retornado pela IA
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
