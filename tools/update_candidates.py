import os, json
from groq import Groq
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
groq_key = os.getenv("GROQ_API_KEY")
if not groq_key:
    print("❌ GROQ_API_KEY não configurada.")
    exit(1)

groq = Groq(api_key=groq_key)
supa = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

ufs = ["AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS", "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC", "SP", "SE", "TO"]

prompt = f"""Liste os atuais Governador, Vice-Governador e os 3 principais pré-candidatos ao governo para as eleições 2026 de cada UF: {', '.join(ufs)}.
Para cada um, forneça nome completo, cargo, UF e o handle oficial do Instagram (sem @).
Responda APENAS com um JSON válido onde as chaves são as UFs e os valores são listas de objetos: {{"AC": [{{"nome": "...", "cargo": "...", "uf": "AC", "username": "..."}}]}}"""

print("🔍 Consultando Groq para identificar alvos reais...")
try:
    res = groq.chat.completions.create(
        model="llama-3.3-70b-versatile", 
        messages=[{"role": "user", "content": prompt}], 
        response_format={"type": "json_object"}, 
        temperature=0.1
    )
    data = json.loads(res.choices[0].message.content)

    candidatos = []
    # O Groq retorna um dict com UFs como chaves
    for v in data.values():
        if isinstance(v, list): candidatos.extend(v)

    print(f"🎯 Total de alvos identificados: {len(candidatos)}")

    for c in candidatos:
        if not c.get("username"): continue
        # Saneamento básico do username
        username = c["username"].replace("@", "").strip().lower()
        if " " in username: continue # Ignora se tiver espaço (inválido)
        
        supa.table('candidatos').upsert({
            "username": username, 
            "nome_completo": c.get("nome"), 
            "estado": c.get("uf"), 
            "cargo": c.get("cargo"),
            "status_monitoramento": "Ativo"
        }, on_conflict='username').execute()

    print(f"✅ {len(candidatos)} candidatos processados no Supabase.")
except Exception as e:
    print(f"❌ Erro: {e}")
