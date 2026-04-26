import json
import logging
import os
import httpx
import asyncio
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

async def consolidar_kpis_dashboard():
    """
    Sincroniza os contadores globais do banco de dados Supabase para alimentar 
    os painéis dinâmicos da plataforma Sentinela Core.
    """
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    
    output_path = "data/sentinela_kpis_sync.json"
    log_path = 'error.log'
    
    print("🔄 Consolidando Inteligência Analítica...")

    try:
        async with httpx.AsyncClient() as client:
            # 1. Total de Ódio Detectado
            res_hate = await client.get(f"{url}/rest/v1/comentarios?is_hate=eq.true&select=id", headers=headers)
            odio_total = len(res_hate.json()) if res_hate.status_code == 200 else 0
            
            # 2. Total de Alvos Ativos
            res_targets = await client.get(f"{url}/rest/v1/candidatos?status_monitoramento=ilike.Ativo&select=id", headers=headers)
            alvos_total = len(res_targets.json()) if res_targets.status_code == 200 else 0

            payload = {
                "motor_inteligencia": "PASA v3.0",
                "timestamp": datetime.now().isoformat(),
                "metricas_globais": {
                    "odio_absoluto": odio_total,
                    "monitoramento_ativo": alvos_total,
                    "frequencia_crise": "1 a cada 1h30"
                }
            }

            # Garantir diretório data/
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as file:
                json.dump(payload, file, ensure_ascii=False, indent=4)
            
            print(f"✅ Sincronização concluída: {odio_total} alertas mapeados.")
            return True

    except Exception as e:
        logging.basicConfig(filename=log_path, level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
        logging.error(f"Falha na sincroniza&ccedil;&atilde;o de KPIs: {str(e)}")
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(consolidar_kpis_dashboard())
