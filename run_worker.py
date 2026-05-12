import subprocess
import sys
import os

# Define o diretório de trabalho como a raiz do projeto
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(project_root)

# Configura o encoding para UTF-8 para stdout e stderr
# Isso garante que caracteres especiais sejam tratados corretamente no Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

# Comando a ser executado (scripts/work_session.py)
# Usando -X utf8 para forçar o modo UTF-8 nativo do interpretador Python
command = "python -X utf8 scripts/work_session.py"

print(f"Executando comando: {command}")

try:
    # Executa o comando e redireciona stdout e stderr para um arquivo de log
    # O redirecionamento '2>&1' é feito implicitamente pelo subprocess.Popen com stderr=subprocess.STDOUT
    # e também explicitamente ao abrir o arquivo de log.
    with open("debug_session.log", "w", encoding="utf-8") as log_file:
        process = subprocess.Popen(
            command,
            shell=True, # Usar shell=True para permitir redirecionamento e outros recursos do shell
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, # Redireciona stderr para stdout
            text=True,
            encoding='utf-8',
            errors='replace',
            cwd=project_root # Garante que o comando seja executado na raiz do projeto
        )
        
        # Lê a saída em tempo real e a escreve no arquivo de log e no console
        for line in process.stdout:
            print(line, end='')
            log_file.write(line)
            log_file.flush() # Garante que a linha seja escrita imediatamente no arquivo

        process.wait() # Espera o processo terminar
        
        if process.returncode != 0:
            print(f"
!!! Comando falhou com código de saída: {process.returncode} !!!")
        else:
            print(f"
Comando executado com sucesso.")

except FileNotFoundError:
    print(f"
!!! Erro: Comando '{command.split()[0]}' não encontrado. Verifique se o Python está no PATH e o script existe. !!!")
except Exception as e:
    print(f"
!!! Erro inesperado ao executar o comando: {e} !!!")
