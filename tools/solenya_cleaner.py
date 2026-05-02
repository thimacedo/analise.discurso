import os
import httpx
from dotenv import load_dotenv

load_dotenv()

def solenyacleaner():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    headers = {"apikey": key, "Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    
    print("🧹 [SOLENYA] Iniciando auditoria de lixo no backlog...")
    
    try:
        # 1. Busca todos os pendentes (precisamos dos IDs e do texto para auditar)
        r = httpx.get(f"{url}/rest/v1/comentarios?processado_ia=eq.false&select=id,autor_username,texto_bruto", headers=headers)
        if r.status_code != 200:
            print(f"❌ Erro ao buscar dados: {r.text}")
            return
            
        backlog = r.json()
        print(f"📊 Analisando {len(backlog)} registros...")
        
        ids_to_delete = []
        
        for c in backlog:
            cid = c['id']
            user = str(c.get('autor_username', '')).lower().strip()
            text = str(c.get('texto_bruto', '')).lower().strip()
            
            is_trash = False
            
            # CRITÉRIOS DE LIXO (JERRY-SLOP)
            # 1. Texto é igual ao nome de usuário (Erro comum de scraper DOM)
            if text == user or text == f"@{user}":
                is_trash = True
            # 2. Texto extremamente curto (menor que 4 caracteres) e não é emoji conhecido
            elif len(text) < 4 and not any(ord(char) > 10000 for char in text):
                is_trash = True
            # 3. Ruído de sistema do Instagram 2026
            elif text in ["há 1 dia", "há 1 h", "responder", "ver tradução", "upload de contatos"]:
                is_trash = True
            # 4. Apenas hashtags sem texto
            elif text.startswith("#") and " " not in text and len(text.split("#")) > 2:
                is_trash = True

            if is_trash:
                ids_to_delete.append(cid)

        print(f"🚨 Detectados {len(ids_to_delete)} registros de lixo.")
        
        if not ids_to_delete:
            print("✨ Nenhum lixo encontrado. O backlog está limpo (mas não processado).")
            return

        # 2. Deleta o lixo em lotes (para não estourar a URL/Payload)
        batch_size = 100
        deleted_count = 0
        
        for i in range(0, len(ids_to_delete), batch_size):
            batch = ids_to_delete[i:i+batch_size]
            # Usando filtro 'in' na query string
            delete_url = f"{url}/rest/v1/comentarios?id=in.({','.join(map(str, batch))})"
            dr = httpx.delete(delete_url, headers=headers)
            
            if dr.status_code in [200, 204]:
                deleted_count += len(batch)
                print(f"🗑️ Deletado lote {i//batch_size + 1}... ({deleted_count} total)")
            else:
                print(f"❌ Erro ao deletar lote: {dr.text}")

        print(f"\n✅ FAXINA CONCLUÍDA! {deleted_count} registros removidos do universo.")
        
    except Exception as e:
        print(f"❌ Falha crítica na limpeza: {e}")

if __name__ == "__main__":
    solenyacleaner()
