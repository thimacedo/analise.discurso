import asyncio
import httpx
import os
import json
from core.config import settings
from core.forensics_service import forensics_service

async def test_gemini():
    print(f"Testing Gemini with key: {settings.GEMINI_API_KEY[:10]}...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={settings.GEMINI_API_KEY}"
    system_prompt = forensics_service.get_system_prompt()
    text = "Esse político é um ladrão corrupto chefe de quadrilha."
    
    payload = {
        "contents": [{"parts": [{"text": f"{system_prompt}\n\nTEXTO: \"{text}\""}]}],
        "generationConfig": {"response_mime_type": "application/json"}
    }
    
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(url, json=payload, timeout=15.0)
            print(f"Status: {resp.status_code}")
            if resp.status_code == 200:
                raw_text = resp.json()['candidates'][0]['content']['parts'][0]['text']
                print(f"Raw Output: {raw_text}")
                parsed = forensics_service.parse_verdict(raw_text)
                print(f"Parsed: {parsed}")
            else:
                print(f"Error: {resp.text}")
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_gemini())
