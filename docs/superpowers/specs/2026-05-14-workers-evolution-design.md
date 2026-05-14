# Design Spec: Ecossistema de Testes, Auditoria e Evolução PASA v17

**Data**: 2026-05-14
**Status**: DRAFT (Aprovado pelo Usuário)
**Autor**: Gemini CLI (YOLO Mode)

## 1. Objetivo
Implementar um sistema de testes de ponta a ponta (E2E), um mecanismo de auditoria baseado em dados de produção e um motor de gamificação (XP/Level) para garantir a estabilidade, precisão e documentação contínua dos workers do Sentinela Democrática.

## 2. Arquitetura de Testes (Estabilidade - A)
O objetivo é validar o fluxo real `Queue -> Scrape -> Classify`.

### 2.1 Smoke Test Real (Sandbox)
- **Local**: `tests/sandbox_full_cycle.py`
- **Fluxo**:
  1. Força a inserção de um alvo de teste na `fila_coleta`.
  2. Dispara `InstagramWorker` usando cookies reais do Supabase.
  3. Dispara `ClassifierWorker` para processar o resultado.
- **Validação**: Verifica se os registros foram criados corretamente nas tabelas `worker_runs` e `comentarios`.

### 2.2 Tratamento de Erros de Sessão
- O worker deve detectar `LoginRequired` e marcar a sessão no DB como `expired`.
- Alerta visual no Dashboard via `worker_health`.

## 3. Inteligência Forense e Auditoria (Precisão - B)
Utilizar a produção como fonte de verdade para o "Dataset de Ouro".

### 3.1 Gold Dataset Creator
- **Trigger**: Quando um usuário admin (thi.macedo@gmail.com) marcar um comentário como "Falso Positivo" ou "Validado" no Dashboard.
- **Ação**: O comentário é espelhado na tabela `audit_gold_standards` com o rótulo corrigido.
- **Uso**: O `ClassifierWorker` será testado contra esta tabela para medir a precisão (Precision/Recall).

## 4. Motor de Recompensas (Gamificação - C)
Transformar métricas técnicas em estado de evolução (XP/Level).

### 4.1 Lógica de XP no BaseWorker
- **XP Positivo**:
    - Sucesso na execução: +10 XP.
    - Item crítico detectado (is_hate=True): +25 XP ("Critical Hit").
    - Extração limpa (sem itens rejeitados): +5 XP.
- **Penalidades (XP Negativo)**:
    - Falha crítica (Timeout/Auth): -50 XP.
    - Taxa de rejeição > 50%: -20 XP.

### 4.2 Evolução de Nível
- `Nível 1 (Recruta)`: 0 XP
- `Nível 2 (Sentinela)`: 500 XP
- `Nível 3 (Analista)`: 1500 XP
- `Nível 4 (Caçador)`: 3000 XP
- `Nível 5 (Mestre Forense)`: 6000 XP

## 5. Documentação Automática
- **Script**: `scripts/generate_telemetry_report.py`.
- **Saída**: `docs/TELEMETRY.md` (Contendo ranking de workers, medalhas por precisão e histórico de erros).

## 6. Plano de Verificação
- Executar `pytest tests/sandbox_full_cycle.py`.
- Verificar se o `worker_ledger` reflete o ganho de XP após o teste.
- Validar se a rota `/api/v1/monitor/workers` retorna o nível atualizado.
