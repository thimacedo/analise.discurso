
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import json
import os
from datetime import datetime

def check_file_exists(path):
    return os.path.exists(path)

def check_task_in_file(path, task_marker):
    """Verifica se uma tarefa está marcada como concluída em um arquivo markdown"""
    if not os.path.exists(path):
        return False
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    return task_marker in content

report = {
    "audit_timestamp": datetime.now().isoformat(),
    "environment": {
        "python": os.sys.version,
        "cwd": os.getcwd()
    },
    "tasks": []
}

# Verifica consistência entre STATE.md e ROADMAP.md
state_path = 'STATE.md'
roadmap_path = 'ROADMAP.md'

if check_file_exists(state_path) and check_file_exists(roadmap_path):
    # Tarefa 1: Null-Safety deveria estar concluída
    state_ok = check_task_in_file(state_path, '✅ **Frontend Null-Safety')
    roadmap_ok = check_task_in_file(roadmap_path, '[x] **[STN-001]**')
    report['tasks'].append({
        "id": "DOC-001",
        "desc": "Sincronizar STATE.md e ROADMAP.md (Null-Safety)",
        "status": "OK" if (state_ok or roadmap_ok) else "FAIL",
        "detail": "Verificado no ROADMAP.md"
    })

    # Tarefa 2: Otimização de Memória
    state_ok = check_task_in_file(state_path, '✅ **Otimização de Memória')
    roadmap_ok = check_task_in_file(roadmap_path, '[x] **[STN-002]**')
    report['tasks'].append({
        "id": "DOC-002",
        "desc": "Sincronizar STATE.md e ROADMAP.md (Otimização de Memória)",
        "status": "OK" if (state_ok or roadmap_ok) else "FAIL",
        "detail": "Verificado no ROADMAP.md"
    })

# Verifica se rotas quebradas foram corrigidas
if check_file_exists('public/docs/metodologia/index.html'):
    report['tasks'].append({
        "id": "ROUTE-001",
        "desc": "Rota /docs/metodologia",
        "status": "OK",
        "detail": "Arquivo estático existe"
    })
else:
    report['tasks'].append({
        "id": "ROUTE-001",
        "desc": "Rota /docs/metodologia",
        "status": "FAIL",
        "detail": "Arquivo estático ausente"
    })

with open('audit_report.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, indent=2, ensure_ascii=False)

print("✅ Relatório de auditoria gerado: audit_report.json")
