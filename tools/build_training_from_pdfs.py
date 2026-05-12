import os, sys, json, asyncio
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from pypdf import PdfReader
from core.config import settings
import httpx

PDF_DIR = ROOT / "bases_pdf"
OUTPUT_FILE = ROOT / "data" / "training_examples.json"

async def extract_examples_from_text(text: str, max_examples: int = 10) -> list:
    if not settings.MISTRAL_API_KEY:
        return []
    prompt = f"""
Analise o texto abaixo e identifique até {max_examples} exemplos de frases que representem discurso político brasileiro.
Classifique cada uma em: NEUTRO, ODIO_IDENTITARIO, VIOLENCIA_GENERO, AMEACA, INSULTO_AD_HOMINEM, ATAQUE_INSTITUCIONAL, RIGOR_CRIMINAL, XENOFOBIA_REGIONAL.
Retorne JSON: {{"examples":[{{"text":"...","category":"..."}}]}}
TEXTO:
{text[:8000]}
"""
    headers = {"Authorization": f"Bearer {settings.MISTRAL_API_KEY}"}
    payload = {"model":"mistral-large-latest","messages":[{"role":"user","content":prompt}],"response_format":{"type":"json_object"}}
    async with httpx.AsyncClient() as client:
        resp = await client.post("https://api.mistral.ai/v1/chat/completions", headers=headers, json=payload, timeout=60)
        if resp.status_code == 200:
            return json.loads(resp.json()['choices'][0]['message']['content']).get("examples",[])
        return []

async def process_all_pdfs():
    pdf_files = list(PDF_DIR.glob("*.pdf"))
    if not pdf_files: return
    all_examples = []
    for pdf_path in pdf_files:
        reader = PdfReader(str(pdf_path))
        text = ""
        for page in reader.pages[:10]:
            text += page.extract_text() + "\n"
        examples = await extract_examples_from_text(text, 5)
        all_examples.extend(examples)
    seen = set()
    unique = []
    for ex in all_examples:
        if ex['text'] not in seen:
            seen.add(ex['text'])
            unique.append(ex)
    with open(OUTPUT_FILE,'w',encoding='utf-8') as f:
        json.dump(unique[:20], f, indent=2)
    print(f"{len(unique)} exemplos salvos.")

if __name__ == "__main__":
    asyncio.run(process_all_pdfs())