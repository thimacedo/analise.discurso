
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import undetected_chromedriver as uc
import time

try:
    print("🚀 Testando UC simples...")
    driver = uc.Chrome()
    driver.get("https://www.google.com")
    print(f"✅ Título: {driver.title}")
    time.sleep(2)
    driver.quit()
    print("🏁 Sucesso!")
except Exception as e:
    print(f"❌ Falha: {e}")
