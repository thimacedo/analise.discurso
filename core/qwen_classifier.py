import os
import httpx
import json
import ollama
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

def load_training_criteria():
    try:
        with open('CRITERIOS_TREINAMENTO.md', 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return "Diretrizes não encontradas. Use bom senso pericial."

def run_integrated_qwen_classification():
    print("🧠 Qwen 2.5 0.5B + Blindagem + Baliza: Iniciando Perícia...")
    criteria = load_training_criteria()
    url_fetch = f"{SUPABASE_URL}/rest/v1/comentarios?processado_ia=eq.false&limit=15"
    
    try:
        resp = httpx.get(url_fetch, headers=HEADERS)
        comments = resp.json()
        if not comments:
            print("✅ Tudo processado.")
            return

        for c in comments:
            text = c.get("texto_bruto", "")
            comment_id = c.get("id")
            
            # 1. BLINDAGEM (SHIELDING) - Resposta imediata para casos óbvios
            text_clean = text.lower().strip()
            shielded_emojis = ["🙌", "👏", "🔥", "❤️", "😍", "🚀", "✅", "👍"]
            is_shielded = any(emoji in text for emoji in shielded_emojis) or \
                          any(term in text_clean for term in ["parabéns", "sucesso", "amigo", "deus", "apoio", "estamos juntos"])
            
            if is_shielded:
                result = {"is_hate": False, "category": "APOIO/EMOJI", "reasoning": "Blindagem: Identificado como apoio positivo."}
            else:
                # 2. PROCESSAMENTO IA (Se não for blindado)
                prompt = f"""
                Você é um Perito em Linguística Forense. Use as DIRETRIZES abaixo para classificar o comentário.
                --- DIRETRIZES MESTRE ---
                {criteria}
                --- FIM DAS DIRETRIZES ---
                Comentário para Análise: "{text}"
                Responda APENAS em JSON:
                {{
                    "is_hate": true/false,
                    "category": "CATEGORIA_DO_MANUAL",
                    "reasoning": "Justificativa técnica"
                }}
                """
                response = ollama.generate(model='qwen2.5-coder:0.5b', prompt=prompt)
                try:
                    res_raw = response['response']
                    start = res_raw.find('{')
                    end = res_raw.rfind('}') + 1
                    result = json.loads(res_raw[start:end])
                except:
                    result = {"is_hate": False, "category": "NEUTRO", "reasoning": "Erro de parse"}

            # 3. ATUALIZAÇÃO CLOUD
            url_update = f"{SUPABASE_URL}/rest/v1/comentarios?id=eq.{comment_id}"
            httpx.patch(url_update, json={
                "processado_ia": True,
                "is_hate": result.get("is_hate", False),
                "categoria_ia": result.get("category", "NEUTRO")
            }, headers=HEADERS)
            
            status_icon = "🚩" if result.get("is_hate") else "✅"
            print(f"   {status_icon} @{c.get('autor_username')}: [{result.get('category')}]")

    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    run_integrated_qwen_classification()
