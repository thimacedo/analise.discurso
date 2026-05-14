# scripts/generate_telemetry_report.py
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.supabase_service import get_supabase_client

def generate_report():
    db = get_supabase_client()
    
    # Ranking de Workers por XP
    ledger = db.table('worker_ledger').select('*').order('current_xp', desc=True).execute()
    
    # Últimas falhas críticas
    failures = db.table('worker_runs')\
        .select('worker_name, error_message, started_at')\
        .eq('status', 'failure')\
        .order('started_at', desc=True)\
        .limit(10)\
        .execute()
    
    report = "# 📊 PASA v17 - Relatório de Telemetria\n\n"
    
    report += "## 🏆 Ranking de Evolução (XP)\n"
    report += "| Worker | Nível | XP | Runs | Critical Hits | Extrações Sucesso |\n"
    report += "|---|---|---|---|---|---|\n"
    for w in (ledger.data or []):
        report += f"| {w['worker_name']} | {w['current_level']} | {w['current_xp']} | {w['total_runs']} | {w['critical_hits']} | {w['successful_extractions']} |\n"
    
    report += "\n## 🚨 Últimas Falhas Críticas\n"
    if failures.data:
        for f in failures.data:
            report += f"- **{f['worker_name']}** ({f['started_at']}): {f['error_message']}\n"
    else:
        report += "Nenhuma falha recente registrada.\n"
    
    # Salva em docs/TELEMETRY.md
    output_path = PROJECT_ROOT / 'docs' / 'TELEMETRY.md'
    output_path.parent.mkdir(exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
        
    print(f"✅ Relatório gerado com sucesso em {output_path}")

if __name__ == "__main__":
    generate_report()
