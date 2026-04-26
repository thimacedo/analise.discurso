import asyncio
from playwright.async_api import async_playwright
import json

async def run_audit():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        console_logs = []
        network_errors = []
        
        page.on("console", lambda msg: console_logs.append({"type": msg.type, "text": msg.text}))
        page.on("requestfailed", lambda req: network_errors.append({"url": req.url, "error": req.failure.error_text}))
        page.on("response", lambda res: network_errors.append({"url": res.url, "status": res.status}) if res.status >= 400 else None)

        url = "https://sentinela-democratica.vercel.app/"
        print(f"🔍 Auditando {url}...")
        
        try:
            await page.goto(url, wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(5000) # Esperar renderização de IA
            
            # Captura de elementos críticos
            elements = {
                "chartMain": await page.inner_html("#chartMain"),
                "feedAlertas": await page.inner_html("#feed-alertas"),
                "predictive": await page.inner_html("#predictive-trends")
            }
            
            report = {
                "url": url,
                "status": "online",
                "console": console_logs,
                "network": network_errors,
                "ui": elements
            }
            
            with open("prod_audit_report.json", "w", encoding="utf-8") as f:
                json.dump(report, f, indent=4, ensure_ascii=False)
            
            print("✅ Auditoria finalizada. Relatório gerado.")
            
        except Exception as e:
            print(f"❌ Falha crítica no teste: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run_audit())
