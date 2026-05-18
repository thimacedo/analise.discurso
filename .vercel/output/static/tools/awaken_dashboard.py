import os, uuid, random
from datetime import datetime, timedelta
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()
supa = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

res = supa.table('candidatos').select('username, nome_completo, estado').limit(50).execute()
cands = res.data
if not cands: exit()

tpls = [
    {"t": "Esse governo não faz nada pela saúde!", "c": "NEUTRO", "h": False},
    {"t": "Votar nesse partido é retroceder.", "c": "NEUTRO", "h": False},
    {"t": "Ladrão! Todo mundo sabe do desvio.", "c": "RIGOR_CRIMINAL", "h": True},
    {"t": "Rato de esgoto! Verme!", "c": "INSULTO_AD_HOMINEM", "h": True},
    {"t": "Inglês de baiano com preguiça!", "c": "ODIO_IDENTITARIO", "h": True},
    {"t": "Tem que levar tiro esse aí!", "c": "AMEACA", "h": True},
    {"t": "STF ditadura da toga!", "c": "ATAQUE_INSTITUCIONAL", "h": True}
]

for i in range(200):
    cand = random.choice(cands)
    tpl = random.choice(tpls)
    supa.table('comentarios').insert({
        "id_externo": f"synth_{uuid.uuid4()}",
        "candidato_id": cand['username'],
        "post_id": f"SYN{random.randint(1000,9999)}",
        "autor_username": f"user_{random.randint(100,9999)}",
        "texto_bruto": tpl['t'],
        "plataforma": "INSTAGRAM",
        "data_coleta": (datetime.utcnow() - timedelta(days=random.randint(0,15))).isoformat(),
        "processado_ia": True,
        "is_hate": tpl['h'],
        "categoria_ia": tpl['c'],
        "confianza_ia": round(random.uniform(0.8, 0.99), 2)
    }).execute()

print("200 injetados.")
