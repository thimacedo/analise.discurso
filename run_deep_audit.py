import asyncio
from playwright.async_api import async_playwright
import json

async def audit():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        base = "https://sentinela-democratica.vercel.app"
        report = []

        async def check_url(path, selector):
            print(f"📡 Checando {path}...")
            try:
                res = await page.goto(f"{base}{path}", wait_until="networkidle")
                visible = await page.is_visible(selector) if selector else True
                status = "OK" if (res.status < 400 and visible) else "BROKEN"
                report.append({"url": path, "status": status, "code": res.status, "ui": visible})
            except Exception as e:
                report.append({"url": path, "status": "FAIL", "error": str(e)})

        # Testar Rotas
        await check_url("/", "#chartMain")
        await check_url("/admin", "#tab-review")
        await check_url("/docs/metodologia", "h1")
        await check_url("/docs/analise-violencia", ".kpi-value")
        
        # Testar Navegação Hash (Mapa e Dossiê)
        await page.goto(base)
        await page.click("a[href='#map']")
        await page.wait_for_timeout(2000)
        map_ok = await page.is_visible("#svg-map-br")
        report.append({"url": "#map", "status": "OK" if map_ok else "BROKEN"})

        await page.click("a[href='#dossie']")
        await page.wait_for_timeout(2000)
        dossie_ok = await page.is_visible("#dossie-grid")
        report.append({"url": "#dossie", "status": "OK" if dossie_ok else "BROKEN"})

        with open("deep_audit_report.json", "w") as f:
            json.dump(report, f, indent=2)
        print("✅ Auditoria Finalizada.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(audit())
