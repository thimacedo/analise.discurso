import os
import httpx
import json
from datetime import datetime
from dotenv import load_dotenv

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

SYSTEM_PROMPT_PASA = """
Você é um analista forense do sistema Sentinela Democrática. Sua tarefa é classificar comentários de redes sociais segundo o Protocolo PASA v16.4.

CATEGORIAS DE HOSTILIDADE:
- ODIO_IDENTITARIO: Ataques baseados em raça, religião, orientação sexual, misoginia ou XENOFOBIA/REGIONALISMO (ex: sotaque, preguiça regional).
- VIOLENCIA_GENERO: Ofensas focadas na condição feminina.
- AMEACA: Incitação a dano físico ou morte.
- INSULTO_AD_HOMINEM: Desumanização e baixo calão (ex: lixo, verme, rato, escória).
- ATAQUE_INSTITUCIONAL: Deslegitimação de órgãos de Estado (ex: ditadura da toga, STF comprado).
- RIGOR_CRIMINAL: Imputação de crime sem prova (ex: ladrão, corrupto, bandido).

⚠️ BLINDAGEM CONTRA FALSOS POSITIVOS (CRÍTICO):
- CRÍTICA POLÍTICA ou INSATISFAÇÃO com gestão pública NÃO são ódio. Classifique como NEUTRO.
- PROTESTOS como "Fora Fulano" ou "Fora Governo X" são liberdade de expressão. Classifique como NEUTRO.
- TERMOS DE BAIXO CALÃO ou GÍRIAS em contexto de exaltação (ex: "porra", "o brabo") são NEUTRO.
- DEFESA DE MANDATO NÃO é ataque institucional.

Responda APENAS com um JSON no formato: {"is_hate": true/false, "category": "CATEGORIA_AQUI", "confianca": 0.9, "justificativa": "breve motivo"}
Se não houver hostilidade forense, use: {"is_hate": false, "category": "NEUTRO", "confianca": 1.0, "justificativa": "critica politica legitima"}
"""

def classify_text_groq(text):
    if not GROQ_API_KEY:
        return {"is_hate": False, "category": "ERRO_CONFIG"}
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT_PASA},
                {"role": "user", "content": f"TEXTO: \"{text}\""}
            ],
            "response_format": {"type": "json_object"}
        }
        resp = httpx.post(url, headers=headers, json=payload, timeout=20.0)
        if resp.status_code == 200:
            return json.loads(resp.json()['choices'][0]['message']['content'])
    except Exception as e:
        print(f"⚠️ Erro Groq: {e}")
    
    return {"is_hate": False, "category": "FALHA_IA"}

def run_integrated_qwen_classification():
    print("🧠 Groq Cloud Intelligence: Iniciando Perícia PASA v16.4 (Blindada)...")
    
    try:
        # Busca comentários não processados
        url = f"{SUPABASE_URL}/rest/v1/comentarios?processado_ia=eq.false&limit=50"
        resp = httpx.get(url, headers=HEADERS)
        comentarios = resp.json()

        if not comentarios:
            print("✅ Tudo processado.")
            return

        for c in comentarios:
            text = c.get('texto_bruto', '')
            result = classify_text_groq(text)
            
            # Atualiza no Supabase
            update_url = f"{SUPABASE_URL}/rest/v1/comentarios?id=eq.{c['id']}"
            patch_data = {
                "is_hate": result.get('is_hate', False),
                "categoria_ia": result.get('category') or result.get('categoria') or 'NEUTRO',
                "processado_ia": True
            }
            httpx.patch(update_url, headers=HEADERS, json=patch_data)
            
            status_icon = "🔥" if patch_data["is_hate"] else "✅"
            print(f"   {status_icon} @{c.get('autor_username')}: [{patch_data['categoria_ia']}]")

    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    run_integrated_qwen_classification()
