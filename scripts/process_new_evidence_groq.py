import os
import asyncio
import httpx
import json
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

# Histórico de logs para o Dashboard
LIVE_LOGS_FILE = "../data/pasa_live_logs.json"

def emit_log(candidato, texto, status, categoria):
    try:
        os.makedirs("../data", exist_ok=True)
        logs = []
        if os.path.exists(LIVE_LOGS_FILE):
            with open(LIVE_LOGS_FILE, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        
        new_log = {
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "alvo": candidato,
            "texto": texto[:60] + "...",
            "status": status,
            "categoria": categoria
        }
        
        logs = [new_log] + logs[:4] # Manter apenas os 5 últimos
        with open(LIVE_LOGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)
    except: pass

async def analyze_comment(text):
    system_instruction = (
        "Você é um Perito em Linguística Forense. Classifique o comentário em JSON.\n"
        "Exemplo: {\"is_hate\": true, \"categoria_ia\": \"INSULTO\", \"justificativa\": \"...\"}"
    )
    url = "https://api.groq.com/openai/v1/chat/completions"
    data = {
        "model": "llama-3.1-8b-instant",
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"Comentário: {text}"}
        ],
        "temperature": 0.1,
        "response_format": {"type": "json_object"}
    }
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(url, headers={"Authorization": f"Bearer {GROQ_API_KEY}"}, json=data)
            resp_json = res.json()
            if 'choices' in resp_json:
                return json.loads(resp_json['choices'][0]['message']['content'])
    except: return None

async def process_batch():
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{SUPABASE_URL}/rest/v1/comentarios?processado_ia=eq.false&limit=10&order=data_coleta.desc", headers=headers)
        comentarios = res.json()
        if not comentarios or not isinstance(comentarios, list): return 0
            
        for com in comentarios:
            text = com.get('texto_bruto') or com.get('texto')
            if not text: continue
            
            result = await analyze_comment(text)
            if result:
                is_hate = result.get('is_hate', False)
                cat = result.get('categoria_ia', 'NEUTRO')
                
                # Enviar para o arquivo de log visual
                emit_log(com['candidato_id'], text, "🚨 ALERTA" if is_hate else "🏳️ NEUTRO", cat)
                print(f"📝 [{com['candidato_id']}] -> {cat}")

                await client.patch(f"{SUPABASE_URL}/rest/v1/comentarios?id=eq.{com['id']}", headers=headers, json={
                    "processado_ia": True, "is_hate": is_hate, "categoria_ia": cat, "justificativa": result.get('justificativa', '')
                })
            await asyncio.sleep(3) # Cadência para observação visual
        return len(comentarios)

async def main():
    print("🧠 MOTOR PASA LIVE STREAMING ATIVO...")
    while True:
        try:
            count = await process_batch()
            if count == 0: await asyncio.sleep(30)
        except Exception as e:
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
