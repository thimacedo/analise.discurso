import os
import sys
from datetime import datetime

# Adiciona a raiz do projeto ao path para importar o DossieService
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from processing.dossie_service import DossieService

import pytest

@pytest.mark.asyncio
async def test_generate_basic_dossie():
    # Mock de dados
    sample_data = [
        {
            "candidatos": {"username": "candidato_teste_1"},
            "texto_bruto": "Este é um comentário de teste com acentuação: Áéíóú ñ ç.",
            "is_hate": False,
            "categoria_ia": "Informativo"
        },
        {
            "candidatos": {"username": "candidato_teste_2"},
            "texto_bruto": "CONTEÚDO AGRESSIVO DETECTADO! script de repetição ativado.",
            "is_hate": True,
            "categoria_ia": "Agressividade"
        }
    ]
    
    output_dir = "E:\\projetos\\sentinela-democratica\\data\\reports"
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"test_dossie_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    path = os.path.join(output_dir, filename)
    
    service = DossieService()
    # Adicionado candidato_id que faltava e await pois agora é async
    result_path = await service.generate_dossie(sample_data, path, candidato_id="candidato_teste_1")
    
    assert result_path is not None
    assert os.path.exists(result_path)
    print(f"Teste concluído. PDF gerado em: {result_path}")

if __name__ == "__main__":
    test_generate_basic_dossie()
