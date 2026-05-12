
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
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
    
    print(f"🕵️‍♂️ [AUDIT] Auditoria Forense Completa - Sentinela v20.1.1")
    print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 60)
    
    try:
        # 1. Auditoria da Tabela 'comentarios'
        print("📊 [ESTATÍSTICAS DE COMENTÁRIOS]")
        r_total = httpx.get(f"{url}/rest/v1/comentarios?select=id", headers=headers)
        total = len(r_total.json())
        
        r_processed = httpx.get(f"{url}/rest/v1/comentarios?processado_ia=eq.true&select=id", headers=headers)
        processed = len(r_processed.json())
        
        r_hate = httpx.get(f"{url}/rest/v1/comentarios?is_hate=eq.true&select=id", headers=headers)
        hate = len(r_hate.json())
        
        print(f"   • Total na Base       : {total}")
        print(f"   • Processamento IA    : {processed} ({(processed/total*100 if total > 0 else 0):.1f}%)")
        print(f"   • Alertas de Ódio     : {hate} ({(hate/processed*100 if processed > 0 else 0):.1f}%)")
        
        # 2. Auditoria da Tabela 'candidatos'
        print("\n🎯 [ESTADO DOS ALVOS]")
        # Colunas reais via introspecção: username, nome_completo, score_risco, comentarios_odio_count
        r_targets = httpx.get(f"{url}/rest/v1/candidatos?select=username,nome_completo,score_risco,comentarios_odio_count&order=score_risco.desc", headers=headers)
        targets = r_targets.json()
        if isinstance(targets, list) and len(targets) > 0:
            print(f"   • Alvos Ativos: {len(targets)}")
            for t in targets:
                print(f"     - @{t.get('username', '???'):15} | Risco: {t.get('score_risco', 0):3}% | Alertas: {t.get('comentarios_odio_count', 0)}")
        else:
            print("   ⚠️ Nenhum alvo encontrado ou erro de acesso.")

        # 3. Distribuição PASA
        print("\n🧠 [DISTRIBUIÇÃO DE CATEGORIAS PASA]")
        r_pasa = httpx.get(f"{url}/rest/v1/comentarios?is_hate=eq.true&select=categoria_ia", headers=headers)
        pasa_data = r_pasa.json()
        counts = {}
        for item in pasa_data:
            cat = item.get('categoria_ia', 'OUTROS')
            counts[cat] = counts.get(cat, 0) + 1
        
        for cat, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
            pct = (count / hate * 100) if hate > 0 else 0
            print(f"   • {cat:20}: {count:4} ({pct:4.1f}%)")

        # 4. Auditoria de Redes Sociais
        print("\n🌐 [ORIGEM DOS DADOS]")
        r_social = httpx.get(f"{url}/rest/v1/comentarios?select=plataforma", headers=headers)
        social_data = r_social.json()
        s_counts = {}
        for item in social_data:
            plat = item.get('plataforma', 'INSTAGRAM')
            s_counts[plat] = s_counts.get(plat, 0) + 1
        for plat, count in s_counts.items():
            print(f"   • {plat:20}: {count:4}")

        print("\n" + "=" * 60)
        print("✅ AUDITORIA CONCLUÍDA - SISTEMA EM ESTADO DIAMOND.")
        
    except Exception as e:
        print(f"❌ FALHA NA AUDITORIA: {e}")

if __name__ == "__main__":
    sentinel_audit()
