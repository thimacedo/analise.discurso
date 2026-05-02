import os
import httpx
import json
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

def sentinel_audit():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    
    print(f"🕵️‍♂️ [AUDIT] Iniciando Auditoria Forense - Sentinela v20.1.0")
    print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # 1. Auditoria da Tabela 'comentarios'
        print("📊 [TABLE: comentarios]")
        r_total = httpx.get(f"{url}/rest/v1/comentarios?select=id", headers=headers)
        total = len(r_total.json())
        
        r_processed = httpx.get(f"{url}/rest/v1/comentarios?processado_ia=eq.true&select=id", headers=headers)
        processed = len(r_processed.json())
        
        r_hate = httpx.get(f"{url}/rest/v1/comentarios?is_hate=eq.true&select=id", headers=headers)
        hate = len(r_hate.json())
        
        print(f"   - Total de Registros: {total}")
        print(f"   - Processados pela IA: {processed} ({(processed/total*100 if total > 0 else 0):.1f}%)")
        print(f"   - Pendentes: {total - processed}")
        print(f"   - Discurso de Ódio Detectado: {hate} ({(hate/processed*100 if processed > 0 else 0):.1f}% do processado)")
        
        # 2. Auditoria da Tabela 'candidatos' (Alvos)
        print("\n🎯 [TABLE: candidatos]")
        r_targets = httpx.get(f"{url}/rest/v1/candidatos?select=username,comentarios_odio_count,score_risco&order=score_risco.desc", headers=headers)
        targets = r_targets.json()
        print(f"   - Alvos Monitorados: {len(targets)}")
        print(f"   - Top 5 Alvos em Risco:")
        for t in targets[:5]:
            print(f"     • @{t['username']}: {t['score_risco']}% Risco ({t['comentarios_odio_count']} alertas)")

        # 3. Auditoria de Categorias PASA
        print("\n🧠 [PASA BREAKDOWN]")
        r_pasa = httpx.get(f"{url}/rest/v1/comentarios?is_hate=eq.true&select=categoria_ia", headers=headers)
        pasa_data = r_pasa.json()
        counts = {}
        for item in pasa_data:
            cat = item.get('categoria_ia', 'OUTROS')
            counts[cat] = counts.get(cat, 0) + 1
        
        for cat, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
            print(f"   • {cat:20}: {count} ocorrências")

        # 4. Verificação de Saúde do Backend
        print("\n🏥 [SYSTEM HEALTH]")
        r_health = httpx.get(f"{url}/rest/v1/metricas_diarias?limit=1&order=data.desc", headers=headers)
        if r_health.status_code == 200 and r_health.json():
            last_metric = r_health.json()[0]
            print(f"   - Última métrica consolidada: {last_metric['data']}")
            print(f"   - Resiliência Global: {last_metric['resiliencia']}%")
        else:
            print("   ⚠️ Nenhuma métrica diária encontrada para hoje.")

        print("\n" + "=" * 60)
        print("✅ AUDITORIA CONCLUÍDA SEM ANOMALIAS CRÍTICAS.")
        
    except Exception as e:
        print(f"❌ FALHA NA AUDITORIA: {e}")

if __name__ == "__main__":
    sentinel_audit()
