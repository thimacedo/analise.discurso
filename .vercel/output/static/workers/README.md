# Arquitetura de Workers (Sentinela Democrática)

Este diretório contém a infraestrutura de processamento assíncrono e tarefas em background do Sentinela Democrática.

## 💎 Design Pattern: Protocolo Diamond
Esta arquitetura segue o princípio Open/Closed. Todos os workers devem estender a classe `BaseWorker` localizada em `core/base_worker.py`.

### Estrutura de Diretórios

- `core/`: Contém contratos (Interfaces/Abstract Base Classes) e utilitários globais (`common.py`). Modifique com cuidado, pois é o contrato principal.
- `scrapers/`: Workers dedicados EXCLUSIVAMENTE a extrair dados da web (Ex: Instagram, Meta Ads).
- `processors/`: Workers dedicados EXCLUSIVAMENTE a processamento (Ex: Análise PASA com LLMs, limpeza de dados).
- `main_orchestrator.py`: O cron/daemon principal responsável por instanciar os workers ou delegar tarefas e persistir estados no Git/Supabase.

### Como criar um novo Worker

1. Crie o arquivo no diretório apropriado (ex: `scrapers/tiktok_scraper.py`).
2. Importe e herde de `BaseWorker`.
3. Implemente o método `async def _run(self, *args, **kwargs)`.
4. (Opcional) Sobrescreva `def handle_failure(self, exception)`.

Exemplo:
```python
from workers.core.base_worker import BaseWorker

class MyNewWorker(BaseWorker):
    def __init__(self):
        super().__init__("MyNewWorker")
        
    async def _run(self, data):
        print(f"Processando {data}")
```
