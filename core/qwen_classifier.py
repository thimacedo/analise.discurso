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

def classify_text_groq(text):
    if not GROQ_API_KEY:
        return {"is_hate": False, "category": "ERRO_CONFIG"}
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""Analise o comentário sob o Protocolo PASA v16.4 de Linguística Forense.
Diferencie CRÍTICA/APOIO POLÍTICO de HOSTILIDADE FORENSE.

TEXTO: "{text}"

DIRETRIZES DE BLINDAGEM:
1. APOIO ENFÁTICO/AGRESSIVO: Frases com gírias ("o brabo", "mito") ou palavrões de exaltação ("porra!", "caralho!") direcionados AO CANDIDATO monitorado são NEUTRO.
2. DEFESA DE MANDATO: Reclamações de perseguição contra o candidato monitorado são NEUTRO.
3. MOBILIZAÇÃO: Convocar para ruas ou citar "inimigos do povo" em contexto de disputa ideológica NÃO é ameaça.

CATEGORIAS: ODIO_IDENTITARIO, VIOLENCIA_GENERO, AMEACA, INSULTO_AD_HOMINEM, ATAQUE_INSTITUCIONAL, RIGOR_CRIMINAL, NEUTRO.

EXEMPLOS DE "NEUTRO":
- "O brabo tem nome porra! @tarcisiogdf" -> Motivo: Exaltação com gíria.
- "@brisabracchi13 na Câmara vai ser um presente!" -> Motivo: Elogio.
- "A ousadia vai ocupar o congresso!" -> Motivo: Vitória eleitoral.
- "Perseguição escancarada contra mandato sério!" -> Motivo: Opinião política.
- "Mobilizar nas ruas no 1º de maio!" -> Motivo: Exercício democrático.

Responda APENAS em JSON:
{{"is_hate": true/false, "category": "CATEGORIA", "justificativa": "breve motivo", "confianca": 0.0-1.0}}"""

    try:
        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "response_format": {"type": "json_object"}
        }
        resp = httpx.post(url, headers=headers, json=payload, timeout=20.0)
        if resp.status_code == 200:
            return json.loads(resp.json()['choices'][0]['message']['content'])
    except Exception as e:
        print(f"⚠️ Erro Groq: {e}")
    
    return {"is_hate": False, "category": "FALHA_IA"}

def run_integrated_qwen_classification():
    print("🧠 Groq Cloud Intelligence: Iniciando Perícia PASA v16.4...")
    
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
                "categoria_ia": result.get('category', 'NEUTRO'),
                "processado_ia": True
            }
            httpx.patch(update_url, headers=HEADERS, json=patch_data)
            
            status_icon = "🔥" if patch_data["is_hate"] else "✅"
            print(f"   {status_icon} @{c.get('autor_username')}: [{patch_data['categoria_ia']}]")

    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    run_integrated_qwen_classification()
