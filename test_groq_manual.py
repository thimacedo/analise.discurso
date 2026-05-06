import asyncio
import httpx
import os
import json
from core.config import settings
from core.forensics_service import forensics_service

async def test_groq():
    print(f"Testing Groq with key: {settings.GROQ_API_KEY[:10]}...")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {settings.GROQ_API_KEY}"}
    system_prompt = forensics_service.get_system_prompt()
    text = "Esse político é um ladrão corrupto chefe de quadrilha."
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"TEXTO: \"{text}\""}
        ],
        "response_format": {"type": "json_object"}
    }
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(url, headers=headers, json=payload, timeout=15.0)
            print(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                raw_text = resp.json()['choices'][0]['message']['content']
                print(f"Raw Output: {raw_text}")
                parsed = forensics_service.parse_verdict(raw_text)
                print(f"Parsed: {parsed}")
            else:
                print(f"Error: {resp.text}")
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_groq())
