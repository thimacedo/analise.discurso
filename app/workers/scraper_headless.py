"""
PASA v49 - Instagram Scraper Headless (Playwright)
Coleta via navegação real com injeção de sessão e extração por modal.
"""
import asyncio
import json
import logging
import os
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from playwright.async_api import async_playwright, BrowserContext, Page

logger = logging.getLogger("ScraperHeadless")


class InstagramScraperHeadless:
    def __init__(self, target_profile: str, max_posts: int = 5, max_comments: int = 20):
        self.target_profile = target_profile
        self.max_posts = max_posts
        self.max_comments = max_comments
        self.browser = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    # ------------------------------------------------------------------ #
    #  MÉTODO FALTANTE - Injeção de Cookies no BrowserContext
    # ------------------------------------------------------------------ #
    async def _inject_cookies(self, cookies: Any) -> bool:
        """
        Injeta cookies de sessão do Instagram no BrowserContext do Playwright.
        Aceita string JSON, lista de dicts ou lista de objetos Supabase.
        Retorna True se a injeção teve sucesso.
        """
        if not cookies:
            logger.warning("⚠️ Nenhum cookie fornecido para injeção.")
            return False

        if not self.context:
            logger.error("❌ BrowserContext não inicializado. Não é possível injetar cookies.")
            return False

        try:
            # Normaliza o formato dos cookies
            parsed_cookies = self._normalize_cookies(cookies)

            if not parsed_cookies:
                logger.warning("⚠️ Lista de cookies vazia após normalização.")
                return False

            await self.context.add_cookies(parsed_cookies)
            logger.info(f"✅ {len(parsed_cookies)} cookies injetados com sucesso no contexto Playwright.")
            return True

        except Exception as e:
            logger.error(f"❌ Falha ao injetar cookies: {e}")
            return False

    def _normalize_cookies(self, raw_cookies: Any) -> List[Dict[str, Any]]:
        """
        Normaliza cookies de qualquer formato de entrada para o formato Playwright:
        { name, value, domain, path, httpOnly, secure, sameSite }
        """
        playw_cookies = []

        # Se é string, tenta parsear como JSON
        if isinstance(raw_cookies, str):
            try:
                raw_cookies = json.loads(raw_cookies)
            except json.JSONDecodeError:
                # Tenta parsear como header Cookie: key=val; key2=val2
                for pair in raw_cookies.split(";"):
                    pair = pair.strip()
                    if "=" in pair:
                        k, v = pair.split("=", 1)
                        playw_cookies.append({
                            "name": k.strip(),
                            "value": v.strip(),
                            "domain": ".instagram.com",
                            "path": "/",
                        })
                return playw_cookies

        # Se é lista
        if isinstance(raw_cookies, list):
            for c in raw_cookies:
                if isinstance(c, dict):
                    # Já está no formato do Playwright?
                    if "name" in c and "value" in c:
                        cookie = {
                            "name": c["name"],
                            "value": c["value"],
                            "domain": c.get("domain", ".instagram.com"),
                            "path": c.get("path", "/"),
                            "httpOnly": c.get("httpOnly", False),
                            "secure": c.get("secure", True),
                            "sameSite": c.get("sameSite", "Lax"),
                        }
                        # Playwright não aceita 'sameSite: None' como string em algumas versões
                        if cookie["sameSite"] not in ("Strict", "Lax", "None"):
                            cookie["sameSite"] = "Lax"
                        playw_cookies.append(cookie)
                    # Formato Supabase/Netscape alternativo
                    elif "key" in c or "name" in c:
                        name = c.get("name") or c.get("key", "")
                        value = c.get("value") or c.get("val", "")
                        if name:
                            playw_cookies.append({
                                "name": name,
                                "value": str(value),
                                "domain": c.get("domain", ".instagram.com"),
                                "path": c.get("path", "/"),
                                "httpOnly": c.get("httpOnly", False),
                                "secure": c.get("secure", True),
                                "sameSite": c.get("sameSite", "Lax"),
                            })

        return playw_cookies

    # ------------------------------------------------------------------ #
    #  Ciclo de Vida do Navegador
    # ------------------------------------------------------------------ #
    async def _launch_browser(self, headless: bool = True) -> BrowserContext:
        """Inicializa o Playwright e cria um BrowserContext com stealth."""
        self._playwright = await async_playwright().start()
        self.browser = await self._playwright.chromium.launch(
            headless=headless,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-infobars",
            ],
        )
        self.context = await self.browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
            locale="pt-BR",
        )

        # Anti-detecção: Remove navigator.webdriver
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            delete navigator.__proto__.webdriver;
        """)

        self.page = await self.context.new_page()
        return self.context

    async def close(self):
        """Fecha navegador e recursos."""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if hasattr(self, "_playwright"):
                await self._playwright.stop()
        except Exception:
            pass

    # ------------------------------------------------------------------ #
    #  Raspagem Principal
    # ------------------------------------------------------------------ #
    async def fetch_recent_posts(
        self, external_cookies: Any = None
    ) -> List[Dict[str, Any]]:
        """
        Raspagem completa: injeta cookies, navega ao perfil, 
        extrai posts e comentários via modal.
        """
        logger.info(f"🚀 Iniciando Playwright para: {self.target_profile}")

        try:
            await self._launch_browser(headless=True)

            # INJEÇÃO DE COOKIES - O método que faltava
            if external_cookies:
                injected = await self._inject_cookies(external_cookies)
                if not injected:
                    logger.warning("⚠️ Continuando sem cookies de sessão - pode enfrentar login wall.")

            # Navegar para o perfil
            profile_url = f"https://www.instagram.com/{self.target_profile}/"
            await self.page.goto(profile_url, wait_until="networkidle", timeout=30000)
            await asyncio.sleep(2)

            # Verificar se caiu na tela de login
            if await self._is_login_wall():
                logger.error("❌ Login Wall detectado. Cookies inválidos ou expirados.")
                return []

            # Verificar se o perfil existe
            if await self._is_profile_not_found():
                logger.error(f"❌ Perfil @{self.target_profile} não encontrado (404).")
                return []

            # Extrair links dos posts recentes
            post_links = await self._extract_post_links()
            if not post_links:
                logger.warning(f"⚠️ Nenhum post encontrado para @{self.target_profile}.")
                return []

            logger.info(f"📋 Encontrados {len(post_links)} posts. Coletando comentários...")

            # Coletar dados de cada post via modal
            detailed_posts = []
            for i, link in enumerate(post_links[:self.max_posts]):
                logger.info(f"  📖 [{i+1}/{min(len(post_links), self.max_posts)}] {link}")
                post_data = await self._scrape_post_via_modal(link)
                if post_data:
                    detailed_posts.append(post_data)
                await asyncio.sleep(1.5)  # Delay humano entre posts

            return detailed_posts

        except Exception as e:
            logger.error(f"💥 Erro geral na raspagem Playwright: {e}")
            return []
        finally:
            await self.close()

    # ------------------------------------------------------------------ #
    #  Métodos Auxiliares
    # ------------------------------------------------------------------ #
    async def _is_login_wall(self) -> bool:
        """Detecta se a página redirecionou para login."""
        try:
            return await self.page.locator('input[name="username"]').count() > 0
        except Exception:
            return False

    async def _is_profile_not_found(self) -> bool:
        """Detecta página de perfil inexistente."""
        try:
            text = await self.page.locator("body").inner_text()
            return "Sorry, this page isn't available" in text or "não está disponível" in text
        except Exception:
            return False

    async def _extract_post_links(self) -> List[str]:
        """Extrai links de posts da grade do perfil."""
        links = []
        try:
            # Espera os links de posts carregarem
            await self.page.wait_for_selector('a[href*="/p/"], a[href*="/reel/"]', timeout=15000)
            anchors = await self.page.query_selector_all('a[href*="/p/"], a[href*="/reel/"]')
            seen = set()
            for a in anchors:
                href = await a.get_attribute("href")
                if href and href not in seen:
                    # Normaliza URL completa
                    if href.startswith("/"):
                        href = f"https://www.instagram.com{href}"
                    links.append(href)
                    seen.add(href)
        except Exception as e:
            logger.error(f"Erro ao extrair links de posts: {e}")
        return links

    async def _scrape_post_via_modal(self, post_url: str) -> Optional[Dict[str, Any]]:
        """Abre um post no modal e extrai legenda + comentários."""
        try:
            await self.page.goto(post_url, wait_until="networkidle", timeout=20000)
            await asyncio.sleep(1.5)

            # Legenda (geralmente o primeiro bloco de texto longo)
            caption = ""
            try:
                # Tenta pegar o texto da legenda no modal
                caption_el = self.page.locator('ul li div[role="button"] span').first
                if await caption_el.count() > 0:
                    caption = await caption_el.inner_text()
            except Exception:
                pass

            # Shortcode
            shortcode_match = re.search(r'/(?:p|reel)/([^/?#&]+)', post_url)
            shortcode = shortcode_match.group(1) if shortcode_match else "unknown"

            # Comentários
            comments = []
            try:
                # Scroll para carregar mais comentários
                comment_list = self.page.locator('ul ul li')  # Estrutura comum de comentários
                count = await comment_list.count()

                for idx in range(min(count, self.max_comments)):
                    try:
                        item = comment_list.nth(idx)
                        # Username
                        username_el = item.locator('a[role="link"] span').first
                        username = ""
                        if await username_el.count() > 0:
                            username = (await username_el.inner_text()).strip()

                        # Texto do comentário (spans após o username)
                        text_parts = item.locator('span')
                        text = ""
                        if await text_parts.count() > 1:
                            text = (await text_parts.nth(1).inner_text()).strip()

                        if text and len(text) > 2:
                            comments.append({
                                "id": f"pw_{hash(text)}_{idx}",
                                "text": text,
                                "ownerUsername": username or "unknown",
                                "timestamp": None,
                            })
                    except Exception:
                        continue

            except Exception as e:
                logger.warning(f"⚠️ Erro ao extrair comentários do modal: {e}")

            return {
                "shortcode": shortcode,
                "text": caption or "[Extraído via Playwright]",
                "timestamp": None,
                "comments": comments,
            }

        except Exception as e:
            logger.error(f"❌ Erro ao raspar post {post_url}: {e}")
            return None


# ------------------------------------------------------------------ #
#  Teste Standalone - Seleção Ponderada do Supabase
# ------------------------------------------------------------------ #
async def main():
    import random
    from datetime import datetime, timezone
    from core.supabase_service import supabase as db

    COOLDOWN_HOURS = 12

    target = None
    nome = ""

    try:
        # 1. Busca candidatos com métricas de atividade
        res = db.table('candidatos') \
            .select('username, nome_completo, last_scraped_at, comentarios_odio_count, comentarios_totais_count, prioridade_coleta') \
            .eq('status_monitoramento', 'Ativo') \
            .execute()

        if not res.data:
            print("❌ Nenhum candidato ativo encontrado no Supabase.")
            return

        # 2. Filtra candidatos fora de cooldown
        candidatos_viaveis = []
        for c in res.data:
            last = c.get('last_scraped_at')
            if last:
                try:
                    last_dt = datetime.fromisoformat(str(last).replace('Z', '+00:00'))
                    hours_since = (datetime.now(timezone.utc) - last_dt).total_seconds() / 3600
                    if hours_since < COOLDOWN_HOURS:
                        continue
                except Exception:
                    pass
            candidatos_viaveis.append(c)

        if not candidatos_viaveis:
            print(f"⚠️ Todos os {len(res.data)} candidatos estão em cooldown ({COOLDOWN_HOURS}h).")
            print("Sorteando entre todos mesmo assim...")
            candidatos_viaveis = res.data

        # 3. Calcula os Pesos (Roleta Ponderada)
        PESO_BASE = 10
        candidatos_com_peso = []
        
        for c in candidatos_viaveis:
            odio = c.get('comentarios_odio_count') or 0
            total = c.get('comentarios_totais_count') or 0
            prio = c.get('prioridade_coleta') or 0
            
            # Fórmula de prioridade
            score = PESO_BASE + (odio * 5) + (total * 1) + (prio * 50)
            
            candidatos_com_peso.append({
                "candidato": c,
                "peso": score
            })

        # 4. Sorteio utilizando random.choices (suporta pesos nativamente)
        populacao = [item["candidato"] for item in candidatos_com_peso]
        pesos = [item["peso"] for item in candidatos_com_peso]
        
        # random.choices retorna uma lista, pegamos o primeiro elemento
        candidato = random.choices(populacao, weights=pesos, k=1)[0]
        
        target = candidato['username']
        nome = candidato.get('nome_completo') or target
        peso_sorteado = next(item["peso"] for item in candidatos_com_peso if item["candidato"]["username"] == target)

        # Mostra o Top 3 para comparação visual
        top_3 = sorted(candidatos_com_peso, key=lambda x: x["peso"], reverse=True)[:3]

        print("🎲 ─────────────────────────────────────────")
        print(f"🎯 Alvo sorteado: @{target} ({nome}) | Peso: {peso_sorteado}")
        print(f"📊 Viáveis: {len(candidatos_viaveis)}/{len(res.data)} candidatos")
        print("🏆 Top 3 Mais Prováveis:")
        for i, t in enumerate(top_3):
            c = t["candidato"]
            print(f"   {i+1}. @{c['username']} (Peso: {t['peso']} | Ódio: {c.get('comentarios_odio_count', 0)})")
        print("─────────────────────────────────────────────")

    except Exception as e:
        print(f"❌ Erro ao buscar candidatos do Supabase: {e}")
        import traceback
        traceback.print_exc()
        print("⚠️ Usando fallback padrão...")
        target = "cironogueira"

    # 5. Executa a raspagem
    scraper = InstagramScraperHeadless(target, max_posts=2, max_comments=15)

    # Tenta buscar cookies de sessão ativa
    cookies = None
    try:
        session_res = db.table("worker_sessions") \
            .select("cookies") \
            .eq("plataforma", "instagram") \
            .eq("status", "active") \
            .order("updated_at", desc=True) \
            .limit(1) \
            .execute()
        if session_res.data:
            cookies = session_res.data[0].get("cookies")
            if cookies:
                print(f"🔑 Sessão ativa encontrada. Cookies serão injetados.")
    except Exception:
        print("⚠️ Sessão de cookies não disponível. Prosseguindo sem autenticação.")

    posts = await scraper.fetch_recent_posts(external_cookies=cookies)

    if posts:
        total_comments = sum(len(p.get("comments", [])) for p in posts)
        print(f"\n✅ Coleta concluída: {len(posts)} posts | {total_comments} comentários")
    else:
        print(f"\n❌ Nenhum dado coletado para @{target}")

    print(json.dumps(posts, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())
