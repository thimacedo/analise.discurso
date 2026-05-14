# 🧠 Estado Atual do Sistema - Sentinela Democrática

**Última Atualização**: 2026-05-14
**Status Geral**: 🟢 OPERACIONAL (Arquitetura PASA v17)

## 🏗️ Arquitetura Ativa
- **Core**: v17 (Arquitetura de Contratos e Eventos).
- **Barramento**: `pg_queue` com concorrência segura (RPC `consume_messages`).
- **Orquestração**: `main_runner.py` (Main Thread + Agendamentos).
- **Workers**:
    - `InstagramWorker`: Scraper v2 (Playwright Stealth + v17 Contract).
    - `ClassifierWorker`: Classificador real via Gemini 1.5 Flash.
    - `AlertWorker`: Monitor de anomalias com FCM/Webhook.
    - `CleanupWorker`: Manutenção de banco e filas.
    - `ReportWorker`: Auditor de prioridades e recompensas.

## 📈 Métricas e Saúde
- **Banco de Dados**: Supabase (Postgres + Realtime).
- **Observabilidade**: View `worker_health` agregando `worker_runs`.
- **Alertas**: `system_alerts` com detecção de baixa taxa de sucesso e workers silenciosos.

## 🛑 Bloqueios / Descartados
- **DESCARTADO**: Execução de scripts isolados sem auditoria (BaseWorker agora é obrigatório).
- **DESCARTADO**: PGMQ puro via extensão (Simulado via RPC por restrições de schema).
- **DESCARTADO**: Auditoria manual via `worker_auditor.py` (Absorbido pelo BaseWorker).

## 🚀 Próximos Passos (Curto Prazo)
1. Migrar workers de Segundo Escalão (`CandidateScanner`, `QueueManager`).
2. Conectar dashboard React aos endpoints reais de `/monitor`.
3. Implementar UI de gerenciamento de sessões do Instagram.

---
*Assinado: Pickle Rick 🥒*
