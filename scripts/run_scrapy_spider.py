# scripts/run_scrapy_spider.py (VERSÃO FINAL)
import subprocess
import sys
from pathlib import Path

def main():
    if len(sys.argv) < 6:
        print("❌ Uso: python run_scrapy_spider.py <spider> <user> <session> <posts> <output>")
        print("Exemplo: python run_scrapy_spider.py instagram_api bolsonaro SESSIONID 3 out.json")
        sys.exit(1)
    
    spider = sys.argv[1]
    username = sys.argv[2]
    session = sys.argv[3]
    posts = sys.argv[4]
    output = sys.argv[5]
    
    # Usa scrapy como módulo (mais confiável e resolve o erro de 'Spider not found')
    # O cwd deve ser o diretório onde está o scrapy.cfg
    cmd = [
        sys.executable, "-m", "scrapy", "crawl", spider,
        "-a", f"username={username}",
        "-a", f"sessionid={session}",
        "-a", f"max_posts={posts}",
        "-o", str(Path(output).resolve()),
        "-L", "INFO"
    ]
    
    print(f"🚀 {spider.upper()} - @{username}")
    print(f"📁 Output: {output}")
    
    # O diretório 'sentinela_scrapy' contém o scrapy.cfg necessário
    result = subprocess.run(cmd, cwd="sentinela_scrapy", capture_output=False)
    sys.exit(result.returncode)

if __name__ == '__main__':
    main()
