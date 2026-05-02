import re
import logging

def fix_agent_definition(filepath):
    """Corrige a definição do agente removendo chaves não reconhecidas do frontmatter YAML.

    Args:
        filepath (str): O caminho absoluto para o arquivo Markdown de configuração do agente.

    Returns:
        bool: True se o arquivo foi modificado e corrigido com sucesso, False caso contrário.

    Raises:
        Exception: Falhas de leitura, gravação ou permissão, que são capturadas e registradas em log.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()

        yaml_pattern = re.compile(r'^---\n(.*?)\n---', re.DOTALL | re.MULTILINE)
        match = yaml_pattern.search(content)

        if match:
            yaml_content = match.group(1)
            
            yaml_content = re.sub(r'^systemPrompt:.*\n?', '', yaml_content, flags=re.MULTILINE)
            yaml_content = re.sub(r'^initialMessages:(?:(?!\n\w).)*\n?', '', yaml_content, flags=re.DOTALL | re.MULTILINE)

            new_content = yaml_pattern.sub(f'---\n{yaml_content}\n---', content, count=1)

            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as file:
                    file.write(new_content)
                
        return True

    except Exception as e:
        logging.basicConfig(filename='error.log', level=logging.ERROR, 
                            format='%(asctime)s - %(levelname)s - %(message)s')
        logging.error(f"Erro ao processar o arquivo {filepath}: {e}")
        return False

if __name__ == "__main__":
    target_file = r'C:\Users\THIAGO\.gemini\extensions\gemini-kit\agents\frontend-specialist.md'
    fix_agent_definition(target_file)