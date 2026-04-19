import os
import asyncio
import httpx
import json
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Credenciais
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GROQ_KEY = os.getenv("GROQ_API_KEY")

client_groq = Groq(api_key=GROQ_KEY)

HEADERS_SB = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

async def analyze_with_groq(text):
    """Realiza análise pericial usando Llama 3.3 70B no Groq."""
    try:
        completion = client_groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "Você é um perito criminal em linguística forense digital. "
                        "Analise o comentário político fornecido quanto a discurso de ódio. "
                        "Retorne EXCLUSIVAMENTE um objeto JSON válido no formato: "
                        "{\"is_hate\": boolean, \"categoria\": \"string\", \"justificativa\": \"string\"}. "
                        "Categorias possíveis: Racismo, Misoginia, Homofobia, Xenofobia, Transfobia, Intolerância Religiosa, Ódio Político, Neutro."
                    )
                },
                {"role": "user", "content": text}
            ],
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        print(f"   ⚠️ Erro Groq: {e}")
        return None

async def process_pendencies():
    print("🧠 INICIANDO PROCESSAMENTO DE INTELIGÊNCIA (GROQ v5.7)...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Buscar comentários não processados
        print("🔍 Buscando evidências pendentes no Supabase...")
        # Filtra por processado_ia is null ou false usando OR
        r = await client.get(
            f"{SUPABASE_URL}/rest/v1/comentarios?or=(processado_ia.is.null,processado_ia.eq.false)&limit=20", 
            headers=HEADERS_SB
        )
        
        if r.status_code != 200:
            print(f"❌ Erro ao buscar dados: {r.text}")
            return
        
        pendencies = r.json()
        if not pendencies:
            print("✅ Nenhuma evidência pendente para processar.")
            return

        print(f"📊 Encontradas {len(pendencies)} evidências. Iniciando análise...")

        for item in pendencies:
            text = item.get("texto_bruto", "")
            id_db = item.get("id_externo") # Usando id_externo como chave de busca/update se necessário, ou id primário
            
            print(f"   📝 Analisando: {text[:40]}...")
            analysis = await analyze_with_groq(text)
            
            if analysis:
                # 2. Atualizar registro no Supabase
                update_data = {
                    "is_hate": analysis.get("is_hate", False),
                    "categoria_ia": analysis.get("categoria", "NEUTRO"),
                    "processado_ia": True
                }
                
                # Patch individual por id_externo
                up_res = await client.patch(
                    f"{SUPABASE_URL}/rest/v1/comentarios?id_externo=eq.{id_db}",
                    json=update_data,
                    headers=HEADERS_SB
                )
                
                if up_res.status_code in [200, 204]:
                    veredito = "🚨 ÓDIO" if analysis.get("is_hate") else "🏳️ NEUTRO"
                    print(f"   ✅ Processado: {veredito} | Categoria: {analysis.get('categoria')}")
                else:
                    print(f"   ❌ Erro update ID {id_db}: {up_res.text}")
            
            # Rate limit preventivo para o Groq Free Tier se necessário
            await asyncio.sleep(1)

    print("\n🏆 ANÁLISE DE INTELIGÊNCIA CONCLUÍDA!")

if __name__ == "__main__":
    asyncio.run(process_pendencies())
