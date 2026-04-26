import os
import json
import asyncio
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Configuração do Provedor de Elite: Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
client_groq = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

SYSTEM_PROMPT = """Você é um Perito em Linguística Forense (Protocolo PASA v15.5) operando sob diretrizes do STF e UFRN.

DIRETRIZES DE RIGOR PERICIAL:
1. MENS REA: Identifique a intenção real. Ironia política ou uso de gírias regionais (ex: 'rapariga' em PT) não são crimes se não houver intenção de ofender a dignidade.
2. FALSOS POSITIVOS: É PROIBIDO classificar como ódio críticas à gestão ('incompetente', 'corrupto') ou Dopamine Agreement (aplausos 👏, elogios).
3. COORDENAÇÃO: Identifique padrões sintáticos repetitivos que indiquem bots/milícias digitais.

TAXONOMIA EXIGIDA:
- ÓDIO_IDENTITÁRIO
- VIOLÊNCIA_GÊNERO
- AMEAÇA_DIRETA
- ATAQUE_COORDENADO
- INSULTO_AD_HOMINEM
- DISSIDÊNCIA_DURA
- APOIO_ORGÂNICO

REGRA DE CLASSIFICAÇÃO FATAL:
Comentários com APENAS aplausos, emojis positivos ou elogios TÊM que retornar is_hate = false e categoria = 'APOIO_ORGÂNICO'.

Retorne APENAS um JSON: {"is_hate": boolean, "categoria": "string", "analise_linguistica": "string", "is_sarcastic": boolean}"""

class AIEngine:
    @staticmethod
    async def analyze_comment(text: str):
        """
        Analisa um comentário usando Groq (Primário) ou Fallback Local.
        """
        if not client_groq:
            return {"error": "Groq API Key não configurada", "is_hate": False}

        try:
            # Motor Groq (Llama 3.3 70B) - Latência sub-segundo
            completion = client_groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Analise pericialmente: {text}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            return json.loads(completion.choices[0].message.content)
            
        except Exception as e:
            print(f"[AI ENGINE] Falha no Groq: {e}. Tentando motor local...")
            # Aqui entraria a lógica de fallback para o Ollama/Qwen se necessário
            return {"text": text, "is_hate": False, "status": "offline_fallback"}

if __name__ == "__main__":
    # Teste rápido de conetividade
    async def test():
        engine = AIEngine()
        res = await engine.analyze_comment("Esse político é um lixo, devia ser preso!")
        print(json.dumps(res, indent=2))
    
    asyncio.run(test())
