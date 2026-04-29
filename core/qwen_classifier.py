import os
import httpx
import json
import time
from datetime import datetime
from dotenv import load_dotenv
from core.ollama_classifier import classify_pasa_ollama

load_dotenv()

# CONFIGURAÇÕES SUPABASE
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# CONFIGURAÇÃO GROQ (CLOUD FALLBACK)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# 1. Prompt RÍGIDO com categorias exatas (PASA v16.4)
SYSTEM_PROMPT_PASA = """
Você é um analista forense do sistema Sentinela Democrática. Classifique o texto segundo o Protocolo PASA v16.4.

CATEGORIAS EXATAS (Não invente outras):
- NEUTRO (Críticas políticas, protestos, apoios agressivos, debates ideológicos NÃO são ódio).
- ODIO_IDENTITARIO (Xenofobia, racismo, regionalismo pejorativo).
- VIOLENCIA_GENERO (Misoginia, ofensas à condição feminina).
- AMEACA (Incitação a dano físico ou morte).
- INSULTO_AD_HOMINEM (Desumanização: lixo, rato, verme, escória).
- ATAQUE_INSTITUCIONAL (Deslegitimação de órgãos como STF/TSE).
- RIGOR_CRIMINAL (Imputação de crime sem prova: ladrão, corrupto, bandido).

⚠️ CUIDADO: Cartas abertas, posicionamentos políticos e reclamações de gestão devem ser classificados como NEUTRO.

REGRAS DE SAÍDA:
1. Analise o texto rigorosamente pela Seção 5 (Blindagem de Falsos Positivos).
2. Responda APENAS com um JSON válido. Nada de texto antes ou depois.
3. Formato EXATO: {"categoria": "CATEGORIA_AQUI", "confianza": 0.95, "is_hate": true/false, "justificativa": "breve motivo"}
"""

# Estado global para fallback
consecutive_failures = 0
MAX_FAILURES_BEFORE_SWITCH = 3
current_engine = "groq"

def parse_pasa_response(response_text):
    """Parser robusto para garantir tipos e evitar alucinações."""
    try:
        # Limpa marcadores de markdown caso a IA insista em colocá-los
        clean_text = response_text.strip().replace('```json', '').replace('```', '')
        result = json.loads(clean_text)
        
        # Força a categoria exata e garante que confianza é float
        categoria = str(result.get("categoria") or result.get("category") or "FALHA_IA").upper().strip()
        # Tratamento de erro de digitação comum da IA
        if categoria == "ODEIO_IDENTITARIO": categoria = "ODIO_IDENTITARIO"
        
        confianza = float(result.get("confianza") or result.get("confianca") or 0.0)
        is_hate = bool(result.get("is_hate", False))
        
        # Proteção contra alucinação de categoria
        categorias_validas = ["NEUTRO", "ODIO_IDENTITARIO", "VIOLENCIA_GENERO", "AMEACA", "INSULTO_AD_HOMINEM", "ATAQUE_INSTITUCIONAL", "RIGOR_CRIMINAL"]
        
        if categoria not in categorias_validas:
            categoria = "FALHA_IA"
            confianza = 0.0
            is_hate = False
            
        return {"is_hate": is_hate, "category": categoria, "confianca": confianza, "justificativa": result.get("justificativa", "")}
        
    except Exception as e:
        print(f"⚠️ Erro Parser: {e}")
        return {"is_hate": False, "category": "FALHA_IA", "confianca": 0.0}

def classify_text_groq(text):
    if not GROQ_API_KEY:
        return {"is_hate": False, "category": "ERRO_CONFIG", "confianca": 0.0}
    
    if not text or not text.strip():
        return {"is_hate": False, "category": "NEUTRO", "confianca": 1.0}
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    for i in range(3): # Tenta 3 vezes com backoff
        try:
            payload = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT_PASA},
                    {"role": "user", "content": f"TEXTO: \"{text}\""}
                ],
                "response_format": {"type": "json_object"}
            }
            resp = httpx.post(url, headers=headers, json=payload, timeout=25.0)
            if resp.status_code == 200:
                content = resp.json()['choices'][0]['message']['content']
                return parse_pasa_response(content)
            elif resp.status_code == 429:
                print(f"⏳ Rate limit atingido. Aguardando {2**(i+1)}s...")
                time.sleep(2**(i+1))
                continue
            else:
                print(f"⚠️ Erro API Groq ({resp.status_code}): {resp.text}")
        except Exception as e:
            print(f"⚠️ Exceção Groq: {e}")
            time.sleep(1)
    
    return {"is_hate": False, "category": "FALHA_IA", "confianca": 0.0}

def classify_with_smart_fallback(text: str):
    global consecutive_failures, current_engine
    
    if current_engine == "ollama":
        return classify_pasa_ollama(text)
    
    # Tenta Groq (Primário)
    result = classify_text_groq(text)
    
    if result.get("category") == "FALHA_IA":
        consecutive_failures += 1
    else:
        consecutive_failures = 0 # Reseta se der certo
        
    if consecutive_failures >= MAX_FAILURES_BEFORE_SWITCH:
        print("🔄 [Fallback Dinâmico] Groq instável ou com Rate Limit. Alternando para Ollama Local...")
        current_engine = "ollama"
        return classify_pasa_ollama(text)
        
    return result

def run_integrated_qwen_classification():
    print(f"🧠 Intelligence Engine: Iniciando Perícia PASA v16.4 (Motor: {current_engine})...")
    
    try:
        # Lote de segurança (Capping) para desengasgar a pipeline
        BATCH_SIZE = 100
        url = f"{SUPABASE_URL}/rest/v1/comentarios?processado_ia=eq.false&limit={BATCH_SIZE}"
        resp = httpx.get(url, headers=HEADERS)
        comentarios = resp.json()

        if not comentarios:
            print("✅ Tudo processado.")
            return

        print(f"📦 [IA] Processando lote de segurança: {len(comentarios)} comentários pendentes.")

        for c in comentarios:
            # Usar texto_bruto obrigatoriamente
            text = c.get('texto_bruto', '')
            result = classify_with_smart_fallback(text)
            
            # Atualiza no Supabase
            update_url = f"{SUPABASE_URL}/rest/v1/comentarios?id=eq.{c['id']}"
            patch_data = {
                "is_hate": result.get('is_hate', False),
                "categoria_ia": result.get('category', 'NEUTRO'),
                "confianza_ia": float(result.get('confianca', 0.0)),
                "processado_ia": True
            }
            
            httpx.patch(update_url, headers=HEADERS, json=patch_data)
            
            status_icon = "🔥" if patch_data["is_hate"] else "✅"
            engine_tag = "[Ollama]" if current_engine == "ollama" else "[Groq]"
            print(f"   {status_icon} {engine_tag} @{c.get('autor_username')}: {patch_data['categoria_ia']}")

    except Exception as e:
        print(f"❌ Erro Crítico na Classificação: {e}")

if __name__ == "__main__":
    run_integrated_qwen_classification()
