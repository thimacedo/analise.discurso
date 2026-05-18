
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import os

root_dir = r"C:\projetos\sentinela-democratica"
old_path = r"C:\projetos\sentinela-democratica"
new_path = r"C:\projetos\sentinela-democratica"

files_updated = 0

for root, dirs, files in os.walk(root_dir):
    for file in files:
        if file.endswith(".py"):
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if old_path in content:
                    new_content = content.replace(old_path, new_path)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"✅ Corrigido: {file_path}")
                    files_updated += 1
            except Exception as e:
                # Tentar com outra codificação se falhar
                try:
                    with open(file_path, 'r', encoding='latin-1') as f:
                        content = f.read()
                    if old_path in content:
                        new_content = content.replace(old_path, new_path)
                        with open(file_path, 'w', encoding='latin-1') as f:
                            f.write(new_content)
                        print(f"✅ Corrigido (latin-1): {file_path}")
                        files_updated += 1
                except:
                    print(f"❌ Erro ao processar {file_path}: {e}")

print(f"\n✨ Limpeza concluída! {files_updated} arquivos purificados.")
