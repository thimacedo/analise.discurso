import asyncio
from playwright.async_api import async_playwright
import os
import sys
import json
import hashlib
from datetime import datetime, UTC
from core.db import db_client 

# Import do contrato BaseWorker
sys.path.append(r"E:\Projetos\sentinela-democratica")
from workers.core.base_worker import BaseWorker

USER_DATA_DIR = os.path.join(os.getcwd(), "browser_profile_tmp")
PROFILE_DIR = "Default"

class InstagramScraperWorker(BaseWorker):
    def __init__(self, name="InstagramScraper"):
        super().__init__(name)

    async def _run(self, username="lulaoficial", *args, **kwargs):
        async with async_playwright() as p:
            self.logger.info(f"🚀 Lançando Chrome com perfil persistente...")
            context = await p.chromium.launch_persistent_context(
                user_data_dir=USER_DATA_DIR,
                channel="chrome",
                headless=False,
                args=[f"--profile-directory={PROFILE_DIR}", "--start-maximized"]
            )
            page = await context.new_page()
            
            self.logger.info(f"🌍 Alvo: @{username}")
            await page.goto(f"https://www.instagram.com/{username}/", wait_until="domcontentloaded", timeout=60000)
            await asyncio.sleep(5)
            
            post_links = await page.evaluate('''() => {
                return Array.from(document.querySelectorAll('a'))
                            .map(a => a.href)
                            .filter(href => href.includes('/p/') || href.includes('/reel/'))
                            .slice(0, 5); // Diamond: Pega os 5 mais recentes
            }''')

            if not post_links:
                self.logger.warning(f"⚠️ Nenhum post encontrado para @{username}. Verifique se a conta é privada ou houve bloqueio.")
                await context.close()
                return

            self.logger.info(f"🔍 Encontrados {len(post_links)} links para navegação profunda.")

            for post_url in post_links:
                # Extrair shortcode da URL (funciona para https://.../p/ABC/ ou /p/ABC/)
                parts = post_url.strip('/').split('/')
                shortcode = parts[-1] if parts[-1] != 'reel' and parts[-1] != 'p' else parts[-2]
                self.logger.info(f"  📸 Abrindo Post: {shortcode} ({post_url})")
                
                try:
                    await page.goto(post_url, wait_until="domcontentloaded")
                    await asyncio.sleep(4)

                    # Tenta carregar mais comentários (clicando no botão de "+" se existir)
                    # O seletor de "carregar mais" costuma ser um SVG de "+" ou texto específico
                    for _ in range(3): # Tenta expandir 3 vezes
                        try:
                            load_more_button = page.locator('svg[aria-label="Carregar mais comentários"], svg[aria-label="Load more comments"]').first
                            if await load_more_button.is_visible():
                                await load_more_button.click()
                                await asyncio.sleep(2)
                            else:
                                break
                        except:
                            break

                    # 2. Extrair Comentários Estruturados
                    extracted_data = await page.evaluate('''() => {
                        // Seletor para os blocos de comentários (li ou div dependendo do layout)
                        const commentNodes = document.querySelectorAll('ul._a9z6 li div._a9zs span, div.x9f619 span[dir="auto"]');
                        return Array.from(commentNodes)
                                    .map(el => {
                                        const text = el.innerText.trim();
                                        // Tenta encontrar o autor (geralmente um link próximo)
                                        const authorEl = el.closest('div')?.querySelector('a[href*="/"]');
                                        const author = authorEl ? authorEl.innerText : 'unknown';
                                        return { author, text };
                                    })
                                    .filter(c => c.text.length > 5);
                    }''')

                    self.logger.info(f"     ✅ {len(extracted_data)} comentários extraídos do post {shortcode}.")

                    for data in extracted_data[:50]: # Limite aumentado para 50 na navegação profunda
                        comment_text = data['text']
                        author = data['author']
                        
                        try:
                            # Hash ID inclui autor para maior unicidade
                            hash_input = f"{shortcode}_{author}_{comment_text}"
                            hash_id = hashlib.md5(hash_input.encode()).hexdigest()[:16]
                            id_externo = f"ig_{hash_id}"

                            res = db_client.client.table('comentarios').upsert({
                                'candidato_id': username,
                                'post_id': shortcode,
                                'autor_username': author, # Ajustado de 'autor' para 'autor_username' conforme schema visto no inspect_db
                                'texto_bruto': comment_text,
                                'plataforma': 'INSTAGRAM',
                                'data_coleta': datetime.now(UTC).isoformat(),
                                'processado_ia': False,
                                'id_externo': id_externo 
                            }, on_conflict='id_externo').execute()
                        except Exception as e:
                            self.logger.error(f"⚠️ Erro ao persistir comentário: {e}")
                            if hasattr(e, 'message'):
                                self.logger.error(f"   Destaque: {e.message}")                
                except Exception as e:
                    self.logger.error(f"❌ Erro ao processar post {shortcode}: {e}")
            
            # 3. Atualizar carimbo de tempo no candidato
            db_client.client.table('candidatos').update({
                'last_scraped_at': datetime.now(UTC).isoformat()
            }).eq('username', username).execute()

            await context.close()

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    target = sys.argv[1] if len(sys.argv) > 1 else "lulaoficial"
    worker = InstagramScraperWorker()
    asyncio.run(worker.execute(username=target))
