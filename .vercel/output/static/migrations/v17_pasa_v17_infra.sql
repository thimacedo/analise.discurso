-- migrations/v17_pasa_v17_infra.sql
-- 1. Adiciona colunas de histórico ao worker_ledger (não destrói o que existe)
ALTER TABLE public.worker_ledger
  ADD COLUMN IF NOT EXISTS run_id uuid DEFAULT gen_random_uuid(),
  ADD COLUMN IF NOT EXISTS started_at timestamptz DEFAULT now(),
  ADD COLUMN IF NOT EXISTS finished_at timestamptz,
  ADD COLUMN IF NOT EXISTS duration_ms integer,
  ADD COLUMN IF NOT EXISTS items_processed integer DEFAULT 0,
  ADD COLUMN IF NOT EXISTS items_rejected integer DEFAULT 0,
  ADD COLUMN IF NOT EXISTS error_message text,
  ADD COLUMN IF NOT EXISTS payload_snapshot jsonb;

-- 2. Cria tabela de eventos imutável (append-only, nunca atualizada)
CREATE TABLE IF NOT EXISTS public.worker_runs (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  worker_name  text NOT NULL,
  started_at   timestamptz NOT NULL DEFAULT now(),
  finished_at  timestamptz,
  duration_ms  integer,
  status       text NOT NULL CHECK (status IN ('running','success','failure')),
  items_processed integer DEFAULT 0,
  items_rejected  integer DEFAULT 0,
  error_message   text,
  payload_snapshot jsonb,
  created_at   timestamptz NOT NULL DEFAULT now()
);

-- 3. Cria tabela pg_queue para o Event Bus (Simulação PGMQ)
CREATE TABLE IF NOT EXISTS public.pg_queue (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  queue_name   text NOT NULL,
  payload      jsonb NOT NULL,
  status       text NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'LOCKED', 'ACK')),
  locked_until timestamptz,
  last_error   text,
  finished_at  timestamptz,
  created_at   timestamptz NOT NULL DEFAULT now()
);

-- 4. View de saúde que o dashboard já espera consumir
CREATE OR REPLACE VIEW public.worker_health AS
SELECT
  worker_name,
  COUNT(*)                                          AS total_runs,
  COUNT(*) FILTER (WHERE status = 'success')        AS successes,
  COUNT(*) FILTER (WHERE status = 'failure')        AS failures,
  ROUND(
    COUNT(*) FILTER (WHERE status = 'success')::numeric
    / NULLIF(COUNT(*), 0) * 100, 1
  )                                                 AS success_rate_pct,
  ROUND(AVG(duration_ms) FILTER (WHERE status = 'success'))
                                                    AS avg_duration_ms,
  SUM(items_processed)                              AS total_items_processed,
  SUM(items_rejected)                               AS total_items_rejected,
  MAX(started_at)                                   AS last_run_at,
  -- últimos 3 erros distintos nas últimas 24h
  ARRAY(
    SELECT DISTINCT error_message
    FROM public.worker_runs r2
    WHERE r2.worker_name = r.worker_name
      AND r2.error_message IS NOT NULL
      AND r2.created_at > now() - interval '24 hours'
    LIMIT 3
  )                                                 AS recent_errors
FROM public.worker_runs r
WHERE created_at > now() - interval '24 hours'
GROUP BY worker_name;
