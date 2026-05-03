import asyncio
from playwright.async_api import async_playwright
import os
import sys
import json
import hashlib
from datetime import datetime, UTC
from core.db import db_client 

# Garante que o diretório raiz está no path de forma absoluta e forçada
sys.path.append(r"E:\Projetos\sentinela-democratica")

USER_DATA_DIR = os.path.join(os.getcwd(), "browser_profile_tmp")
PROFILE_DIR = "Default"

async def scrape_instagram_comments(username):
    async with async_playwright() as p:
        print(f"🚀 Lançando Chrome em {USER_DATA_DIR}...")
        context = await p.chromium.launch_persistent_context(
            user_data_dir=USER_DATA_DIR,
            channel="chrome",
            headless=False,
            args=[f"--profile-directory={PROFILE_DIR}", "--start-maximized"]
        )
        page = await context.new_page()
        
        print(f"🌍 Navegando para: https://www.instagram.com/{username}/")
        # Mudança cirúrgica: networkidle trava com telemetria, domcontentloaded é o caminho
        await page.goto(f"https://www.instagram.com/{username}/", wait_until="domcontentloaded", timeout=60000)
        
        # Espera forçada para o DOM renderizar
        await asyncio.sleep(15) 
        
        # Extração
        comments = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('span._ap3a')).map(el => el.innerText);
        }''')
        
        print(f"✅ Encontrados {len(comments)} comentários. Persistindo no banco...")
        
        for comment in comments:
            if len(comment) > 5:
                try:
                    hash_id = hashlib.md5(comment.encode()).hexdigest()
                    id_externo = f"ig_{hash_id}"
                    
                    comment_data = {
                        'candidato_id': username,
                        'texto_bruto': comment,
                        'plataforma': 'INSTAGRAM',
                        'data_coleta': datetime.now(UTC).isoformat(),
                        'processado_ia': False,
                        'id_externo': id_externo 
                    }
                    db_client.client.table('comentarios').insert(comment_data).execute()
                    print(f"💾 Persistido: {comment[:30]}...")
                except Exception as e:
                    print(f"⚠️ Erro ao persistir: {e}")
        
        await context.close()

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "lulaoficial"
    asyncio.run(scrape_instagram_comments(target))
