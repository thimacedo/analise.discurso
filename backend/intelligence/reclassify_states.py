import os
import httpx
import json
from dotenv import load_dotenv

load_dotenv()

URL = os.getenv("SUPABASE_URL")
KEY = os.getenv("SUPABASE_KEY")
LLM_KEY = os.getenv("GROQ_API_KEY")
headers = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}

def identify_strict_state(username, nome, cargo):
    prompt = f"Analise: @{username} ({nome}) - Cargo: {cargo}. Este político é uma figura de PROJEÇÃO NACIONAL (Ex: Presidente, Ministro STF, Liderança Nacional) ou é focado em um ESTADO específico? Responda APENAS a sigla: BR (para Nacional) ou a UF (ex: RN, SP, RJ, MG). Seja rigoroso."
    try:
        res = httpx.post("https://api.groq.com/openai/v1/chat/completions", 
            headers={"Authorization": f"Bearer {LLM_KEY}"},
            json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1})
        return res.json()['choices'][0]['message']['content'].strip().upper()[:2]
    except: return None

def cleanup_national_base():
    print("🧹 Iniciando Auditoria de Base Nacional (Exclusividade BR vs UF)...")
    r = httpx.get(f"{URL}/candidatos?select=id,username,nome_completo,cargo,estado", headers=headers)
    candidates = r.json()
    
    count = 0
    for c in candidates:
        u, n, cargo, estado = (c.get("username") or "").lower(), (c.get("nome_completo") or "").lower(), (c.get("cargo") or "").lower(), c.get("estado")
        
        # Só auditamos quem está no BR para ver se deve descer para UF
        if estado == "BR":
            # Proteção manual para a elite inquestionável
            if any(x in u for x in ["lulaoficial", "jairmessiasbolsonaro", "michellebolsonaro", "geraldoalckmin", "marinasilva"]):
                continue
                
            novo = identify_strict_state(u, n, cargo)
            if novo and novo != "BR":
                print(f"   -> REMOVENDO DO NACIONAL: @{u} vai para {novo}")
                httpx.patch(f"{URL}/candidatos?id=eq.{c['id']}", headers=headers, json={"estado": novo})
                count += 1

    print(f"\n✅ Auditoria concluída! {count} perfis reordenados para seus estados de origem.")

if __name__ == "__main__":
    cleanup_national_base()
