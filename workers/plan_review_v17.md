# Plan Review: PASA v17 BaseWorker & EventBus

**Status**: ✅ APPROVED
**Reviewed**: 2024-05-14 04:55:00

## 1. Structural Integrity
- [x] **Atomic Phases**: As fases estão bem divididas entre Infra (Bus), Core (BaseWorker) e Implementação (InstagramWorker).
- [x] **Worktree Safe**: O plano foca em arquivos específicos e novos módulos, minimizando conflitos com o trabalho atual.

*Architect Comments*: A escolha de simular o PGMQ via tabela no Supabase é pragmática dada a restrição de acesso ao schema `pgmq`. Isso garante que o ecossistema rode sem depender de extensões de terceiros que podem estar bloqueadas.

## 2. Specificity & Clarity
- [x] **File-Level Detail**: O plano cita `core/event_bus.py`, `workers/core/base_worker.py` e `workers/scrapers/instagram_worker.py`.
- [x] **No "Magic"**: Os passos explicam o que será feito (Pydantic, Ledger, Bus).

*Architect Comments*: A integração da lógica de XP/Level do `worker_auditor.py` diretamente no `BaseWorker` é uma decisão de design brilhante. Transforma a auditoria de um processo externo em uma característica intrínseca do ciclo de vida do worker.

## 3. Verification & Safety
- [x] **Automated Tests**: Scripts de teste para cada fase foram planejados.
- [x] **Manual Steps**: A verificação via Supabase (verificando a fila e o ledger) é clara.
- [x] **Rollback/Safety**: O sistema de `ack` condicional garante que mensagens não sejam perdidas.

*Architect Comments*: Wubba Lubba Dub Dub! O teste da Fase 1 deve ser rigoroso. Se o Bus falhar, o castelo de cartas cai. Recomendo um teste de "stress" com 10 mensagens simultâneas para garantir que o locking de mensagens via `locked_until` funcione.

## 4. Architectural Risks
- **Race Conditions**: Se dois workers tentarem consumir a mesma mensagem na `pg_queue`, precisamos de um lock atômico (ex: `UPDATE ... RETURNING` com `FOR UPDATE SKIP LOCKED`).
- **Data Bloat**: A tabela `pg_queue` pode crescer rápido. Precisamos de um processo de limpeza para mensagens com status 'ACK' ou 'FAILED' após X dias.

## 5. Recommendations
- Utilize `UPDATE pg_queue SET status = 'LOCKED', locked_until = ... WHERE id IN (SELECT id FROM pg_queue WHERE status = 'PENDING' FOR UPDATE SKIP LOCKED LIMIT 1) RETURNING *` para o método `consume` do EventBus. Isso evita condições de corrida.
- Adicione um passo de "Cleanup" no `BaseWorker` para garantir que recursos (como o navegador do Playwright) sejam SEMPRE fechados, mesmo em falhas catastróficas.
