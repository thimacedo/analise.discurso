# PASA v17 Implementation Plan - BaseWorker & EventBus

## Overview
Refatoração do núcleo dos workers para adotar o padrão de Contratos (Pydantic) e Mensageria (Event Bus). Isso transforma scripts isolados em um ecossistema resiliente e auditável.

## Scope Definition
### In Scope
- Criação do `core/event_bus.py` (Simulação de PGMQ via tabela Supabase).
- Refatoração do `workers/core/base_worker.py` para incluir o Ledger e tratamento de filas.
- Atualização do `InstagramWorker` para herdar o novo comportamento.
### Out of Scope
- Migração de todos os outros workers (serão feitos em tickets subsequentes).
- Implementação de um broker de mensagens real (RabbitMQ/Redis).

## Current State Analysis
- `BaseWorker`: Apenas loga início/fim, sem persistência de estado ou tratamento de filas.
- `worker_ledger`: Usado apenas pelo `worker_auditor.py`, não é atualizado automaticamente pelo ciclo de vida do worker.
- `InstagramWorker`: Chama `save_comments` diretamente, sem passar por uma fila de classificação posterior.

## Implementation Phases

### Phase 1: Event Bus Foundation
- **Goal**: Criar o mecanismo de mensageria assíncrona.
- **Steps**:
  1. [ ] Criar a tabela `pg_queue` no Supabase (id, queue_name, payload, status, created_at, locked_until).
  2. [ ] Implementar `core/event_bus.py` com métodos `publish`, `consume` e `ack`.
- **Verification**: Script de teste disparando e lendo mensagens da fila `test_queue`.

### Phase 2: BaseWorker Pro Refactor
- **Goal**: Tornar o BaseWorker o cérebro da operação com suporte a Auditoria e Filas.
- **Steps**:
  1. [ ] Atualizar `workers/core/base_worker.py` com integração ao `EventBus`.
  2. [ ] Implementar registro automático no `worker_ledger` para Sucesso/Falha.
  3. [ ] Adicionar cálculo de XP e Level direto no ciclo de vida (integrando lógica do `worker_auditor.py`).
- **Verification**: Executar um worker dummy e verificar inserção no `worker_ledger` e na `pg_queue`.

### Phase 3: InstagramWorker Migration
- **Goal**: Adaptar o scraper principal para o novo fluxo.
- **Steps**:
  1. [ ] Atualizar `InstagramWorker` para usar o novo `BaseWorker`.
  2. [ ] Em vez de apenas salvar, publicar evento `classify_comments` após a extração validada.
- **Verification**: Executar `InstagramWorker` e verificar se os comentários chegam ao banco E uma mensagem é gerada na fila de classificação.

## Review Criteria
- O `ack` da mensagem só deve ocorrer em caso de sucesso absoluto.
- O `worker_ledger` deve refletir a duração real de cada execução.
- O Pydantic deve barrar ruídos antes de qualquer publicação no Bus.
