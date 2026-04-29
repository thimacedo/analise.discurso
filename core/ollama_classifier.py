import os
import httpx
import json
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

def classify_pasa_ollama(text: str):
    """Classificador PASA rodando 100% local via Ollama (Sem Rate Limits)."""
    if not text or not text.strip():
        return {"is_hate": False, "category": "NEUTRO", "confianca": 1.0}

    prompt = f"""
    Você é um analista forense do sistema Sentinela. Classifique o texto segundo o Protocolo PASA v16.4.
    Categorias possíveis: NEUTRO, ODIO_IDENTITARIO, VIOLENCIA_GENERO, AMEACA, INSULTO_AD_HOMINEM, ATAQUE_INSTITUCIONAL, RIGOR_CRIMINAL.
    Críticas políticas, ironias de debate e reclamações de gestão são NEUTRO.
    
    Texto: "{text}"
    
    Responda APENAS um JSON válido no formato: {{"categoria": "CATEGORIA", "confianza": 0.9, "is_hate": true/false, "justificativa": "motivo"}}
    """
    
    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                }
            )
            response.raise_for_status()
            data = response.json()
            result = json.loads(data.get("response", "{}"))
            
            categoria = str(result.get("categoria", "FALHA_IA")).upper().strip()
            confianza = float(result.get("confianza", 0.0))
            is_hate = bool(result.get("is_hate", False))
            
            # Normalização de categorias
            categorias_validas = ["NEUTRO", "ODIO_IDENTITARIO", "VIOLENCIA_GENERO", "AMEACA", "INSULTO_AD_HOMINEM", "ATAQUE_INSTITUCIONAL", "RIGOR_CRIMINAL"]
            if categoria not in categorias_validas:
                categoria = "FALHA_IA"
            
            return {
                "is_hate": is_hate,
                "category": categoria,
                "confianca": confianza,
                "justificativa": result.get("justificativa", "")
            }
            
    except Exception as e:
        print(f"⚠️ Erro Ollama local: {e}")
        return {"is_hate": False, "category": "FALHA_IA", "confianca": 0.0}

if __name__ == "__main__":
    print(classify_pasa_ollama("Teste de integridade local."))
