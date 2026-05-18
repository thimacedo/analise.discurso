import os, sys
from pathlib import Path
import re

root = Path('.').resolve()
files = list(root.rglob('*.py'))
count = 0

# O bloco robusto que queremos garantir
robust_block = """
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
"""

# Regex para encontrar versões antigas/parciais
old_block_pattern = re.compile(r"if hasattr\(sys\.stdout, ['\"]reconfigure['\"]\):\s+sys\.stdout\.reconfigure\(encoding=['\"]utf-8['\"]\)", re.MULTILINE)

for f in files:
    if any(p in str(f) for p in ['.venv', '.gemini', 'tests', '__pycache__', 'node_modules']):
        continue
    
    try:
        content = f.read_text(encoding='utf-8', errors='ignore')
        
        # Se já tem o robusto com errors='replace', pula
        if "encoding='utf-8', errors='replace'" in content and "sys.stderr.reconfigure" in content:
            continue
            
        # Se tem a versão antiga, substitui
        if old_block_pattern.search(content):
            new_content = old_block_pattern.sub(robust_block.strip(), content)
            f.write_text(new_content, encoding='utf-8')
            print(f"🔄 Atualizado: {f.relative_to(root)}")
            count += 1
            continue

        # Se não tem nada, insere no início (após shebang/docstring)
        lines = content.splitlines(keepends=True)
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.startswith('#!') or line.startswith('"""') or line.startswith("'''"):
                insert_pos = i + 1
                if line.strip().count('"""') == 1 or line.strip().count("'''") == 1:
                    for j in range(i + 1, len(lines)):
                        if '"""' in lines[j] or "'''" in lines[j]:
                            insert_pos = j + 1
                            break
                break
        
        lines.insert(insert_pos, robust_block)
        f.write_text(''.join(lines), encoding='utf-8')
        print(f"✅ Blindado: {f.relative_to(root)}")
        count += 1
        
    except Exception as e:
        print(f"❌ Erro em {f}: {e}")

print(f"\n🛡️ {count} scripts blindados/atualizados contra erros de encoding.")
