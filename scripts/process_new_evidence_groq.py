import os
import asyncio
import httpx
import json
import time
from dotenv import load_dotenv

load_dotenv()

# Configurações de API
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

async def analyze_comment(text):
    """Motor de IA v15.6.10 - Scanner de Ironia e Rigor Criminal."""
    system_instruction = (
        "Você é um Perito em Linguística Forense (Protocolo PASA v15.6) independente.\n\n"
        "DIRETRIZES DE RIGOR PERICIAL:\n"
        "1. SCANNER DE IRONIA: Desconstrua elogios cínicos. Se o usuário usa termos positivos ('parabéns', 'lindo', 'gênio') para descrever resultados negativos ou crises, classifique como INSULTO ou ATAQUE.\n"
        "2. ACUSAÇÕES CRIMINAIS: Marque como 'ATAQUE_INSTITUCIONAL' qualquer imputação de crime sem provas (ladrão, traficante, corrupto, genocida).\n"
        "3. ESCATOLOGIA: Termos vulgares (lixo, cocô, merda) são sempre INSULTO.\n"
        "4. NEUTRO: Apenas para apoio real, dúvidas administrativas ou críticas educadas sem adjetivação pejorativa.\n\n"
        "TAXONOMIA: ÓDIO_IDENTITÁRIO, VIOLÊNCIA_GÊNERO, AMEAÇA, INSULTO_AD_HOMINEM, ATAQUE_INSTITUCIONAL, NEUTRO.\n\n"
        "Retorne EXATAMENTE um JSON: {\"is_hate\": boolean, \"categoria_ia\": \"string\", \"justificativa\": \"string\"}"
    )

    url = "https://api.groq.com/openai/v1/chat/completions"
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"Analise: {text}"}
        ],
        "response_format": {"type": "json_object"}
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            res = await client.post(url, headers={"Authorization": f"Bearer {GROQ_API_KEY}"}, json=data)
            return json.loads(res.json()['choices'][0]['message']['content'])
    except Exception as e:
        print(f"Erro IA: {e}")
        return None

async def process_batch():
    async with httpx.AsyncClient() as client:
        # Buscar próximos 50 itens pendentes
        res = await client.get(f"{SUPABASE_URL}/rest/v1/comentarios?processado_ia=eq.false&limit=50", headers=headers)
        comentarios = res.json()
        
        if not comentarios or not isinstance(comentarios, list):
            return 0
            
        for com in comentarios:
            text = com.get('texto_bruto') or com.get('texto')
            if not text: continue
            
            print(f"📝 Analisando: {text[:50]}...")
            result = await analyze_comment(text)
            
            if result:
                is_hate = result.get('is_hate', False)
                cat = result.get('categoria_ia', 'NEUTRO')
                print(f"   ✅ {'🚨 ALERTA' if is_hate else '🏳️ NEUTRO'} [{cat}]")
                
                # Atualizar banco instantaneamente
                await client.patch(
                    f"{SUPABASE_URL}/rest/v1/comentarios?id=eq.{com['id']}", 
                    headers=headers,
                    json={
                        "processado_ia": True,
                        "is_hate": is_hate,
                        "categoria_ia": cat,
                        "justificativa": result.get('justificativa', '')
                    }
                )
            await asyncio.sleep(0.5)
        return len(comentarios)

async def main():
    print("🧠 INICIANDO PROCESSAMENTO INTEGRAL PASA v15.6.10...")
    while True:
        processed_count = await process_batch()
        if processed_count == 0:
            print("✨ Backlog zerado. Aguardando novas evidências...")
            break
        print(f"📦 Lote de {processed_count} concluído. Continuando...")

if __name__ == "__main__":
    asyncio.run(main())
