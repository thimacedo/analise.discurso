import os

def fix_mcp_agent_definitions(file_paths):
    for file_path in file_paths:
        try:
            if not os.path.exists(file_path):
                continue
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            if not content.startswith("---"):
                extension_name = os.path.basename(os.path.dirname(os.path.dirname(file_path)))
                yaml_frontmatter = f"---\nname: {extension_name}\n---\n\n"
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(yaml_frontmatter + content)
                print(f"Frontmatter adicionado: {file_path}")
        except Exception as e:
            print(f"Falha em {file_path}: {e}")

target_files = [
    r'C:\Users\THIAGO\.gemini\extensions\apify-agent-skills\agents\AGENTS.md',
    r'C:\Users\THIAGO\.gemini\extensions\awesome-skills\agents\AGENTS.md'
]
fix_mcp_agent_definitions(target_files)
