import os
import asyncio
import httpx
import json
from datetime import datetime
from groq import Groq
from braintrust import traced, init_logger
from dotenv import load_dotenv

load_dotenv()

# Credenciais
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GROQ_KEY = os.getenv("GROQ_API_KEY")
BRAINTRUST_API_KEY = os.getenv("BRAINTRUST_API_KEY")

# Inicializa Logger da Braintrust
logger = init_logger(project="braintrust-beige-umbrella", api_key=BRAINTRUST_API_KEY)
client_groq = Groq(api_key=GROQ_KEY)

HEADERS_SB = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

async def analyze_with_qwen_local(text):
    """Fallback: Análise pericial usando Qwen 2.5 Coder 1.5B local via Ollama."""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            payload = {
                "model": "qwen2.5-coder:1.5b",
                "messages": [
                    {
                        "role": "system", 
                        "content": "Analise o comentário quanto a discurso de ódio. Retorne JSON: {\"is_hate\": boolean, \"categoria\": \"string\"}. Categorias: Racismo, Misoginia, Homofobia, Xenofobia, Ódio Político, Neutro."
                    },
                    {"role": "user", "content": text}
                ],
                "stream": False,
                "format": "json"
            }
            r = await client.post("http://localhost:11434/api/chat", json=payload)
            result = r.json()
            content = json.loads(result["message"]["content"])
            return content
    except Exception as e:
        print(f"      ⚠️ Falha Fallback Qwen: {e}")
        return None

@traced(name="Advanced Situacional Analysis v9.6")
async def analyze_hybrid(text):
    """Motor de IA instruído com protocolos de detecção de sarcasmo e linguística forense."""
    system_instruction = (
        "Você é um Perito em Linguística Forense e Análise de Discurso Político. "
        "Sua tarefa é identificar a intenção real por trás de comentários em redes sociais, aplicando o PROTOCOLO PASA (Análise Situacional Avançada).\n\n"
        "DIRETRIZES DE DETECÇÃO:\n"
        "1. INCONGRUÊNCIA DE SENTIMENTO: Identifique se há elogios seguidos de emojis de deboche (ex: 🤡, 🙄, 👏) ou valência oposta.\n"
        "2. INTENSIFICADORES PRAGMÁTICOS: Atribua SARCASMO a termos como 'genial', 'parabéns', 'um orgulho' quando o contexto geral do comentário indica desaprovação.\n"
        "3. PONTUAÇÃO E REPETIÇÃO: Múltiplas exclamações ou repetições de caracteres (ex: 'lindo0000') são marcadores de ironia.\n"
        "4. monitoradoS DE RIDÍCULO: Diferencie 'Debate Crítico' (legítimo) de 'Ataque Reputacional' (Agressivo).\n\n"
        "REGRA DE CLASSIFICAÇÃO:\n"
        "- Se for SARCASMO CRÍTICO (sem xingamentos diretos): is_hate = false, categoria = 'Sarcasmo Situacional'.\n"
        "- Se o sarcasmo for usado para humilhação/desumanização: is_hate = true, categoria = 'Ataque Agravado'.\n\n"
        "RETORNO: JSON {\"is_hate\": boolean, \"categoria\": \"string\", \"analise_linguistica\": \"string\"}"
    )
    
    try:
        completion = client_groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": text}
            ],
            response_format={"type": "json_object"}
        )
        analysis = json.loads(completion.choices[0].message.content)
        analysis["engine"] = "groq-llama-70b-pasa"
        return analysis
    except Exception as e:
        if "rate_limit" in str(e).lower() or "limit" in str(e).lower():
            print(f"   📉 Limite Groq atingido. Acionando Fallback Qwen Local...")
            analysis = await analyze_with_qwen_local(text)
            if analysis:
                analysis["engine"] = "qwen-local-1.5b"
                return analysis
        else:
            print(f"   ⚠️ Erro Groq: {e}")
    return None

@traced(name="Supabase Sinc")
async def update_supabase(client, id_db, update_data):
    # Nota: Ajustado para o nome da coluna correto no Supabase
    up_res = await client.patch(
        f"{SUPABASE_URL}/rest/v1/comentarios?id_externo=eq.{id_db}",
        json=update_data,
        headers=HEADERS_SB
    )
    return up_res

async def process_pendencies():
    print("🧠 INICIANDO MOTOR HÍBRIDO (GROQ + QWEN FALLBACK v6.2)...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Busca evidências não processadas
        r = await client.get(
            f"{SUPABASE_URL}/rest/v1/comentarios?or=(processado_ia.is.null,processado_ia.eq.false)&limit=50", 
            headers=HEADERS_SB
        )
        
        pendencies = r.json() if r.status_code == 200 else []
        if not pendencies:
            print("✅ Tudo processado.")
            return

        print(f"📊 {len(pendencies)} itens na fila.")

        for item in pendencies:
            text = item.get("texto_bruto", "")
            id_db = item.get("id_externo")
            
            print(f"   📝 Analisando: {text[:30]}...")
            analysis = await analyze_hybrid(text)
            
            if analysis:
                engine_name = analysis.get('engine', 'groq-70b').upper()
                update_data = {
                    "is_hate": analysis.get("is_hate", False),
                    "categoria_ia": f"[{engine_name}] {analysis.get('categoria', 'NEUTRO').upper()}",
                    "processado_ia": True
                }
                
                await update_supabase(client, id_db, update_data)
                
                veredito = "🚨 ÓDIO" if analysis.get("is_hate") else "🏳️ NEUTRO"
                print(f"   ✅ {veredito} [{analysis.get('engine')}]")
            
            await asyncio.sleep(0.2)

if __name__ == "__main__":
    asyncio.run(process_pendencies())
