import os
import glob
from pathlib import Path

def generate_audit():
    root_dir = Path('.')
    output_file = root_dir / 'AUDITORIA_WORKSPACE.md'
    
    ignore_dirs = {'.git', 'node_modules', 'venv', '__pycache__', '.temp', '.supabase', 'visualizacoes', 'docs/superpowers', 'embed'}
    ignore_exts = {'.pyc', '.png', '.webp', '.jpg', '.pdf', '.xml', '.code-workspace', '.cjs', '.cpuprofile'}

    audit_data = []

    for filepath in root_dir.rglob('*'):
        if not filepath.is_file():
            continue
            
        parts = filepath.parts
        if any(ignored in parts for ignored in ignore_dirs):
            continue
            
        if filepath.suffix in ignore_exts:
            continue

        file_str = str(filepath).replace('\\', '/')
        
        # Heuristic Analysis
        status = "A Revisar"
        action = "Manter"
        desc = "Arquivo de sistema"

        if file_str.startswith('src/core/') or file_str == 'index.html' or file_str == 'local_dashboard.html':
            status = "Ativo (Core)"
            action = "Manter (Limpo PASA v47)"
            desc = "Frontend Vanilla JS e UI"
        elif file_str.startswith('workers/') or file_str == 'local_server.py' or file_str == 'watchdog.py':
            status = "Ativo (Daemon)"
            action = "Manter"
            desc = "Backend local, orquestração e scrapers"
        elif file_str.startswith('supabase/migrations/'):
            status = "Histórico"
            action = "Manter"
            desc = "Migração de Banco de Dados"
        elif file_str.startswith('tools/') or 'tmp_' in file_str or 'test_' in file_str:
            status = "Suspeito / Isolado"
            action = "Auditar/Deletar"
            desc = "Scripts avulsos, testes antigos ou ferramentas mortas"
        elif file_str.startswith('scripts/') and file_str.endswith('.py'):
            status = "Operacional / Cron"
            action = "Revisar Integração"
            desc = "Scripts utilitários ou de manutenção (ex: detect_shadowbans)"
        elif file_str.endswith('.md'):
            status = "Documentação"
            if file_str in ['ROADMAP.md', 'STATE.md', 'GEMINI.md', 'AUDITORIA_WORKSPACE.md']:
                action = "Manter (Essencial)"
            else:
                action = "Mesclar ou Deletar se obsoleto"
            desc = "Memória do projeto, skills ou logs de IA"

        audit_data.append(f"| `{file_str}` | {status} | {desc} | **{action}** |")

    # Sort alphabetically
    audit_data.sort()

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 🕵️‍♂️ GRANDE AUDITORIA DO WORKSPACE (PASA v47)\n\n")
        f.write("Esta é a listagem exaustiva de todos os arquivos rastreados no repositório, classificados por estado atual e ação recomendada para a purga final.\n\n")
        f.write("| Arquivo | Status | Propósito Inferido | Ação Recomendada |\n")
        f.write("|---------|--------|--------------------|------------------|\n")
        f.write("\n".join(audit_data))
        f.write("\n")

if __name__ == '__main__':
    generate_audit()
    print("Relatório gerado em AUDITORIA_WORKSPACE.md")
