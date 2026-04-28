import httpx
import os
from dotenv import load_dotenv

load_dotenv()

def reset_and_reclassify():
    print("🧹 Resetando marcações incorretas no Supabase...")
    headers = {
        "apikey": os.getenv("SUPABASE_KEY"),
        "Authorization": f"Bearer {os.getenv('SUPABASE_KEY')}",
        "Content-Type": "application/json"
    }
    # Filtro correto para o PostgREST: is.not.null (sem ponto entre not e null)
    url = f"{os.getenv('SUPABASE_URL')}/rest/v1/comentarios?processado_ia=not.is.null"
    
    try:
        resp = httpx.patch(url, json={
            "processado_ia": False, 
            "is_hate": False, 
            "categoria_ia": "NEUTRO"
        }, headers=headers)
        
        if resp.status_code in [200, 204]:
            print("✅ Banco pronto para re-classificação.")
        else:
            print(f"❌ Erro no reset: {resp.text}")
            
    except Exception as e:
        print(f"❌ Falha: {e}")

if __name__ == "__main__":
    reset_and_reclassify()
