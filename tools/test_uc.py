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
