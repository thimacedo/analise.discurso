import sys
import os

# Adiciona o diretório raiz ao path para permitir import da API
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.index import app

