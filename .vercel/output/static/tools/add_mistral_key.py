import os, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
config_path = ROOT / 'core' / 'config.py'

with open(config_path, 'r', encoding='utf-8') as f:
    content = f.read()

if 'MISTRAL_API_KEY' not in content:
    lines = content.splitlines(keepends=True)
    insert_pos = -1
    for i, line in enumerate(lines):
        if line.strip().startswith('GROQ_API_KEY'):
            insert_pos = i + 1
            break
    if insert_pos == -1:
        for i, line in enumerate(lines):
            if line.strip().startswith('IA_PROVIDER'):
                insert_pos = i + 1
                break
    if insert_pos != -1:
        lines.insert(insert_pos, '''    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")
''')
        with open(config_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print("✅ MISTRAL_API_KEY adicionada ao config.py")
    else:
        print("❌ Não encontrei onde inserir. Adicione manualmente a linha abaixo em core/config.py:")
        print('    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")')
else:
    print("ℹ️ MISTRAL_API_KEY já existe no config.py")
