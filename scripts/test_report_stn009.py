
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from processing.report_generator import ReportGenerator
import os

async def test_executive_report():
    print("\n🛡️ [Sentinela] Testando Geração de Dossiê Executivo (STN-009)...")
    
    # 1. Simulação de Dados Robustos
    dates = [datetime.now() - timedelta(days=x) for x in range(10, 0, -1)]
    data = []
    
    categories = ["ODIO_IDENTITARIO", "VIOLENCIA_GENERO", "AMEACA", "INSULTO_AD_HOMINEM", "ATAQUE_INSTITUCIONAL", "RIGOR_CRIMINAL", "NEUTRO"]
    
    for i in range(100):
        is_hate = i < 70 # 70% de ódio para o teste
        cat = np.random.choice(categories[:-1]) if is_hate else "NEUTRO"
        data.append({
            "id": f"uuid-{i}",
            "candidato_id": "candidato_premium",
            "owner_username": f"usuario_{i}",
            "text": f"Texto de exemplo número {i} com sinais de {cat} para validação do Protocolo PASA v16.4.",
            "is_hate_speech": is_hate,
            "category": cat,
            "data_coleta": np.random.choice(dates).isoformat(),
            "plataforma": "instagram"
        })
        
    df = pd.DataFrame(data)
    
    # 2. Geração do PDF
    rg = ReportGenerator()
    output_path = "data/reports/teste_executivo_diamond.pdf"
    os.makedirs("data/reports", exist_ok=True)
    
    print("🎨 Renderizando gráficos e estruturando documento...")
    rg.generate_pdf(df, output_path)
    
    if os.path.exists(output_path):
        print(f"✅ Dossiê gerado com sucesso: {output_path}")
        print(f"📊 Tamanho do arquivo: {os.path.getsize(output_path) / 1024:.1f} KB")
    else:
        print("❌ Falha na geração do arquivo.")

if __name__ == "__main__":
    asyncio.run(test_executive_report())
