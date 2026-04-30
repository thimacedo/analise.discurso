import os, time, hashlib, asyncio
from playwright.async_api import async_playwright
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
supa = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
CHROME_PROFILE = r"C:\Users\THIAGO\AppData\Local\Google\Chrome\User Data"

async def scrape_instagram_stealth(limit=15):
    print("🚀 Iniciando Playwright com perfil do Chrome...")
    
    async with async_playwright() as p:
        # Lança o navegador usando o perfil persistente do usuário
        # ATENÇÃO: O Chrome deve estar fechado!
        try:
            browser_context = await p.chromium.launch_persistent_context(
                user_data_dir=CHROME_PROFILE,
                channel="chrome", # Usa o Google Chrome instalado
                headless=False,
                args=["--disable-blink-features=AutomationControlled"],
                no_viewport=False
            )
        except Exception as e:
            print(f"❌ Erro ao abrir Chrome: {e}")
            print("💡 Certifique-se de que TODAS as janelas do Chrome estão fechadas (verifique o Gerenciador de Tarefas).")
            return

        page = await browser_context.new_page()
        
        # Verifica login
        await page.goto("https://www.instagram.com/")
        await asyncio.sleep(5)
        
        if "login" in page.url:
            print("🔑 Login necessário. Por favor, realize o login manualmente.")
            input("✅ Pressione ENTER aqui no terminal após estar logado na tela inicial do IG...")
        else:
            print("✅ Sessão ativa detectada.")

        # Busca candidatos pendentes
        res = supa.table('candidatos').select('id, username, nome_completo').is_('last_scraped_at', 'null').limit(limit).execute()
        targets = res.data
        if not targets:
            print("✅ Tudo raspado.")
            await browser_context.close()
            return

        for t in targets:
            uname = t['username']
            cid = t['id']
            print(f"\n🔍 @{uname}")
            try:
                await page.goto(f"https://www.instagram.com/{uname}/", wait_until="networkidle")
                await asyncio.sleep(4)
                
                # Marcar como processado
                supa.table('candidatos').update({'last_scraped_at': datetime.utcnow().isoformat()}).eq('id', cid).execute()
                
                # Pegar posts
                posts = await page.query_selector_all('article a[href*="/p/"], article a[href*="/reel/"]')
                
                for i, p in enumerate(posts[:3]):
                    try:
                        href = await p.get_attribute("href")
                        shortcode = href.split("/p/")[1].split("/")[0] if "/p/" in href else href.split("/reel/")[1].split("/")[0]
                        
                        await p.click()
                        await asyncio.sleep(4)
                        
                        print(f"  📸 Post: {shortcode}")
                        
                        # Extrair comentários
                        elements = await page.query_selector_all('div.x9f619 span[dir="auto"]')
                        texts = []
                        for el in elements:
                            txt = await el.inner_text()
                            if txt and len(txt) > 10:
                                texts.append(txt)
                        
                        unique_texts = list(dict.fromkeys(texts))[-20:]
                        for txt in unique_texts:
                            txt_hash = hashlib.md5(f"{uname}_{txt}".encode()).hexdigest()[:12]
                            data = {
                                "id_externo": f"pw_{txt_hash}",
                                "candidato_id": uname,
                                "post_id": shortcode,
                                "autor_username": "stealth_user",
                                "texto_bruto": txt,
                                "plataforma": "INSTAGRAM",
                                "data_coleta": datetime.utcnow().isoformat(),
                                "processado_ia": False
                            }
                            try:
                                supa.table('comentarios').upsert(data, on_conflict='id_externo').execute()
                            except: pass
                        
                        # Fechar modal
                        await page.keyboard.press("Escape")
                        await asyncio.sleep(2)
                    except Exception as post_err:
                        print(f"  ❌ Erro no post: {post_err}")
                        await page.go_back()
                        await asyncio.sleep(2)

            except Exception as e:
                print(f"❌ Erro em @{uname}: {e}")

        await browser_context.close()
        print("\n🏁 Coleta finalizada.")

if __name__ == "__main__":
    asyncio.run(scrape_instagram_stealth(limit=15))
