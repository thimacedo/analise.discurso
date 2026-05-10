# Sistema de Recompensas e Quality Gate de Workers (Worker Ledger)

Este sistema atua como uma camada de auditoria e garantia de qualidade (Quality Gate) para todos os dados coletados pelos workers do Sentinela Democrática.

## 🎯 Objetivos
- Garantir a integridade dos dados antes da persistência no Supabase.
- Atribuir pontuações (recompensas/penalidades) aos workers com base na qualidade da extração.
- Identificar proativamente falhas de stealth, shadowbans ou problemas de infraestrutura.

## ⚖️ Regras de Pontuação
O `WorkerValidator` avalia cada payload e aplica as seguintes pontuações:

| Cenário | Pontuação | Ação |
| :--- | :---: | :--- |
| **Extração Limpa** | +15 | Dado persistido no Supabase. |
| **Timeout / Erro de Stealth** | -10 | Dado descartado. |
| **Dados Inválidos / Nulos / Erros** | -20 | Dado descartado. Registro imediato no log. |

### Critérios de Invalidação:
- Conteúdo contendo strings de erro padrão (ex: `[Conteúdo do comentário não pôde ser recuperado]`).
- Payloads nulos ou vazios.
- Datas de coleta zeradas (`00:00:00`).

## 📊 Auditoria do Ledger
O estado atual das notas dos workers pode ser consultado no arquivo:
`metrics/performance_ledger.json`

### Estrutura do Arquivo:
- `workers`: Contém o score acumulado, total de tarefas, tarefas válidas e inválidas por worker.
- `history`: Um log cronológico das últimas 1000 avaliações, incluindo o motivo do descarte ou aceitação.

## 🛠️ Como Auditar
Para auditar o sistema manualmente:
1. Abra o arquivo `metrics/performance_ledger.json`.
2. Verifique o campo `score`. Workers com score negativo constante devem ser revisados (atualização de seletores ou rotação de proxies).
3. Verifique o `history` para entender os motivos frequentes de falha (`reason`).

## 🚀 Integração Técnica
O validador é instanciado pelo `Orchestrator` e injetado nos scrapers ativos. Nenhum dado deve chegar ao banco de dados sem passar pelo método `evaluate_payload()`.
