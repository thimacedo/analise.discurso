
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import httpx

def test_ollama():
    base_url = "http://127.0.0.1:11434"
    print(f"--- Testando Ollama em {base_url} ---")
    
    try:
        r = httpx.get(f"{base_url}/")
        print(f"Root: {r.status_code} - {r.text.strip()}")
    except Exception as e:
        print(f"Root Erro: {e}")

    try:
        # /api/tags deve ser GET
        r = httpx.get(f"{base_url}/api/tags")
        print(f"Tags: {r.status_code} - {len(r.json().get('models', []))} modelos encontrados")
    except Exception as e:
        print(f"Tags Erro: {e}")

    try:
        # Tenta um /api/chat minimalista
        payload = {
            "model": "qwen2.5:3b",
            "messages": [{"role": "user", "content": "hi"}],
            "stream": False
        }
        r = httpx.post(f"{base_url}/api/chat", json=payload)
        print(f"Chat: {r.status_code} - {r.text[:100]}...")
    except Exception as e:
        print(f"Chat Erro: {e}")

if __name__ == "__main__":
    test_ollama()
